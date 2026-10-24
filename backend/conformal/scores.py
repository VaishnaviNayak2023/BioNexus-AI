"""
Nonconformity scores for conformal prediction in zero-shot eDNA assignment.

Implements four score functions from the research plan:
1. Probability score: one minus the model probability of the true species
2. Embedding-distance score: cosine distance between sequence and species embeddings
3. Tree-aware score: phylogenetic distance from predicted mass to true species
4. Combined score: weighted combination of embedding distance and tree-aware score
"""
import numpy as np
from typing import Tuple, Optional


def probability_score(P: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Score 1: Probability score.
    
    Standard baseline: one minus the model probability of the true species.
    Large when the model finds the true species implausible.
    
    Args:
        P: Probability matrix (n_samples, n_species)
        y: True species labels (n_samples,)
    
    Returns:
        Score array (n_samples,)
    """
    return 1.0 - P[np.arange(len(y)), y]


def embedding_distance_score(
    P: np.ndarray,
    y: np.ndarray,
    sequence_embeddings: np.ndarray,
    species_embeddings: np.ndarray
) -> np.ndarray:
    """
    Score 2: Embedding-distance score.
    
    Cosine distance between the sequence embedding and the true species embedding.
    
    Args:
        P: Probability matrix (n_samples, n_species)
        y: True species labels (n_samples,)
        sequence_embeddings: Sequence embeddings (n_samples, embedding_dim)
        species_embeddings: Species embeddings (n_species, embedding_dim)
    
    Returns:
        Score array (n_samples,)
    """
    # Normalize embeddings
    seq_norm = sequence_embeddings / (np.linalg.norm(sequence_embeddings, axis=1, keepdims=True) + 1e-12)
    sp_norm = species_embeddings / (np.linalg.norm(species_embeddings, axis=1, keepdims=True) + 1e-12)
    
    # Get embeddings for true species
    true_sp_emb = sp_norm[y]
    
    # Compute cosine distance
    cosine_sim = np.sum(seq_norm * true_sp_emb, axis=1)
    score = 1.0 - cosine_sim
    
    return score


def tree_aware_score(
    P: np.ndarray,
    y: np.ndarray,
    tree_distance: np.ndarray,
    radii: Tuple[int, ...] = (0, 1, 2, 3, 4)
) -> np.ndarray:
    """
    Score 3: Tree-aware score.
    
    Phylogenetic distance from the predicted mass to the true species,
    aggregating probability over clades.
    
    Args:
        P: Probability matrix (n_samples, n_species)
        y: True species labels (n_samples,)
        tree_distance: Tree distance matrix (n_species, n_species)
        radii: Tree radii for clade levels (e.g., 0=species, 1=genus, 2=family, 3=order)
    
    Returns:
        Score array (n_samples,)
    """
    n_samples, n_species = P.shape
    top1 = P.argmax(axis=1)
    
    # Compute mass inside each clade level around top-1 prediction
    scores = np.zeros(n_samples)
    
    for i in range(n_samples):
        top_sp = top1[i]
        true_sp = y[i]
        
        # Find the tree distance from top-1 to true species
        d_true = tree_distance[top_sp, true_sp]
        
        # Find the smallest clade level that contains the true species
        # Score is the probability mass just below that level
        for level_idx, radius in enumerate(radii):
            if d_true <= radius:
                # This level contains the true species
                # Score is mass in the level below
                if level_idx > 0:
                    prev_radius = radii[level_idx - 1]
                    in_clade = tree_distance[top_sp] <= prev_radius
                    mass = (P[i] * in_clade).sum()
                    scores[i] = 1.0 - mass  # Higher when mass below containing level is low
                else:
                    # True species is the top-1 prediction
                    scores[i] = 1.0 - P[i, top_sp]
                break
        else:
            # True species is outside all defined clades
            scores[i] = 1.0
    
    return scores


def combined_score(
    P: np.ndarray,
    y: np.ndarray,
    sequence_embeddings: np.ndarray,
    species_embeddings: np.ndarray,
    tree_distance: np.ndarray,
    radii: Tuple[int, ...] = (0, 1, 2, 3, 4),
    weights: Optional[dict] = None
) -> np.ndarray:
    """
    Score 4: Combined score.
    
    Weighted combination of embedding distance and tree-aware score with
    the co-occurrence-adjusted probability.
    
    Args:
        P: Probability matrix (n_samples, n_species)
        y: True species labels (n_samples,)
        sequence_embeddings: Sequence embeddings
        species_embeddings: Species embeddings
        tree_distance: Tree distance matrix
        radii: Tree radii for clade levels
        weights: Dictionary of weights for each component
    
    Returns:
        Score array (n_samples,)
    """
    if weights is None:
        weights = {
            "probability": 0.3,
            "embedding": 0.3,
            "tree": 0.4
        }
    
    # Compute individual scores
    prob_score = probability_score(P, y)
    emb_score = embedding_distance_score(P, y, sequence_embeddings, species_embeddings)
    tree_score = tree_aware_score(P, y, tree_distance, radii)
    
    # Normalize scores to [0, 1]
    prob_score = prob_score / (prob_score.max() + 1e-12)
    emb_score = emb_score / (emb_score.max() + 1e-12)
    tree_score = tree_score / (tree_score.max() + 1e-12)
    
    # Combine with weights
    combined = (
        weights["probability"] * prob_score +
        weights["embedding"] * emb_score +
        weights["tree"] * tree_score
    )
    
    return combined
