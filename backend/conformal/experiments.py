"""
Experiment runner for conformal prediction in zero-shot eDNA assignment.

Implements the complete experimental pipeline from the research plan.
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path
from datetime import datetime

from .calibration import (
    random_split_calibration,
    leave_species_out_calibration,
    good_turing_open_set_calibration,
    mixture_calibration,
    conformal_quantile
)
from .scores import (
    probability_score,
    embedding_distance_score,
    tree_aware_score,
    combined_score
)
from .prediction_sets import (
    flat_sets,
    clade_sets,
    hierarchical_conformal_sets,
    set_statistics
)
from .evaluation import (
    empirical_coverage,
    coverage_gap,
    mean_set_size,
    specificity,
    singleton_rate,
    tree_distance_error,
    top_k_accuracy_at_ranks,
    expected_calibration_error,
    conditional_coverage,
    downstream_diversity_metrics,
    reliability_diagram
)


class ConformalExperiment:
    """
    Main experiment class for conformal prediction in zero-shot eDNA assignment.
    """
    
    def __init__(
        self,
        model,
        alphas: List[float] = [0.05, 0.1, 0.2],
        radii: Tuple[int, ...] = (0, 1, 2, 3, 4),
        K: int = 5,
        seed: int = 42
    ):
        """
        Initialize experiment.
        
        Args:
            model: Zero-shot model with fit() and predict_proba() methods
            alphas: Target miscoverage levels
            radii: Tree radii for clade levels
            K: Number of folds for LOSO
            seed: Random seed
        """
        self.model = model
        self.alphas = alphas
        self.radii = radii
        self.K = K
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        
        # Store results
        self.results = []
        self.config = {
            "alphas": alphas,
            "radii": radii,
            "K": K,
            "seed": seed,
            "timestamp": datetime.now().isoformat()
        }
    
    def run_calibration_comparison(
        self,
        X: np.ndarray,
        y: np.ndarray,
        train_species: np.ndarray,
        test_species: np.ndarray,
        sequence_embeddings: Optional[np.ndarray] = None,
        species_embeddings: Optional[np.ndarray] = None,
        tree_distance: Optional[np.ndarray] = None,
        score_type: str = "probability"
    ) -> Dict:
        """
        Experiment E2: Compare calibration regimes A, B, C, D across alpha.
        
        Answers RQ1 and RQ2.
        
        Args:
            X: Sequence features
            y: True species labels
            train_species: Species for training
            test_species: Species held out as unseen
            sequence_embeddings: Sequence embeddings (for embedding-distance score)
            species_embeddings: Species embeddings
            tree_distance: Tree distance matrix
            score_type: Type of score to use
        
        Returns:
            Dictionary of results for each regime
        """
        # Select score function
        score_fns = {
            "probability": probability_score,
            "embedding": lambda P, y: embedding_distance_score(P, y, sequence_embeddings, species_embeddings),
            "tree": lambda P, y: tree_aware_score(P, y, tree_distance, self.radii),
            "combined": lambda P, y: combined_score(P, y, sequence_embeddings, species_embeddings, tree_distance, self.radii)
        }
        score_fn = score_fns[score_type]
        
        # Get test indices
        test_idx = np.where(np.isin(y, test_species))[0]
        X_test, y_test = X[test_idx], y[test_idx]
        
        # Train final model on all training species
        fit_idx = np.where(np.isin(y, train_species))[0]
        self.model.fit(X[fit_idx], y[fit_idx])
        P_test = self.model.predict_proba(X_test)
        
        # Run each calibration regime
        regimes = {}
        
        # Regime A: Random split
        print("Running Regime A: Random split calibration...")
        cal_scores_A = random_split_calibration(
            X, y, self.model, score_fn, train_species, self.rng
        )
        regimes["A_random_split"] = cal_scores_A
        
        # Regime B: Leave-species-out
        print("Running Regime B: Leave-species-out calibration...")
        cal_scores_B = leave_species_out_calibration(
            X, y, self.model, score_fn, train_species, self.rng, K=self.K
        )
        regimes["B_leave_species_out"] = cal_scores_B
        
        # Regime C: Open-set Good-Turing (if tree_distance available)
        if tree_distance is not None:
            print("Running Regime C: Open-set Good-Turing calibration...")
            cal_scores_C, gt_stats = good_turing_open_set_calibration(
                X, y, self.model, score_fn, train_species, test_species, self.rng
            )
            regimes["C_good_turing"] = cal_scores_C
        else:
            print("Skipping Regime C: tree_distance not available")
        
        # Regime D: Mixture
        print("Running Regime D: Mixture calibration...")
        cal_scores_D = mixture_calibration(
            X, y, self.model, score_fn, train_species, self.rng, K=self.K
        )
        regimes["D_mixture"] = cal_scores_D
        
        # Evaluate each regime
        results = {}
        for regime_name, cal_scores in regimes.items():
            regime_results = self._evaluate_regime(
                P_test, y_test, cal_scores, X_test, y_test,
                sequence_embeddings, species_embeddings, tree_distance
            )
            results[regime_name] = regime_results
        
        return results
    
    def _evaluate_regime(
        self,
        P_test: np.ndarray,
        y_test: np.ndarray,
        cal_scores: np.ndarray,
        X_test: np.ndarray,
        y_test_orig: np.ndarray,
        sequence_embeddings: Optional[np.ndarray],
        species_embeddings: Optional[np.ndarray],
        tree_distance: Optional[np.ndarray]
    ) -> Dict:
        """
        Evaluate a single calibration regime across all alphas.
        """
        regime_results = {}
        
        for alpha in self.alphas:
            alpha_results = {}
            
            # Get quantile threshold
            q = conformal_quantile(cal_scores, alpha)
            
            if np.isinf(q):
                print(f"Warning: alpha={alpha} has infinite threshold (too few calibration points)")
                continue
            
            # Flat sets
            mask_flat = flat_sets(P_test, q)
            stats_flat = set_statistics(mask_flat, y_test, tree_distance if tree_distance is not None else np.zeros((P_test.shape[1], P_test.shape[1])))
            
            alpha_results["flat"] = {
                "coverage": stats_flat["coverage"],
                "coverage_gap": coverage_gap(stats_flat["coverage"], alpha),
                "mean_set_size": stats_flat["mean_set_size"],
                "singleton_rate": stats_flat["singleton_rate"]
            }
            
            # Tree-structured sets (if tree_distance available)
            if tree_distance is not None:
                mask_clade, chosen = clade_sets(P_test, tree_distance, self.radii, q)
                stats_clade = set_statistics(mask_clade, y_test, tree_distance)
                
                alpha_results["clade"] = {
                    "coverage": stats_clade["coverage"],
                    "coverage_gap": coverage_gap(stats_clade["coverage"], alpha),
                    "mean_set_size": stats_clade["mean_set_size"],
                    "singleton_rate": stats_clade["singleton_rate"],
                    "specificity": stats_clade["tree_distance_error"]
                }
            
            regime_results[f"alpha_{alpha}"] = alpha_results
        
        return regime_results
    
    def run_score_comparison(
        self,
        X: np.ndarray,
        y: np.ndarray,
        train_species: np.ndarray,
        test_species: np.ndarray,
        sequence_embeddings: np.ndarray,
        species_embeddings: np.ndarray,
        tree_distance: np.ndarray
    ) -> Dict:
        """
        Experiment E3: Compare score functions 1 to 4.
        
        Answers RQ4.
        """
        score_types = ["probability", "embedding", "tree", "combined"]
        results = {}
        
        for score_type in score_types:
            print(f"Running with score type: {score_type}")
            results[score_type] = self.run_calibration_comparison(
                X, y, train_species, test_species,
                sequence_embeddings, species_embeddings, tree_distance,
                score_type=score_type
            )
        
        return results
    
    def run_set_comparison(
        self,
        X: np.ndarray,
        y: np.ndarray,
        train_species: np.ndarray,
        test_species: np.ndarray,
        tree_distance: np.ndarray
    ) -> Dict:
        """
        Experiment E4: Compare set constructions.
        
        Answers RQ3.
        """
        # Get test data
        test_idx = np.where(np.isin(y, test_species))[0]
        X_test, y_test = X[test_idx], y[test_idx]
        
        # Train model
        fit_idx = np.where(np.isin(y, train_species))[0]
        self.model.fit(X[fit_idx], y[fit_idx])
        P_test = self.model.predict_proba(X_test)
        
        # Calibrate with LOSO
        cal_scores = leave_species_out_calibration(
            X, y, self.model, probability_score, train_species, self.rng, K=self.K
        )
        
        results = {}
        for alpha in self.alphas:
            q = conformal_quantile(cal_scores, alpha)
            
            alpha_results = {}
            
            # Flat sets
            mask_flat = flat_sets(P_test, q)
            alpha_results["flat"] = set_statistics(mask_flat, y_test, tree_distance)
            
            # Tree-structured sets
            mask_clade, chosen = clade_sets(P_test, tree_distance, self.radii, q)
            alpha_results["clade"] = set_statistics(mask_clade, y_test, tree_distance)
            
            # Generic hierarchical conformal
            # Build simple taxonomy from tree distance
            taxonomy = self._distance_to_taxonomy(tree_distance)
            mask_hier = hierarchical_conformal_sets(P_test, taxonomy, q)
            alpha_results["hierarchical"] = set_statistics(mask_hier, y_test, tree_distance)
            
            results[f"alpha_{alpha}"] = alpha_results
        
        return results
    
    def _distance_to_taxonomy(self, tree_distance: np.ndarray) -> np.ndarray:
        """
        Convert tree distance matrix to taxonomy matrix.
        
        Simple conversion: distance 0=species, 1=genus, 2=family, 3=order
        """
        n_species = tree_distance.shape[0]
        taxonomy = np.zeros((n_species, 4), dtype=int)
        
        for i in range(n_species):
            for j in range(n_species):
                if tree_distance[i, j] == 0:
                    taxonomy[i, 0] = i  # Each species is its own species
                elif tree_distance[i, j] == 1:
                    taxonomy[i, 1] = j  # Same genus
                elif tree_distance[i, j] == 2:
                    taxonomy[i, 2] = j  # Same family
                elif tree_distance[i, j] == 3:
                    taxonomy[i, 3] = j  # Same order
        
        return taxonomy
    
    def save_results(self, filepath: str):
        """Save experiment results to JSON file."""
        with open(filepath, 'w') as f:
            json.dump({
                "config": self.config,
                "results": self.results
            }, f, indent=2)
        print(f"Results saved to {filepath}")
