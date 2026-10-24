import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from typing import List, Tuple
import numpy as np

class CooccurrenceCorrection(nn.Module):
    """
    Stage 3: Co-occurrence correction
    Adjust predictions using co-occurrence patterns from other species in the same sample.
    
    Uses two learned matrices U and V (size: num_species x 256) to model
    species co-occurrence patterns.
    """
    def __init__(self, num_species: int, hidden_dim: int = 256):
        super().__init__()
        self.num_species = num_species
        self.hidden_dim = hidden_dim
        
        # Learnable matrices for co-occurrence
        self.U = nn.Parameter(torch.randn(num_species, hidden_dim))
        self.V = nn.Parameter(torch.randn(num_species, hidden_dim))
    
    def forward(self, p: torch.Tensor) -> torch.Tensor:
        """
        Apply co-occurrence correction to species probabilities.
        
        Args:
            p: (M, n_species) tensor of species probabilities per sequence at one site
               M = number of sequences in the sample
        
        Returns:
            (M, n_species) tensor of corrected probabilities
        """
        M, n_species = p.shape
        
        # Compute average probability of each species across all other sequences
        # others = (p.sum(0, keepdim=True) - p) / (M - 1)
        others = (p.sum(dim=0, keepdim=True) - p) / (M - 1)
        
        # Apply co-occurrence correction
        # p_co = softmax(log(p) + others @ V @ U.T)
        cooccurrence_effect = others @ self.V @ self.U.T
        log_p = torch.log(p + 1e-10)  # Add small epsilon to avoid log(0)
        corrected = torch.softmax(log_p + cooccurrence_effect, dim=-1)
        
        return corrected

def soft_nearest_neighbor_kernel(
    embeddings: torch.Tensor,
    species_embeddings: torch.Tensor,
    temperature: float = 0.05
) -> torch.Tensor:
    """
    Convert embedding distances into species probabilities using soft nearest-neighbor kernel.
    
    Args:
        embeddings: (M, embedding_dim) sequence embeddings
        species_embeddings: (n_species, embedding_dim) species embeddings
        temperature: Temperature parameter for softmax
    
    Returns:
        (M, n_species) tensor of species probabilities
    """
    # Compute cosine similarity
    similarity = F.cosine_similarity(
        embeddings.unsqueeze(1),  # (M, 1, embedding_dim)
        species_embeddings.unsqueeze(0),  # (1, n_species, embedding_dim)
        dim=-1
    )  # (M, n_species)
    
    # Apply temperature and softmax
    probabilities = F.softmax(similarity / temperature, dim=-1)
    
    return probabilities

def train_cooccurrence_correction(
    sequence_embeddings: np.ndarray,
    species_embeddings: np.ndarray,
    cooccurrence_data: List[List[int]],  # List of species lists for each site
    num_species: int,
    hidden_dim: int = 256,
    epochs: int = 50,
    learning_rate: float = 1e-3,
    temperature: float = 0.05
) -> Tuple[CooccurrenceCorrection, np.ndarray]:
    """
    Train the co-occurrence correction model.
    
    Args:
        sequence_embeddings: Embeddings of sequences from all sites
        species_embeddings: Pre-trained species embeddings
        cooccurrence_data: List of species lists for each site (training data)
        num_species: Total number of species
        hidden_dim: Hidden dimension for U and V matrices
        epochs: Number of training epochs
        learning_rate: Learning rate for optimizer
        temperature: Temperature for soft nearest-neighbor kernel
    
    Returns:
        Trained model and corrected probabilities
    """
    model = CooccurrenceCorrection(num_species, hidden_dim)
    optimizer = optim.AdamW(model.parameters(), lr=learning_rate)
    
    species_emb_tensor = torch.tensor(species_embeddings, dtype=torch.float32)
    seq_emb_tensor = torch.tensor(sequence_embeddings, dtype=torch.float32)
    
    # Prepare training data
    # For each site, get the true species present
    num_sites = len(cooccurrence_data)
    
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        
        for site_idx in range(num_sites):
            # Get sequences for this site (simplified - in practice, group by site)
            # For now, use a random subset
            site_sequences = seq_emb_tensor[site_idx * 10:(site_idx + 1) * 10]
            if len(site_sequences) == 0:
                continue
            
            M = len(site_sequences)
            
            optimizer.zero_grad()
            
            # Convert to species probabilities
            p = soft_nearest_neighbor_kernel(site_sequences, species_emb_tensor, temperature)
            
            # Apply co-occurrence correction
            p_co = model(p)
            
            # Compute loss: negative log likelihood
            # true_idx: for each sequence, the true species index
            # This is simplified - in practice, you need ground truth labels
            true_species = cooccurrence_data[site_idx]
            if len(true_species) == 0:
                continue
            
            # For simplicity, assume first sequence corresponds to first species, etc.
            true_indices = torch.tensor([min(s, num_species - 1) for s in true_species[:M]], dtype=torch.long)
            
            loss = -torch.log(p_co[range(len(true_indices)), true_indices] + 1e-10).mean()
            
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch + 1}/{epochs}, Loss: {epoch_loss / num_sites:.4f}")
    
    # Generate final corrected probabilities
    model.eval()
    with torch.no_grad():
        p = soft_nearest_neighbor_kernel(seq_emb_tensor, species_emb_tensor, temperature)
        p_co = model(p)
        final_probabilities = p_co.cpu().numpy()
    
    return model, final_probabilities
