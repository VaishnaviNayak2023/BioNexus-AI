import torch
import torch.nn as nn
import torch.optim as optim
from typing import List, Tuple
import numpy as np

class PhylogeneticEmbedding(nn.Module):
    """
    Stage 1: Phylogenetic embedding
    Learn a 64-dimensional vector for every species so that the cosine distance
    between two vectors matches their normalized distance on the phylogenetic tree.
    """
    def __init__(self, num_species: int, embedding_dim: int = 64):
        super().__init__()
        self.embedding = nn.Embedding(num_species, embedding_dim)
        
    def forward(self, species_ids: torch.Tensor) -> torch.Tensor:
        return self.embedding(species_ids)
    
    def get_embeddings(self) -> torch.Tensor:
        """Return all species embeddings"""
        return self.embedding.weight.detach()

def sample_opposite_branch(
    tree_distance: np.ndarray,
    species_id: int
) -> List[int]:
    """
    For each branching point on the root-to-leaf path of species i,
    pick one random tip from the sibling branch.
    
    Args:
        tree_distance: Normalized distance matrix from phylogenetic tree
        species_id: The species to sample opposite branches for
    
    Returns:
        List of species IDs from opposite branches
    """
    # TODO: Implement tree traversal to find branching points
    # This is a placeholder - actual implementation depends on tree structure
    num_species = tree_distance.shape[0]
    opposite_branches = []
    
    # Simplified: sample random species for now
    # In real implementation, this would follow the tree structure
    for _ in range(5):  # Sample 5 opposite branches
        random_species = np.random.randint(0, num_species)
        if random_species != species_id:
            opposite_branches.append(random_species)
    
    return opposite_branches

def compute_phylogenetic_loss(
    embeddings: torch.Tensor,
    tree_distance: np.ndarray,
    species_ids: List[int]
) -> torch.Tensor:
    """
    Compute loss: minimize difference between tree distance and embedding cosine distance.
    
    loss = ((d_tree[i, S_i] - cosine_dist(E[i], E[S_i])) ** 2).sum()
    """
    total_loss = 0.0
    count = 0
    
    for species_id in species_ids:
        opposite_branches = sample_opposite_branch(tree_distance, species_id)
        
        for opposite_id in opposite_branches:
            # Tree distance
            d_tree = tree_distance[species_id, opposite_id]
            
            # Embedding cosine distance
            emb_i = embeddings[species_id]
            emb_opposite = embeddings[opposite_id]
            cosine_dist = 1 - torch.nn.functional.cosine_similarity(
                emb_i.unsqueeze(0),
                emb_opposite.unsqueeze(0)
            )
            
            total_loss += (d_tree - cosine_dist) ** 2
            count += 1
    
    return total_loss / count if count > 0 else torch.tensor(0.0)

def train_phylogenetic_embedding(
    tree_distance: np.ndarray,
    num_species: int,
    embedding_dim: int = 64,
    epochs: int = 100,
    learning_rate: float = 0.01,
    batch_size: int = 64
) -> Tuple[PhylogeneticEmbedding, np.ndarray]:
    """
    Train the phylogenetic embedding model.
    
    Args:
        tree_distance: Normalized distance matrix from phylogenetic tree
        num_species: Number of species in the tree
        embedding_dim: Dimension of the embedding space
        epochs: Number of training epochs
        learning_rate: Learning rate for optimizer
        batch_size: Batch size for training
    
    Returns:
        Trained model and embedding matrix
    """
    model = PhylogeneticEmbedding(num_species, embedding_dim)
    optimizer = optim.AdamW(model.parameters(), lr=learning_rate)
    
    species_ids = list(range(num_species))
    
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        
        # Shuffle and batch
        np.random.shuffle(species_ids)
        for i in range(0, len(species_ids), batch_size):
            batch_ids = species_ids[i:i + batch_size]
            
            optimizer.zero_grad()
            
            # Get embeddings
            embeddings = model.embedding.weight
            
            # Compute loss
            loss = compute_phylogenetic_loss(embeddings, tree_distance, batch_ids)
            
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch + 1}/{epochs}, Loss: {epoch_loss / len(species_ids):.4f}")
    
    # Return final embeddings
    final_embeddings = model.get_embeddings().cpu().numpy()
    return model, final_embeddings
