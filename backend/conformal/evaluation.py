"""
Evaluation metrics for conformal prediction in zero-shot eDNA assignment.

Implements metrics from the research plan:
- Empirical coverage
- Coverage gap
- Mean set size
- Specificity (average taxonomic rank)
- Singleton rate
- Tree-distance error
- Calibration error
- Conditional coverage
- Downstream bias (richness, phylogenetic diversity, functional diversity)
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy.stats import entropy


def empirical_coverage(mask: np.ndarray, y: np.ndarray) -> float:
    """
    Fraction of test sequences whose true species lies inside the set.
    
    Args:
        mask: Boolean mask (n_samples, n_species)
        y: True species labels (n_samples,)
    
    Returns:
        Coverage value in [0, 1]
    """
    n_samples = mask.shape[0]
    return mask[np.arange(n_samples), y].mean()


def coverage_gap(coverage: float, alpha: float) -> float:
    """
    Empirical coverage minus target (1 - alpha).
    
    Negative values indicate under-coverage.
    
    Args:
        coverage: Empirical coverage
        alpha: Target miscoverage level
    
    Returns:
        Coverage gap
    """
    target = 1 - alpha
    return coverage - target


def mean_set_size(mask: np.ndarray) -> float:
    """
    Average number of species covered by the set.
    
    Args:
        mask: Boolean mask (n_samples, n_species)
    
    Returns:
        Mean set size
    """
    return mask.sum(axis=1).mean()


def specificity(mask: np.ndarray, tree_distance: np.ndarray, y: np.ndarray) -> float:
    """
    Average taxonomic rank of the set's smallest enclosing clade.
    
    Lower is better (more specific).
    
    Args:
        mask: Boolean mask (n_samples, n_species)
        tree_distance: Tree distance matrix
        y: True species labels
    
    Returns:
        Average specificity score
    """
    n_samples = mask.shape[0]
    specificities = []
    
    for i in range(n_samples):
        if not mask[i].any():
            specificities.append(4.0)  # Maximum distance (no prediction)
            continue
        
        # Get species in set
        set_species = np.where(mask[i])[0]
        
        # Find minimum distance from any species in set to true species
        distances = tree_distance[set_species, y[i]]
        min_dist = distances.min()
        specificities.append(min_dist)
    
    return np.mean(specificities)


def singleton_rate(mask: np.ndarray) -> float:
    """
    Share of sequences with a one-species set.
    
    High singleton rate is practically valuable.
    
    Args:
        mask: Boolean mask (n_samples, n_species)
    
    Returns:
        Singleton rate in [0, 1]
    """
    return (mask.sum(axis=1) == 1).mean()


def tree_distance_error(mask: np.ndarray, tree_distance: np.ndarray, y: np.ndarray) -> float:
    """
    Mean phylogenetic distance from the prediction to the true species.
    
    More fair than top-1 accuracy because "wrong genus" and "wrong order"
    are treated differently.
    
    Args:
        mask: Boolean mask (n_samples, n_species)
        tree_distance: Tree distance matrix
        y: True species labels
    
    Returns:
        Mean tree distance error
    """
    n_samples = mask.shape[0]
    distances = []
    
    for i in range(n_samples):
        if not mask[i].any():
            distances.append(4.0)  # Maximum distance
            continue
        
        # Use top-1 species in set
        top1 = np.where(mask[i])[0][0]
        distances.append(tree_distance[top1, y[i]])
    
    return np.mean(distances)


def top_k_accuracy_at_ranks(
    P: np.ndarray,
    y: np.ndarray,
    taxonomy: np.ndarray,
    ranks: List[str] = ["species", "genus", "family", "order"]
) -> Dict[str, float]:
    """
    Top-1 accuracy at each taxonomic rank.
    
    Args:
        P: Probability matrix (n_samples, n_species)
        y: True species labels (n_samples,)
        taxonomy: Taxonomy assignments (n_species, n_ranks)
        ranks: List of rank names
    
    Returns:
        Dictionary mapping rank to accuracy
    """
    top1 = P.argmax(axis=1)
    accuracies = {}
    
    for rank_idx, rank_name in enumerate(ranks):
        # Check if top-1 and true species match at this rank
        match = taxonomy[top1, rank_idx] == taxonomy[y, rank_idx]
        accuracies[rank_name] = match.mean()
    
    return accuracies


def expected_calibration_error(P: np.ndarray, y: np.ndarray, n_bins: int = 10) -> float:
    """
    Expected calibration error of the underlying probabilities.
    
    Diagnoses whether the base model is well-calibrated before conformal.
    
    Args:
        P: Probability matrix (n_samples, n_species)
        y: True species labels (n_samples,)
        n_bins: Number of probability bins
    
    Returns:
        ECE value
    """
    confidences = P[np.arange(len(y)), y]
    n_samples = len(confidences)
    
    # Sort by confidence
    sorted_indices = np.argsort(confidences)
    confidences = confidences[sorted_indices]
    y_sorted = y[sorted_indices]
    
    # Create bins
    bin_edges = np.linspace(0, 1, n_bins + 1)
    bin_indices = np.digitize(confidences, bin_edges, right=True) - 1
    
    ece = 0.0
    for bin_idx in range(n_bins):
        mask = bin_indices == bin_idx
        if mask.sum() == 0:
            continue
        
        bin_conf = confidences[mask].mean()
        bin_acc = (P[mask].argmax(axis=1) == y_sorted[mask]).mean()
        bin_weight = mask.sum() / n_samples
        
        ece += bin_weight * abs(bin_conf - bin_acc)
    
    return ece


def conditional_coverage(
    mask: np.ndarray,
    y: np.ndarray,
    group_labels: np.ndarray,
    group_name: str
) -> Dict[str, float]:
    """
    Coverage broken out by group (region, clade, read depth, etc.).
    
    Important for fairness: ensure method doesn't under-cover specific groups.
    
    Args:
        mask: Boolean mask (n_samples, n_species)
        y: True species labels
        group_labels: Group assignment for each sample (n_samples,)
        group_name: Name of the grouping variable
    
    Returns:
        Dictionary mapping group values to coverage
    """
    unique_groups = np.unique(group_labels)
    coverages = {}
    
    for group in unique_groups:
        group_mask = group_labels == group
        group_coverage = empirical_coverage(mask[group_mask], y[group_mask])
        coverages[f"{group_name}_{group}"] = group_coverage
    
    return coverages


def downstream_diversity_metrics(
    mask: np.ndarray,
    y: np.ndarray,
    tree_distance: np.ndarray,
    traits: Optional[np.ndarray] = None
) -> Dict[str, float]:
    """
    Propagate assignments into diversity metrics.
    
    Computes:
    - Species richness error
    - Phylogenetic diversity error
    - Functional diversity error (if traits provided)
    
    Args:
        mask: Boolean mask (n_samples, n_species)
        y: True species labels
        tree_distance: Tree distance matrix
        traits: Optional trait matrix (n_species, n_traits)
    
    Returns:
        Dictionary of diversity metrics
    """
    # True diversity
    true_species = np.unique(y)
    true_richness = len(true_species)
    
    # Predicted diversity (using top-1 from each set)
    pred_species = []
    for i in range(mask.shape[0]):
        if mask[i].any():
            pred_species.append(np.where(mask[i])[0][0])
    
    pred_species = np.array(pred_species)
    pred_richness = len(np.unique(pred_species))
    
    # Richness error
    richness_error = abs(pred_richness - true_richness) / true_richness
    
    # Phylogenetic diversity (sum of pairwise distances)
    def compute_pd(species_list):
        if len(species_list) < 2:
            return 0.0
        subset_dist = tree_distance[np.ix_(species_list, species_list)]
        return subset_dist.sum() / 2
    
    true_pd = compute_pd(true_species)
    pred_pd = compute_pd(np.unique(pred_species))
    
    pd_error = abs(pred_pd - true_pd) / (true_pd + 1e-12)
    
    metrics = {
        "richness_error": richness_error,
        "phylogenetic_diversity_error": pd_error
    }
    
    # Functional diversity if traits provided
    if traits is not None:
        true_trait_entropy = entropy(traits[true_species].mean(axis=0))
        pred_trait_entropy = entropy(traits[np.unique(pred_species)].mean(axis=0))
        
        fd_error = abs(pred_trait_entropy - true_trait_entropy) / (true_trait_entropy + 1e-12)
        metrics["functional_diversity_error"] = fd_error
    
    return metrics


def reliability_diagram(P: np.ndarray, y: np.ndarray, n_bins: int = 10) -> Tuple[np.ndarray, np.ndarray]:
    """
    Reliability diagram for the base model's probabilities.
    
    Returns:
        mean_conf: Mean confidence in each bin
        accuracy: Actual accuracy in each bin
    """
    confidences = P[np.arange(len(y)), y]
    correct = P.argmax(axis=1) == y
    
    bin_edges = np.linspace(0, 1, n_bins + 1)
    bin_indices = np.digitize(confidences, bin_edges, right=True) - 1
    
    mean_conf = []
    accuracy = []
    
    for bin_idx in range(n_bins):
        mask = bin_indices == bin_idx
        if mask.sum() == 0:
            continue
        
        mean_conf.append(confidences[mask].mean())
        accuracy.append(correct[mask].mean())
    
    return np.array(mean_conf), np.array(accuracy)
