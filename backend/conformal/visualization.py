"""
Visualization tools for conformal prediction results.

Creates figures for the paper:
- Coverage vs target coverage (Figure 2)
- Set size vs coverage (Figure 3)
- Coverage by region/clade (Figure 4)
- Example phylogenetic tree with predicted sets (Figure 5)
- Reliability diagram (Figure 6)
- Downstream diversity metrics (Figure 7)
"""
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
import json


def plot_coverage_vs_target(
    results: Dict,
    alphas: List[float],
    save_path: Optional[str] = None
):
    """
    Figure 2: Coverage against target (1 - alpha) for each calibration regime.
    
    Shows diagonal ideal line and how each regime performs.
    """
    plt.figure(figsize=(8, 6))
    
    targets = [1 - a for a in alphas]
    
    # Plot ideal line
    plt.plot(targets, targets, 'k--', label='Ideal (perfect calibration)', linewidth=2)
    
    # Plot each regime
    colors = ['blue', 'red', 'green', 'orange']
    markers = ['o', 's', '^', 'D']
    
    for idx, (regime_name, regime_results) in enumerate(results.items()):
        coverages_flat = []
        coverages_clade = []
        
        for alpha in alphas:
            alpha_key = f"alpha_{alpha}"
            if alpha_key in regime_results:
                if "flat" in regime_results[alpha_key]:
                    coverages_flat.append(regime_results[alpha_key]["flat"]["coverage"])
                if "clade" in regime_results[alpha_key]:
                    coverages_clade.append(regime_results[alpha_key]["clade"]["coverage"])
        
        if coverages_flat:
            plt.plot(targets, coverages_flat, marker=markers[idx], color=colors[idx],
                    linestyle='-', label=f'{regime_name} (flat)', markersize=8)
        if coverages_clade:
            plt.plot(targets, coverages_clade, marker=markers[idx], color=colors[idx],
                    linestyle='--', label=f'{regime_name} (clade)', markersize=8)
    
    plt.xlabel('Target coverage (1 - α)', fontsize=12)
    plt.ylabel('Empirical coverage', fontsize=12)
    plt.title('Coverage vs Target for Different Calibration Regimes', fontsize=14)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.plot([0, 1], [0, 1], 'k--', alpha=0.5)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to {save_path}")
    
    plt.close()


def plot_set_size_vs_coverage(
    results: Dict,
    alphas: List[float],
    save_path: Optional[str] = None
):
    """
    Figure 3: Set size against coverage for each set construction.
    
    Shows the efficiency frontier.
    """
    plt.figure(figsize=(8, 6))
    
    colors = ['blue', 'red', 'green']
    markers = ['o', 's', '^']
    
    for idx, (regime_name, regime_results) in enumerate(results.items()):
        coverages = []
        set_sizes = []
        
        for alpha in alphas:
            alpha_key = f"alpha_{alpha}"
            if alpha_key in regime_results:
                if "flat" in regime_results[alpha_key]:
                    coverages.append(regime_results[alpha_key]["flat"]["coverage"])
                    set_sizes.append(regime_results[alpha_key]["flat"]["mean_set_size"])
                if "clade" in regime_results[alpha_key]:
                    coverages.append(regime_results[alpha_key]["clade"]["coverage"])
                    set_sizes.append(regime_results[alpha_key]["clade"]["mean_set_size"])
        
        if coverages:
            plt.scatter(coverages, set_sizes, marker=markers[idx], color=colors[idx],
                       s=100, label=regime_name, alpha=0.7)
    
    plt.xlabel('Coverage', fontsize=12)
    plt.ylabel('Mean set size', fontsize=12)
    plt.title('Efficiency Frontier: Set Size vs Coverage', fontsize=14)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to {save_path}")
    
    plt.close()


