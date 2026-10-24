from typing import List, Tuple, Dict, Any
import numpy as np
import torch
from .phylogenetic_embedding import train_phylogenetic_embedding
from .dna_encoder import train_dna_encoder, encode_sequence
from .cooccurrence_correction import train_cooccurrence_correction, soft_nearest_neighbor_kernel

class eDNAPipeline:
    """
    Complete eDNA taxonomy pipeline:
    1. Phylogenetic embedding
    2. DNA encoder
    3. Co-occurrence correction
    """
    def __init__(
        self,
        num_species: int,
        embedding_dim: int = 64,
        seq_length: int = 200,
        hidden_dim: int = 2048,
        cooccurrence_hidden_dim: int = 256
    ):
        self.num_species = num_species
        self.embedding_dim = embedding_dim
        self.seq_length = seq_length
        self.hidden_dim = hidden_dim
        self.cooccurrence_hidden_dim = cooccurrence_hidden_dim
        
        self.species_embeddings = None
        self.dna_encoder = None
        self.cooccurrence_model = None
    
    def train_stage1(
        self,
        tree_distance: np.ndarray,
        epochs: int = 100,
        learning_rate: float = 0.01,
        batch_size: int = 64
    ) -> np.ndarray:
        """
        Stage 1: Train phylogenetic embedding
        """
        print("Training Stage 1: Phylogenetic embedding...")
        model, embeddings = train_phylogenetic_embedding(
            tree_distance=tree_distance,
            num_species=self.num_species,
            embedding_dim=self.embedding_dim,
            epochs=epochs,
            learning_rate=learning_rate,
            batch_size=batch_size
        )
        self.species_embeddings = embeddings
        return embeddings
    
    def train_stage2(
        self,
        sequences: List[str],
        species_labels: List[int],
        epochs: int = 50,
        learning_rate: float = 1e-3,
        batch_size: int = 16
    ) -> Tuple[Any, np.ndarray]:
        """
        Stage 2: Train DNA encoder
        """
        print("Training Stage 2: DNA encoder...")
        if self.species_embeddings is None:
            raise ValueError("Stage 1 must be trained first")
        
        model, embeddings = train_dna_encoder(
            sequences=sequences,
            species_embeddings=self.species_embeddings,
            species_labels=species_labels,
            seq_length=self.seq_length,
            embedding_dim=self.embedding_dim,
            hidden_dim=self.hidden_dim,
            epochs=epochs,
            learning_rate=learning_rate,
            batch_size=batch_size
        )
        self.dna_encoder = model
        return model, embeddings
    
    def train_stage3(
        self,
        sequence_embeddings: np.ndarray,
        cooccurrence_data: List[List[int]],
        epochs: int = 50,
        learning_rate: float = 1e-3,
        temperature: float = 0.05
    ) -> Tuple[Any, np.ndarray]:
        """
        Stage 3: Train co-occurrence correction
        """
        print("Training Stage 3: Co-occurrence correction...")
        if self.species_embeddings is None:
            raise ValueError("Stage 1 must be trained first")
        
        model, probabilities = train_cooccurrence_correction(
            sequence_embeddings=sequence_embeddings,
            species_embeddings=self.species_embeddings,
            cooccurrence_data=cooccurrence_data,
            num_species=self.num_species,
            hidden_dim=self.cooccurrence_hidden_dim,
            epochs=epochs,
            learning_rate=learning_rate,
            temperature=temperature
        )
        self.cooccurrence_model = model
        return model, probabilities
    
    def predict(
        self,
        sequences: List[str],
        use_cooccurrence: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Predict species for new sequences.
        
        Args:
            sequences: List of DNA sequences to classify
            use_cooccurrence: Whether to apply co-occurrence correction
        
        Returns:
            List of predictions with species, confidence, etc.
        """
        if self.dna_encoder is None:
            raise ValueError("Stage 2 must be trained first")
        
        # Encode sequences
        encoded_seqs = [encode_sequence(seq, self.seq_length) for seq in sequences]
        seq_tensor = torch.tensor(encoded_seqs, dtype=torch.long)
        
        # Get embeddings
        self.dna_encoder.eval()
        with torch.no_grad():
            seq_embeddings = self.dna_encoder(seq_tensor)
        
        # Convert to species probabilities
        species_emb_tensor = torch.tensor(self.species_embeddings, dtype=torch.float32)
        p = soft_nearest_neighbor_kernel(seq_embeddings, species_emb_tensor, temperature=0.05)
        
        # Apply co-occurrence if requested
        if use_cooccurrence and self.cooccurrence_model is not None:
            p = self.cooccurrence_model(p)
        
        # Convert to predictions
        predictions = []
        probs = p.cpu().numpy()
        
        for i, prob in enumerate(probs):
            top_species = np.argmax(prob)
            confidence = prob[top_species]
            
            predictions.append({
                "sequence_index": i,
                "predicted_species": top_species,
                "confidence": float(confidence),
                "all_probabilities": prob.tolist()
            })
        
        return predictions
    
    def save_models(self, path: str):
        """Save all trained models"""
        import torch
        import pickle
        
        checkpoint = {
            "species_embeddings": self.species_embeddings,
            "dna_encoder_state": self.dna_encoder.state_dict() if self.dna_encoder else None,
            "cooccurrence_state": self.cooccurrence_model.state_dict() if self.cooccurrence_model else None,
            "config": {
                "num_species": self.num_species,
                "embedding_dim": self.embedding_dim,
                "seq_length": self.seq_length,
                "hidden_dim": self.hidden_dim,
                "cooccurrence_hidden_dim": self.cooccurrence_hidden_dim,
            }
        }
        
        torch.save(checkpoint, path)
        print(f"Models saved to {path}")
    
    def load_models(self, path: str):
        """Load trained models"""
        import torch
        
        checkpoint = torch.load(path)
        
        self.species_embeddings = checkpoint["species_embeddings"]
        self.num_species = checkpoint["config"]["num_species"]
        self.embedding_dim = checkpoint["config"]["embedding_dim"]
        self.seq_length = checkpoint["config"]["seq_length"]
        self.hidden_dim = checkpoint["config"]["hidden_dim"]
        self.cooccurrence_hidden_dim = checkpoint["config"]["cooccurrence_hidden_dim"]
        
        if checkpoint["dna_encoder_state"]:
            from dna_encoder import DNAEncoder
            self.dna_encoder = DNAEncoder(self.seq_length, self.embedding_dim, self.hidden_dim)
            self.dna_encoder.load_state_dict(checkpoint["dna_encoder_state"])
        
        if checkpoint["cooccurrence_state"]:
            from cooccurrence_correction import CooccurrenceCorrection
            self.cooccurrence_model = CooccurrenceCorrection(self.num_species, self.cooccurrence_hidden_dim)
            self.cooccurrence_model.load_state_dict(checkpoint["cooccurrence_state"])
        
        print(f"Models loaded from {path}")
