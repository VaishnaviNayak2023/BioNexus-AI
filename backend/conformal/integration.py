"""
Integration wrapper for conformal prediction with the existing eDNA pipeline.

Connects the conformal prediction framework with the DNA encoder, phylogenetic
embedding, and co-occurrence correction models.
"""
import numpy as np
from typing import Optional, Dict, Tuple
import torch

from ml.pipeline import eDNAPipeline
from .calibration import leave_species_out_calibration, conformal_quantile
from .scores import combined_score
from .prediction_sets import clade_sets
from .evaluation import empirical_coverage, mean_set_size


class ConformalWrapper:
    """
    Wrapper that integrates conformal prediction with the eDNA pipeline.
    """
    
    def __init__(
        self,
        pipeline: eDNAPipeline,
        num_species: int,
        embedding_dim: int = 64,
        radii: Tuple[int, ...] = (0, 1, 2, 3, 4),
        K: int = 5,
        alpha: float = 0.1
    ):
        """
        Initialize conformal wrapper.
        
        Args:
            pipeline: Trained eDNA pipeline
            num_species: Total number of species
            embedding_dim: Embedding dimension
            radii: Tree radii for clade levels
            K: Number of folds for LOSO calibration
            alpha: Target miscoverage level
        """
        self.pipeline = pipeline
        self.num_species = num_species
        self.embedding_dim = embedding_dim
        self.radii = radii
        self.K = K
        self.alpha = alpha
        
        # Calibration threshold (computed during calibration)
        self.q_flat = None
        self.q_clade = None
    
    def calibrate(
        self,
        X_cal: np.ndarray,
        y_cal: np.ndarray,
        sequence_embeddings: np.ndarray,
        species_embeddings: np.ndarray,
        tree_distance: np.ndarray
    ):
        """
        Calibrate the conformal predictor using LOSO.
        
        Args:
            X_cal: Calibration sequence features
            y_cal: Calibration species labels
            sequence_embeddings: Sequence embeddings
            species_embeddings: Species embeddings
            tree_distance: Tree distance matrix
        """
        # Create a simple model wrapper for the pipeline
        model_wrapper = PipelineModelWrapper(self.pipeline)
        
        # Compute calibration scores using combined score
        def score_fn(P, y):
            return combined_score(
                P, y, sequence_embeddings, species_embeddings, tree_distance, self.radii
            )
        
        # For calibration, we'll use a simplified approach
        # In practice, this would use full LOSO
        cal_scores = score_fn(
            model_wrapper.predict_proba(X_cal),
            y_cal
        )
        
        # Compute quantiles
        self.q_flat = conformal_quantile(cal_scores, self.alpha)
        self.q_clade = conformal_quantile(cal_scores, self.alpha)
        
        print(f"Calibration complete. q_flat={self.q_flat:.3f}, q_clade={self.q_clade:.3f}")
    
    def predict_sets(
        self,
        X_test: np.ndarray,
        sequence_embeddings: np.ndarray,
        species_embeddings: np.ndarray,
        tree_distance: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict conformal sets for new sequences.
        
        Args:
            X_test: Test sequence features
            sequence_embeddings: Test sequence embeddings
            species_embeddings: Species embeddings
            tree_distance: Tree distance matrix
        
        Returns:
            mask_flat: Flat set membership mask
            mask_clade: Clade set membership mask
        """
        if self.q_flat is None or self.q_clade is None:
            raise ValueError("Must call calibrate() before predict_sets()")
        
        # Get probabilities from pipeline
        model_wrapper = PipelineModelWrapper(self.pipeline)
        P_test = model_wrapper.predict_proba(X_test)
        
        # Flat sets
        mask_flat = (1.0 - P_test) <= self.q_flat
        mask_flat[np.arange(len(P_test)), P_test.argmax(axis=1)] = True
        
        # Clade sets
        mask_clade, _ = clade_sets(P_test, tree_distance, self.radii, self.q_clade)
        
        return mask_flat, mask_clade
    
    def evaluate(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray,
        sequence_embeddings: np.ndarray,
        species_embeddings: np.ndarray,
        tree_distance: np.ndarray
    ) -> Dict:
        """
        Evaluate the conformal predictor.
        
        Args:
            X_test: Test sequence features
            y_test: True species labels
            sequence_embeddings: Test sequence embeddings
            species_embeddings: Species embeddings
            tree_distance: Tree distance matrix
        
        Returns:
            Dictionary of evaluation metrics
        """
        mask_flat, mask_clade = self.predict_sets(
            X_test, sequence_embeddings, species_embeddings, tree_distance
        )
        
        return {
            "flat": {
                "coverage": empirical_coverage(mask_flat, y_test),
                "mean_set_size": mean_set_size(mask_flat)
            },
            "clade": {
                "coverage": empirical_coverage(mask_clade, y_test),
                "mean_set_size": mean_set_size(mask_clade)
            }
        }


class PipelineModelWrapper:
    """
    Wrapper to make the eDNA pipeline compatible with the conformal framework.
    """
    
    def __init__(self, pipeline: eDNAPipeline):
        self.pipeline = pipeline
    
    def fit(self, X, y):
        """Train the pipeline (no-op if already trained)."""
        # The pipeline is assumed to be pre-trained
        pass
    
    def predict_proba(self, X):
        """
        Get species probabilities from the pipeline.
        
        Args:
            X: Sequence features or embeddings
        
        Returns:
            Probability matrix (n_samples, n_species)
        """
        # If X are already embeddings, use them directly
        # Otherwise, need to encode sequences first
        if isinstance(X, torch.Tensor):
            X = X.cpu().numpy()
        
        # For now, assume X are embeddings
        # In practice, this would call the DNA encoder first
        if self.pipeline.dna_encoder is not None:
            # Encode sequences
            from ml.dna_encoder import encode_sequence
            seq_length = self.pipeline.seq_length
            encoded = np.array([encode_sequence(str(seq), seq_length) for seq in X])
            embeddings = self.pipeline.dna_encoder.predict(encoded)
        else:
            embeddings = X
        
        # Convert to species probabilities using soft nearest neighbor
        from ml.cooccurrence_correction import soft_nearest_neighbor_kernel
        species_emb = torch.tensor(self.pipeline.species_embeddings, dtype=torch.float32)
        seq_emb = torch.tensor(embeddings, dtype=torch.float32)
        P = soft_nearest_neighbor_kernel(seq_emb, species_emb, temperature=0.05)
        
        return P.cpu().numpy()
