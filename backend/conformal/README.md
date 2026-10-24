# Conformal Prediction for Zero-Shot eDNA Taxonomic Assignment

This module implements distribution-free prediction sets for zero-shot eDNA taxonomic assignment, calibrated for species-level shift.

## Overview

The framework provides statistically valid coverage guarantees for taxonomic assignments even when species are missing from the reference database (zero-shot learning).

## Key Components

### 1. Calibration Regimes (`calibration.py`)

- **Regime A (Random Split)**: Standard conformal calibration with random sequence holdout. Expected to under-cover on unseen species.
- **Regime B (Leave-Species-Out)**: K-fold species-level calibration that mimics true zero-shot behavior. Expected to restore coverage.
- **Regime C (Open-set Good-Turing)**: Principled handling of unseen labels using conformal p-values.
- **Regime D (Mixture)**: Weighted combination of random split and LOSO for practical scenarios.

### 2. Nonconformity Scores (`scores.py`)

- **Probability Score**: `1 - P(true_species)` - standard baseline
- **Embedding-Distance Score**: Cosine distance between sequence and species embeddings
- **Tree-Aware Score**: Phylogenetic distance from predicted mass to true species
- **Combined Score**: Weighted combination of all three components

### 3. Prediction Sets (`prediction_sets.py`)

- **Flat Sets**: Species with probability >= threshold
- **Tree-Structured Sets**: Smallest clade around top-1 with calibrated mass
- **Hierarchical Conformal**: Generic hierarchical baseline

### 4. Evaluation Metrics (`evaluation.py`)

- Empirical coverage
- Coverage gap
- Mean set size
- Specificity (average taxonomic rank)
- Singleton rate
- Tree-distance error
- Expected calibration error
- Conditional coverage
- Downstream diversity metrics

### 5. Experiment Runner (`experiments.py`)

`ConformalExperiment` class that runs the complete experimental pipeline:
- Calibration regime comparison (E2)
- Score function comparison (E3)
- Set construction comparison (E4)

### 6. Visualization (`visualization.py`)

Functions to create paper figures:
- Coverage vs target (Figure 2)
- Set size vs coverage (Figure 3)
- Coverage heatmap (Figure 4)
- Reliability diagram (Figure 6)
- Downstream metrics (Figure 7)

### 7. Integration (`integration.py`)

`ConformalWrapper` class that integrates conformal prediction with the existing eDNA pipeline.

## Quick Start

### Basic Usage with Synthetic Data

```python
from conformal.experiments import ConformalExperiment
from conformal.scores import probability_score
import numpy as np

# Create synthetic data (replace with real data)
X, y, E, D = make_synthetic_data()

# Initialize experiment
experiment = ConformalExperiment(
    model=ZeroShotModel(E),
    alphas=[0.05, 0.1, 0.2],
    radii=(0, 1, 2, 3, 4),
    K=5,
    seed=42
)

# Split species
n_species = E.shape[0]
sp_perm = np.random.permutation(n_species)
test_sp = sp_perm[:int(0.2 * n_species)]
train_sp = sp_perm[int(0.2 * n_species):]

# Run calibration comparison
results = experiment.run_calibration_comparison(
    X, y, train_sp, test_sp,
    sequence_embeddings=X @ E,
    species_embeddings=E,
    tree_distance=D,
    score_type="probability"
)

# Print results
for regime, regime_results in results.items():
    print(f"\n{regime}:")
    for alpha_key, alpha_results in regime_results.items():
        print(f"  {alpha_key}:")
        for set_type, stats in alpha_results.items():
            print(f"    {set_type}: coverage={stats['coverage']:.3f}, "
                  f"set_size={stats['mean_set_size']:.1f}")
```

### Integration with eDNA Pipeline

```python
from ml.pipeline import eDNAPipeline
from conformal.integration import ConformalWrapper

# Load or train your pipeline
pipeline = eDNAPipeline(num_species=31500)
# ... train pipeline ...

# Create conformal wrapper
wrapper = ConformalWrapper(
    pipeline=pipeline,
    num_species=31500,
    alpha=0.1
)

# Calibrate with LOSO
wrapper.calibrate(
    X_cal=X_calibration,
    y_cal=y_calibration,
    sequence_embeddings=sequence_embeddings,
    species_embeddings=species_embeddings,
    tree_distance=tree_distance
)

# Predict sets for new sequences
mask_flat, mask_clade = wrapper.predict_sets(
    X_test,
    sequence_embeddings_test,
    species_embeddings,
    tree_distance
)

# Evaluate
metrics = wrapper.evaluate(
    X_test,
    y_test,
    sequence_embeddings_test,
    species_embeddings,
    tree_distance
)
```

## Research Questions

The framework is designed to answer these research questions:

**RQ1**: Does standard random-split conformal calibration give valid coverage on unseen species?
- Expected: No, it under-covers because calibration species were seen in training.

**RQ2**: Does leave-species-out calibration restore coverage?
- Expected: Yes, within about 2 percentage points of the target level.

**RQ3**: Do tree-structured sets beat flat top-k sets?
- Expected: Tree sets are smaller at equal coverage.

**RQ4**: Does adding co-occurrence and embedding distance to the score help?
- Expected: Yes, smaller sets at the same coverage.

**RQ5**: Does using several phylogenetic trees improve calibration?
- Expected: Yes, it reduces over-confidence from tree uncertainty.

**RQ6**: Does the approach transfer to another taxon and marker?
- Expected: Yes, coverage holds on insect COI barcodes.

**RQ7**: Do calibrated sets reduce distortion in downstream ecological metrics?
- Expected: Yes, diversity estimates become less biased.

## File Structure

```
conformal/
├── __init__.py
├── calibration.py      # Calibration regimes
├── scores.py           # Nonconformity scores
├── prediction_sets.py  # Set construction
├── evaluation.py       # Evaluation metrics
├── experiments.py      # Experiment runner
├── visualization.py    # Plotting functions
├── integration.py      # Pipeline integration
└── README.md          # This file
```

## Dependencies

- numpy
- scipy (for evaluation metrics)
- matplotlib (for visualization)
- torch (for pipeline integration)

## References

This implementation is based on the research plan for:
"Distribution-free taxonomic prediction sets for zero-shot eDNA assignment"

Related work:
- Stalder et al. 2025 - Zero-shot deep learning for eDNA annotation
- Hierarchical conformal classification
- Open-set conformal prediction with Good-Turing p-values
- Conformal prediction for long-tailed species identification

## Citation

If you use this code in your research, please cite:
- The original eDNA zero-shot method (Stalder et al. 2025)
- This conformal prediction framework (when published)

## License

This code is part of the eDNA Taxonomy Workbench project.
