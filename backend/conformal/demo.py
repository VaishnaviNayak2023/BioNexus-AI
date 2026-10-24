"""
Demo script for conformal prediction in zero-shot eDNA assignment.

This script demonstrates the core experiment:
- Compare calibration regimes A (random split) vs B (leave-species-out)
- Show that regime A under-covers on unseen species while B restores coverage

This is the first critical result (RQ1 and RQ2) that determines if the paper is viable.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from conformal.experiments import ConformalExperiment
from conformal.visualization import plot_coverage_vs_target, create_summary_table


def make_synthetic_data(seed=0, n_order=4, fam_per=4, gen_per=4, sp_per=5,
                        seq_per_species=20, dim=16, feat_dim=64, noise=2.5):
    """
    Create synthetic hierarchical data for testing.
    
    Generates:
    - Species embeddings E with hierarchical structure
    - Tree distance matrix D
    - Sequence features X
    - Species labels y
    
    NOTE: Increased noise to make the task harder and show coverage differences.
    """
    rng = np.random.default_rng(seed)
    
    # Create hierarchical species labels
    labels = []
    for o in range(n_order):
        for f in range(fam_per):
            for g in range(gen_per):
                for s in range(sp_per):
                    labels.append((o, f, g, s))
    labels = np.array(labels)
    n_species = len(labels)
    
    # Generate hierarchical embeddings
    c_order = rng.normal(0, 3.0, (n_order, dim))
    c_family = rng.normal(0, 2.0, (n_order, fam_per, dim))
    c_genus = rng.normal(0, 1.0, (n_order, fam_per, gen_per, dim))
    
    E = np.stack([
        c_order[o] + c_family[o, f] + c_genus[o, f, g] + rng.normal(0, 0.5, dim)
        for o, f, g, s in labels
    ])
    
    # Tree distance matrix
    D = np.full((n_species, n_species), 4, dtype=int)
    for i in range(n_species):
        for j in range(n_species):
            if i == j:
                D[i, j] = 0
            elif tuple(labels[i, :3]) == tuple(labels[j, :3]):
                D[i, j] = 1
            elif tuple(labels[i, :2]) == tuple(labels[j, :2]):
                D[i, j] = 2
            elif labels[i, 0] == labels[j, 0]:
                D[i, j] = 3
    
    # Generate sequence features
    W = rng.normal(0, 1.0, (dim, feat_dim))
    y = np.repeat(np.arange(n_species), seq_per_species)
    X = E[y] @ W + rng.normal(0, noise, (len(y), feat_dim))
    
    return X, y, E, D, X  # Return X as sequence embeddings


class SimpleZeroShotModel:
    """
    Simple zero-shot model for demo purposes.
    
    In production, replace this with the actual eDNA pipeline:
    DNA encoder -> phylogenetic embedding -> co-occurrence correction
    """
    
    def __init__(self, E_all, lam=10.0, tau=0.05):
        self.E_all = E_all
        self.En = E_all / np.linalg.norm(E_all, axis=1, keepdims=True)
        self.lam = lam
        self.tau = tau
        self.W = None
    
    def fit(self, X, y):
        """Train on sequences of training species."""
        T = self.E_all[y]
        A = X.T @ X + self.lam * np.eye(X.shape[1])
        self.W = np.linalg.solve(A, X.T @ T)
        return self
    
    def predict_proba(self, X):
        """Predict probabilities over ALL species (including unseen)."""
        Z = X @ self.W
        Z = Z / (np.linalg.norm(Z, axis=1, keepdims=True) + 1e-12)
        cos_dist = 1.0 - Z @ self.En.T
        logits = -cos_dist / self.tau
        logits -= logits.max(1, keepdims=True)
        P = np.exp(logits)
        return P / P.sum(1, keepdims=True)


def main():
    """
    Run the core experiment: compare calibration regimes A vs B.
    
    This is the "go/no-go" gate. If regime A under-covers and B fixes it,
    the paper concept is viable.
    """
    print("=" * 70)
    print("Conformal Prediction Demo: Calibration Regime Comparison")
    print("=" * 70)
    
    # Generate synthetic data
    print("\n1. Generating synthetic hierarchical data...")
    X, y, E, D, sequence_embeddings = make_synthetic_data(seed=42)
    n_species = E.shape[0]
    print(f"   - {n_species} species")
    print(f"   - {len(y)} sequences")
    print(f"   - Embedding dimension: {E.shape[1]}")
    
    # Split species into train/test
    print("\n2. Splitting species (species-level holdout)...")
    rng = np.random.default_rng(42)
    sp_perm = rng.permutation(n_species)
    test_species = sp_perm[:int(0.2 * n_species)]
    train_species = sp_perm[int(0.2 * n_species):]
    print(f"   - Training species: {len(train_species)}")
    print(f"   - Test (unseen) species: {len(test_species)}")
    
    # Initialize model
    print("\n3. Initializing zero-shot model...")
    model = SimpleZeroShotModel(E)
    
    # Initialize experiment
    print("\n4. Setting up conformal experiment...")
    alphas = [0.05, 0.1, 0.2]
    experiment = ConformalExperiment(
        model=model,
        alphas=alphas,
        radii=(0, 1, 2, 3, 4),
        K=5,
        seed=42
    )
    
    # Run calibration comparison
    print("\n5. Running calibration regime comparison...")
    print("   This tests RQ1 (does random split under-cover?) and RQ2 (does LOSO fix it?)")
    
    results = experiment.run_calibration_comparison(
        X, y, train_species, test_species,
        sequence_embeddings=sequence_embeddings,
        species_embeddings=E,
        tree_distance=D,
        score_type="probability"
    )
    
    # Print results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    for regime_name, regime_results in results.items():
        print(f"\n{regime_name}:")
        for alpha_key, alpha_results in regime_results.items():
            alpha = float(alpha_key.split('_')[1])
            target = 1 - alpha
            print(f"\n  Alpha = {alpha:.2f} (target coverage = {target:.2f}):")
            
            for set_type, stats in alpha_results.items():
                coverage = stats['coverage']
                gap = stats['coverage_gap']
                set_size = stats['mean_set_size']
                
                print(f"    {set_type:8s}: coverage = {coverage:.3f} (gap = {gap:+.3f}), "
                      f"set_size = {set_size:.1f}")
    
    # Check the core hypothesis
    print("\n" + "=" * 70)
    print("CORE HYPOTHESIS CHECK")
    print("=" * 70)
    
    alpha = 0.1
    alpha_key = f"alpha_{alpha}"
    
    if alpha_key in results["A_random_split"] and alpha_key in results["B_leave_species_out"]:
        cov_A = results["A_random_split"][alpha_key]["flat"]["coverage"]
        cov_B = results["B_leave_species_out"][alpha_key]["flat"]["coverage"]
        target = 1 - alpha
        
        print(f"\nAt alpha = {alpha} (target coverage = {target:.2f}):")
        print(f"  Regime A (random split): coverage = {cov_A:.3f}")
        print(f"  Regime B (LOSO): coverage = {cov_B:.3f}")
        
        if cov_A < target - 0.05:
            print(f"\n  [OK] Regime A UNDER-COVERS (as expected): {cov_A:.3f} < {target:.2f}")
        else:
            print(f"\n  [!] Regime A does NOT under-cover (unexpected): {cov_A:.3f} >= {target:.2f}")
        
        if abs(cov_B - target) < 0.05:
            print(f"  [OK] Regime B APPROXIMATES target (as expected): {cov_B:.3f} ~= {target:.2f}")
        else:
            print(f"  [!] Regime B does NOT approximate target (unexpected): {cov_B:.3f} != {target:.2f}")
        
        if cov_A < target - 0.05 and abs(cov_B - target) < 0.05:
            print("\n  [SUCCESS] CORE HYPOTHESIS CONFIRMED: LOSO calibration restores coverage!")
            print("     This is a publishable result. Proceed with full experiments.")
        else:
            print("\n  [WARNING] CORE HYPOTHESIS NOT CONFIRMED: Reconsider the framing.")
    
    # Generate visualization
    print("\n6. Generating coverage vs target plot...")
    plot_coverage_vs_target(
        results,
        alphas,
        save_path="conformal_coverage_plot.png"
    )
    
    # Generate summary table
    print("\n7. Generating summary table...")
    table = create_summary_table(
        results,
        alphas,
        save_path="conformal_summary_table.md"
    )
    print(table)
    
    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Replace synthetic data with real eDNA data")
    print("2. Replace SimpleZeroShotModel with actual eDNA pipeline")
    print("3. Run full experiments (score comparison, set comparison, etc.)")
    print("4. Generate all figures and tables for the paper")
    print("\nSee conformal/README.md for full documentation.")


if __name__ == "__main__":
    main()
