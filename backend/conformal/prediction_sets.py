"""
Prediction set construction for conformal prediction in zero-shot eDNA assignment.

Implements:
- Flat sets: species with probability >= threshold
- Tree-structured sets: smallest clade around top-1 with calibrated mass
- Generic hierarchical conformal baseline
"""
import numpy as np
from typing import Tuple, Optional


def flat_sets(P: np.ndarray, q: float) -> np.ndarray:
    """
    Flat prediction sets.
    
    Set = species with 1 - p <= q.
    Always keep top-1 so sets are never empty.
    
    Args:
        P: Probability matrix (n_samples, n_species)
        q: Quantile threshold from calibration
    
    Returns:
        Boolean mask (n_samples, n_species) indicating set membership
    """
    mask = (1.0 - P) <= q
    # Always include top-1 prediction
    mask[np.arange(len(P)), P.argmax(axis=1)] = True
    return mask


def clade_masses(P: np.ndarray, tree_distance: np.ndarray, radii: Tuple[int, ...]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute probability mass inside clades of different radii around top-1 prediction.
    
    Args:
        P: Probability matrix (n_samples, n_species)
        tree_distance: Tree distance matrix (n_species, n_species)
        radii: Tree radii for clade levels
    
    Returns:
        masses: Probability mass at each level (n_samples, n_levels)
        top1: Top-1 species for each sample (n_samples,)
    """
    top1 = P.argmax(axis=1)
    n_samples, n_levels = len(P), len(radii)
    masses = np.zeros((n_samples, n_levels))
    
    for level_idx, radius in enumerate(radii):
        # Get species within radius of top-1
        in_clade = tree_distance[top1] <= radius  # (n_samples, n_species)
        # Sum probability mass in clade
        masses[:, level_idx] = (P * in_clade).sum(axis=1)
    
    return masses, top1


def clade_sets(
    P: np.ndarray,
    tree_distance: np.ndarray,
    radii: Tuple[int, ...],
    q: float
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Tree-structured prediction sets.
    
    Return the smallest clade around top-1 whose probability mass exceeds q.
    
    Args:
        P: Probability matrix (n_samples, n_species)
        tree_distance: Tree distance matrix
        radii: Tree radii for clade levels
        q: Calibrated threshold
    
    Returns:
        mask: Boolean membership matrix (n_samples, n_species)
        chosen: Chosen level for each sample (n_samples,)
    """
    masses, top1 = clade_masses(P, tree_distance, radii)
    n_samples, n_levels = masses.shape
    
    # Find smallest level with mass > q (from most specific to least)
    chosen = np.full(n_samples, n_levels - 1)  # Default to root (last level)
    
    for level_idx in range(n_levels - 1, -1, -1):
        # Update chosen for samples where this level exceeds threshold
        # and we haven't already chosen a more specific level
        mask_level = masses[:, level_idx] > q
        more_specific = chosen > level_idx
        chosen = np.where(mask_level & more_specific, level_idx, chosen)
    
    # Create membership mask based on chosen radii
    radii_arr = np.array(radii)[chosen]
    mask = tree_distance[top1] <= radii_arr[:, np.newaxis]
    
    return mask, chosen


def hierarchical_conformal_sets(
    P: np.ndarray,
    taxonomy: np.ndarray,
    q: float,
    max_nodes: Optional[int] = None
) -> np.ndarray:
    """
    Generic hierarchical conformal classification baseline.
    
    Build sets by aggregating probabilities up the taxonomy hierarchy.
    
    Args:
        P: Probability matrix (n_samples, n_species)
        taxonomy: Taxonomy matrix (n_species, n_ranks) with rank assignments
        q: Calibrated threshold
        max_nodes: Maximum number of nodes in set (for interpretability)
    
    Returns:
        Boolean mask (n_samples, n_species)
    """
    n_samples, n_species = P.shape
    mask = np.zeros((n_samples, n_species), dtype=bool)
    
    for i in range(n_samples):
        # Sort species by probability
        sorted_idx = np.argsort(P[i])[::-1]
        cum_prob = 0.0
        
        for idx in sorted_idx:
            if max_nodes and mask[i].sum() >= max_nodes:
                break
            
            cum_prob += P[i, idx]
            mask[i, idx] = True
            
            if cum_prob >= q:
                break
    
    return mask


def set_statistics(mask: np.ndarray, y: np.ndarray, tree_distance: np.ndarray) -> dict:
    """
    Compute statistics about prediction sets.
    
    Args:
        mask: Boolean mask (n_samples, n_species)
        y: True species labels (n_samples,)
        tree_distance: Tree distance matrix
    
    Returns:
        Dictionary of statistics
    """
    n_samples = mask.shape[0]
    
    # Coverage: fraction of sets containing true species
    coverage = mask[np.arange(n_samples), y].mean()
    
    # Mean set size
    set_size = mask.sum(axis=1).mean()
    
    # Singleton rate: fraction of single-species sets
    singleton_rate = (mask.sum(axis=1) == 1).mean()
    
    # Specificity: average taxonomic rank of smallest enclosing clade
    # Compute distance from top-1 to true species
    top1 = np.zeros(n_samples, dtype=int)
    for i in range(n_samples):
        top1[i] = np.where(mask[i])[0][0] if mask[i].any() else 0
    
    # Average distance from prediction to truth
    tree_dist_error = tree_distance[top1, y].mean()
    
    return {
        "coverage": coverage,
        "mean_set_size": set_size,
        "singleton_rate": singleton_rate,
        "tree_distance_error": tree_dist_error
    }