def plot_coverage_heatmap(
    coverage_by_group: Dict[str, float],
    group_labels: List[str],
    save_path: Optional[str] = None
):
    """
    Figure 4: Heatmap of coverage by clade and region.
    
    Highlights under-covered groups.
    """
    # Convert to matrix
    groups = list(coverage_by_group.keys())
    values = [coverage_by_group[g] for g in groups]
    
    # Reshape if we have region x clade structure
    n_groups = len(groups)
    matrix = np.array(values).reshape(int(np.sqrt(n_groups)), -1)
    
    plt.figure(figsize=(10, 8))
    im = plt.imshow(matrix, cmap='RdYlGn', vmin=0.5, vmax=1.0, aspect='auto')
    
    # Add colorbar
    cbar = plt.colorbar(im)
    cbar.set_label('Coverage', fontsize=12)
    
    # Add text annotations
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            text = plt.text(j, i, f'{matrix[i, j]:.2f}',
                          ha="center", va="center", color="black", fontsize=10)
    
    plt.xlabel('Clade', fontsize=12)
    plt.ylabel('Region', fontsize=12)
    plt.title('Conditional Coverage by Group', fontsize=14)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to {save_path}")
    
    plt.close()


def plot_reliability_diagram(
    mean_conf: np.ndarray,
    accuracy: np.ndarray,
    save_path: Optional[str] = None
):
    """
    Figure 6: Reliability diagram of the base model's probabilities.
    
    Shows calibration before conformal correction.
    """
    plt.figure(figsize=(8, 6))
    
    plt.plot([0, 1], [0, 1], 'k--', label='Perfect calibration', linewidth=2)
    plt.plot(mean_conf, accuracy, 'o-', label='Model', markersize=8, linewidth=2)
    
    plt.xlabel('Mean predicted probability', fontsize=12)
    plt.ylabel('Actual accuracy', fontsize=12)
    plt.title('Reliability Diagram', fontsize=14)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to {save_path}")
    
    plt.close()


def plot_downstream_metrics(
    metrics_with_sets: Dict,
    metrics_without_sets: Dict,
    save_path: Optional[str] = None
):
    """
    Figure 7: Downstream metrics with and without calibrated sets.
    
    Shows error in richness, phylogenetic diversity, and functional diversity.
    """
    metric_names = ['richness_error', 'phylogenetic_diversity_error']
    if 'functional_diversity_error' in metrics_with_sets:
        metric_names.append('functional_diversity_error')
    
    x = np.arange(len(metric_names))
    width = 0.35
    
    with_sets = [metrics_with_sets[m] for m in metric_names]
    without_sets = [metrics_without_sets[m] for m in metric_names]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars1 = ax.bar(x - width/2, with_sets, width, label='With calibrated sets', color='steelblue')
    bars2 = ax.bar(x + width/2, without_sets, width, label='Without calibrated sets', color='coral')
    
    ax.set_xlabel('Diversity metric', fontsize=12)
    ax.set_ylabel('Error', fontsize=12)
    ax.set_title('Impact of Calibrated Sets on Downstream Diversity Metrics', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels([m.replace('_', ' ').title() for m in metric_names], rotation=45, ha='right')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.3f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to {save_path}")
    
    plt.close()


def create_summary_table(
    results: Dict,
    alphas: List[float],
    save_path: Optional[str] = None
) -> str:
    """
    Create a summary table in Markdown format.
    
    Table 2: Main results for all methods at alpha = 0.1
    """
    table = "| Method | Set Type | Coverage | Coverage Gap | Mean Set Size | Singleton Rate |\n"
    table += "|--------|----------|----------|--------------|---------------|----------------|\n"
    
    alpha = 0.1
    alpha_key = f"alpha_{alpha}"
    
    for regime_name, regime_results in results.items():
        if alpha_key not in regime_results:
            continue
        
        for set_type in ["flat", "clade"]:
            if set_type not in regime_results[alpha_key]:
                continue
            
            stats = regime_results[alpha_key][set_type]
            table += f"| {regime_name} | {set_type} | {stats['coverage']:.3f} | "
            table += f"{stats['coverage_gap']:.3f} | {stats['mean_set_size']:.1f} | "
            table += f"{stats['singleton_rate']:.3f} |\n"
    
    if save_path:
        with open(save_path, 'w') as f:
            f.write(table)
        print(f"Table saved to {save_path}")
    
    return table
