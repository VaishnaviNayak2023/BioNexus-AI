import torch
import torch.nn as nn
import torch.optim as optim
from typing import List, Tuple, Dict
import numpy as np

class TraitEstimator(nn.Module):
    """
    Trait estimation model for zero-shot species.
    Regresses functional traits (size, trophic level, habitat) from DNA-derived embeddings.
    """
    def __init__(
        self,
        embedding_dim: int = 64,
        hidden_dim: int = 256,
        trait_dims: Dict[str, int] = None
    ):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        
        # Default trait dimensions
        if trait_dims is None:
            trait_dims = {
                "max_length": 1,  # Continuous
                "trophic_level": 1,  # Continuous
                "habitat": 10,  # Categorical (10 habitat types)
            }
        
        self.trait_dims = trait_dims
        
        # Shared feature extractor
        self.feature_extractor = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
        )
        
        # Trait-specific heads
        self.trait_heads = nn.ModuleDict({
            trait: nn.Linear(hidden_dim, dim)
            for trait, dim in trait_dims.items()
        })
    
    def forward(self, embeddings: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Args:
            embeddings: (batch, embedding_dim) species embeddings
        
        Returns:
            Dictionary of trait predictions
        """
        features = self.feature_extractor(embeddings)
        
        predictions = {}
        for trait, head in self.trait_heads.items():
            predictions[trait] = head(features)
        
        return predictions

def train_trait_estimator(
    species_embeddings: np.ndarray,
    trait_data: Dict[str, np.ndarray],  # trait_name -> (num_species, trait_dim)
    trait_dims: Dict[str, int],
    embedding_dim: int = 64,
    hidden_dim: int = 256,
    epochs: int = 100,
    learning_rate: float = 1e-3,
    batch_size: int = 32
) -> Tuple[TraitEstimator, Dict[str, np.ndarray]]:
    """
    Train trait estimation model.
    
    Args:
        species_embeddings: Pre-trained species embeddings (num_species, embedding_dim)
        trait_data: Dictionary mapping trait names to arrays of trait values
        trait_dims: Dictionary mapping trait names to output dimensions
        embedding_dim: Dimension of input embeddings
        hidden_dim: Hidden layer dimension
        epochs: Number of training epochs
        learning_rate: Learning rate
        batch_size: Batch size
    
    Returns:
        Trained model and trait predictions for all species
    """
    model = TraitEstimator(embedding_dim, hidden_dim, trait_dims)
    optimizer = optim.AdamW(model.parameters(), lr=learning_rate)
    
    # Prepare data
    num_species = species_embeddings.shape[0]
    emb_tensor = torch.tensor(species_embeddings, dtype=torch.float32)
    
    # Create masks for species with trait data
    trait_masks = {}
    trait_tensors = {}
    
    for trait, values in trait_data.items():
        mask = ~np.isnan(values).any(axis=1) if values.ndim > 1 else ~np.isnan(values)
        trait_masks[trait] = torch.tensor(mask, dtype=torch.bool)
        trait_tensors[trait] = torch.tensor(values, dtype=torch.float32)
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        
        # Shuffle
        indices = np.random.permutation(num_species)
        
        for i in range(0, num_species, batch_size):
            batch_indices = indices[i:i + batch_size]
            batch_emb = emb_tensor[batch_indices]
            
            optimizer.zero_grad()
            
            # Forward pass
            predictions = model(batch_emb)
            
            # Compute loss for each trait
            trait_losses = []
            for trait, pred in predictions.items():
                mask = trait_masks[trait][batch_indices]
                if mask.sum() > 0:
                    target = trait_tensors[trait][batch_indices]
                    
                    if trait_dims[trait] == 1:
                        # Continuous trait - MSE loss
                        loss = nn.functional.mse_loss(pred[mask], target[mask])
                    else:
                        # Categorical trait - Cross entropy
                        loss = nn.functional.cross_entropy(
                            pred[mask],
                            target[mask].argmax(dim=1) if target.ndim > 1 else target[mask].long()
                        )
                    
                    trait_losses.append(loss)
            
            if trait_losses:
                loss = sum(trait_losses) / len(trait_losses)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch + 1}/{epochs}, Loss: {total_loss / (num_species // batch_size):.4f}")
    
    # Generate predictions for all species
    model.eval()
    with torch.no_grad():
        all_predictions = model(emb_tensor)
    
    # Convert to numpy
    final_predictions = {
        trait: pred.cpu().numpy()
        for trait, pred in all_predictions.items()
    }
    
    return model, final_predictions

def estimate_traits_for_zero_shot(
    model: TraitEstimator,
    species_embeddings: np.ndarray,
    zero_shot_species: List[int]
) -> Dict[int, Dict[str, float]]:
    """
    Estimate traits for zero-shot species.
    
    Args:
        model: Trained trait estimator
        species_embeddings: All species embeddings
        zero_shot_species: Indices of zero-shot species
    
    Returns:
        Dictionary mapping species ID to trait predictions
    """
    model.eval()
    emb_tensor = torch.tensor(species_embeddings, dtype=torch.float32)
    
    with torch.no_grad():
        all_predictions = model(emb_tensor)
    
    results = {}
    for species_id in zero_shot_species:
        species_traits = {}
        for trait, predictions in all_predictions.items():
            pred_value = predictions[species_id].cpu().numpy()
            
            if model.trait_dims[trait] == 1:
                # Continuous - return as-is
                species_traits[trait] = float(pred_value)
            else:
                # Categorical - return probability distribution
                species_traits[trait] = pred_value.tolist()
        
        results[species_id] = species_traits
    
    return results
