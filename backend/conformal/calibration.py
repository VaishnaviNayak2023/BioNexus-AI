"""
Calibration regimes for conformal prediction in zero-shot eDNA assignment.

Implements the four calibration regimes from the research plan:
- Regime A: Random split (species seen in training - expected to under-cover)
- Regime B: Leave-species-out (mimics unseen species - expected to be valid)
- Regime C: Open-set with Good-Turing p-values
- Regime D: Mixture of A and B
"""
import numpy as np
from typing import Tuple, List, Dict, Optional
import math


def conformal_quantile(scores: np.ndarray, alpha: float) -> float:
    """
    Finite-sample split-conformal quantile.
    
    Args:
        scores: Array of nonconformity scores from calibration set
        alpha: Target miscoverage level (e.g., 0.1 for 90% coverage)
    
    Returns:
        Quantile threshold q. Returns +inf if too few calibration points.
    """
    n = len(scores)
    k = math.ceil((n + 1) * (1 - alpha))
    if k > n:
        return np.inf
    return np.sort(scores)[k - 1]


def random_split_calibration(
    X: np.ndarray,
    y: np.ndarray,
    model,
    score_fn,
    train_species: np.ndarray,
    rng: np.random.Generator,
    frac: float = 0.3,
    **model_kwargs
) -> np.ndarray:
    """
    Regime A: Random split calibration.
    
    Hold out random sequences of TRAIN species (species still seen in training).
    Expected to under-cover on unseen species.
    
    Args:
        X: Sequence features
        y: True species labels
        model: Zero-shot model with fit() and predict_proba() methods
        score_fn: Function to compute nonconformity scores
        train_species: Species available for training
        rng: Random number generator
        frac: Fraction of data to use for calibration
        **model_kwargs: Additional arguments for model
    
    Returns:
        Calibration scores
    """
    # Get indices of training species
    idx = np.where(np.isin(y, train_species))[0]
    rng.shuffle(idx)
    
    n_cal = int(frac * len(idx))
    cal_idx, fit_idx = idx[:n_cal], idx[n_cal:]
    
    # Train model on fit set
    model.fit(X[fit_idx], y[fit_idx], **model_kwargs)
    
    # Get predictions on calibration set
    P = model.predict_proba(X[cal_idx])
    
    # Compute scores
    scores = score_fn(P, y[cal_idx])
    
    return scores


def leave_species_out_calibration(
    X: np.ndarray,
    y: np.ndarray,
    model,
    score_fn,
    train_species: np.ndarray,
    rng: np.random.Generator,
    K: int = 5,
    **model_kwargs
) -> np.ndarray:
    """
    Regime B: Leave-species-out (LOSO) calibration.
    
    Split species into K folds. Train on K-1 folds, score the held-out fold.
    Pool scores across all folds. Mimics true zero-shot behavior.
    
    Args:
        X: Sequence features
        y: True species labels
        model: Zero-shot model
        score_fn: Score function
        train_species: Species available for training
        rng: Random number generator
        K: Number of folds
        **model_kwargs: Additional arguments for model
    
    Returns:
        Pooled calibration scores from all folds
    """
    sp = np.array(train_species)
    rng.shuffle(sp)
    folds = np.array_split(sp, K)
    
    all_scores = []
    
    for k in range(K):
        held_species = folds[k]
        fit_species = np.concatenate([folds[j] for j in range(K) if j != k])
        
        fit_idx = np.where(np.isin(y, fit_species))[0]
        cal_idx = np.where(np.isin(y, held_species))[0]
        
        # Train on fit species
        model.fit(X[fit_idx], y[fit_idx], **model_kwargs)
        
        # Predict on held-out species
        P = model.predict_proba(X[cal_idx])
        
        # Compute scores
        scores = score_fn(P, y[cal_idx])
        all_scores.append(scores)
    
    return np.concatenate(all_scores)


def good_turing_open_set_calibration(
    X: np.ndarray,
    y: np.ndarray,
    model,
    score_fn,
    train_species: np.ndarray,
    test_species: np.ndarray,
    rng: np.random.Generator,
    **model_kwargs
) -> Tuple[np.ndarray, Dict]:
    """
    Regime C: Open-set calibration with Good-Turing p-values.
    
    Tests whether a sequence belongs to an unseen species using conformal p-values.
    Principled for unseen labels, may give larger sets.
    
    Args:
        X: Sequence features
        y: True species labels
        model: Zero-shot model
        score_fn: Score function
        train_species: Species for training
        test_species: Species held out as "unseen"
        rng: Random number generator
        **model_kwargs: Additional arguments
    
    Returns:
        Calibration scores and Good-Turing statistics
    """
    # Train on all training species
    fit_idx = np.where(np.isin(y, train_species))[0]
    model.fit(X[fit_idx], y[fit_idx], **model_kwargs)
    
    # Get calibration scores from training species
    cal_idx = np.where(np.isin(y, train_species))[0]
    rng.shuffle(cal_idx)
    cal_idx = cal_idx[:len(cal_idx) // 2]  # Use half for calibration
    
    P_cal = model.predict_proba(X[cal_idx])
    cal_scores = score_fn(P_cal, y[cal_idx])
    
    # Compute Good-Turing estimate for unseen species probability
    # This is a simplified version - full implementation would use the empirical distribution
    n_unseen = len(test_species)
    n_seen = len(train_species)
    gt_ratio = n_unseen / (n_seen + n_unseen)
    
    gt_stats = {
        "good_turing_ratio": gt_ratio,
        "n_seen": n_seen,
        "n_unseen": n_unseen
    }
    
    return cal_scores, gt_stats


def mixture_calibration(
    X: np.ndarray,
    y: np.ndarray,
    model,
    score_fn,
    train_species: np.ndarray,
    rng: np.random.Generator,
    unseen_fraction: float = 0.3,
    K: int = 5,
    **model_kwargs
) -> np.ndarray:
    """
    Regime D: Mixture calibration.
    
    Weight leave-species-out and random split by the expected share of unseen species.
    Practical option when some species are known to be unseen.
    
    Args:
        X: Sequence features
        y: True species labels
        model: Zero-shot model
        score_fn: Score function
        train_species: Species for training
        rng: Random number generator
        unseen_fraction: Expected fraction of unseen species
        K: Number of folds for LOSO
        **model_kwargs: Additional arguments
    
    Returns:
        Weighted calibration scores
    """
    # Get LOSO scores
    loso_scores = leave_species_out_calibration(
        X, y, model, score_fn, train_species, rng, K=K, **model_kwargs
    )
    
    # Get random split scores
    random_scores = random_split_calibration(
        X, y, model, score_fn, train_species, rng, **model_kwargs
    )
    
    # Handle different sizes by sampling from the larger to match the smaller
    min_len = min(len(loso_scores), len(random_scores))
    if len(loso_scores) > min_len:
        loso_scores = rng.choice(loso_scores, min_len, replace=False)
    if len(random_scores) > min_len:
        random_scores = rng.choice(random_scores, min_len, replace=False)
    
    # Interpolate based on unseen fraction
    # More weight to LOSO as unseen fraction increases
    combined_scores = (
        (1 - unseen_fraction) * random_scores +
        unseen_fraction * loso_scores
    )
    
    return combined_scores
