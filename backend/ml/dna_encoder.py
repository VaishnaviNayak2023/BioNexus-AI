import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from typing import List, Tuple
import numpy as np

class DNAEncoder(nn.Module):
    """
    Stage 2: DNA encoder
    Train a small neural network to map a raw DNA sequence into the same
    64-dimensional space as the phylogenetic embeddings.
    
    Network architecture:
    - Learnable nucleotide embedding (A, C, G, T, N, pad)
    - Two 1D convolution layers (kernel size 5; second dilated by 5)
    - MLP with 2048-unit hidden layer and 64-unit output
    """
    def __init__(self, seq_length: int, embedding_dim: int = 64, hidden_dim: int = 2048):
        super().__init__()
        self.seq_length = seq_length
        self.embedding_dim = embedding_dim
        
        # Nucleotide embedding: A, C, G, T, N, pad (6 tokens)
        self.nucleotide_emb = nn.Embedding(6, 16)
        
        # Convolutional layers
        self.conv1 = nn.Conv1d(16, 64, kernel_size=5, padding=2)
        self.conv2 = nn.Conv1d(64, 64, kernel_size=5, padding=10, dilation=5)
        
        # MLP head
        self.head = nn.Sequential(
            nn.LazyLinear(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, embedding_dim)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (batch, seq_length) tensor of nucleotide indices
               0=A, 1=C, 2=G, 3=T, 4=N, 5=pad
        
        Returns:
            (batch, embedding_dim) tensor of sequence embeddings
        """
        # Embed nucleotides: (batch, seq_length, 16)
        h = self.nucleotide_emb(x)
        
        # Transpose for conv1d: (batch, 16, seq_length)
        h = h.transpose(1, 2)
        
        # Conv layers
        h = F.relu(self.conv1(h))
        h = F.relu(self.conv2(h))
        
        # Flatten: (batch, 64 * seq_length)
        h = h.flatten(1)
        
        # MLP: (batch, embedding_dim)
        return self.head(h)

def encode_sequence(
    sequence: str,
    seq_length: int
) -> np.ndarray:
    """
    Convert DNA sequence to nucleotide indices.
    
    Args:
        sequence: DNA sequence string
        seq_length: Fixed length to pad/truncate to
    
    Returns:
        Array of nucleotide indices
    """
    nucleotide_map = {'A': 0, 'C': 1, 'G': 2, 'T': 3, 'N': 4, 'a': 0, 'c': 1, 'g': 2, 't': 3, 'n': 4}
    
    # Convert to indices
    indices = []
    for char in sequence:
        if char in nucleotide_map:
            indices.append(nucleotide_map[char])
        else:
            indices.append(4)  # N for unknown
    
    # Pad or truncate
    if len(indices) < seq_length:
        indices += [5] * (seq_length - len(indices))  # pad
    else:
        indices = indices[:seq_length]
    
    return np.array(indices)

def train_dna_encoder(
    sequences: List[str],
    species_embeddings: np.ndarray,
    species_labels: List[int],
    seq_length: int = 200,
    embedding_dim: int = 64,
    hidden_dim: int = 2048,
    epochs: int = 50,
    learning_rate: float = 1e-3,
    batch_size: int = 16
) -> Tuple[DNAEncoder, np.ndarray]:
    """
    Train the DNA encoder to map sequences to phylogenetic embedding space.
    
    Args:
        sequences: List of DNA sequences
        species_embeddings: Pre-trained species embeddings (num_species, embedding_dim)
        species_labels: Species index for each sequence
        seq_length: Fixed sequence length
        embedding_dim: Dimension of embedding space
        hidden_dim: Hidden layer dimension in MLP
        epochs: Number of training epochs
        learning_rate: Learning rate for optimizer
        batch_size: Batch size for training
    
    Returns:
        Trained model and sequence embeddings
    """
    model = DNAEncoder(seq_length, embedding_dim, hidden_dim)
    optimizer = optim.AdamW(model.parameters(), lr=learning_rate)
    
    # Freeze species embeddings
    species_emb_tensor = torch.tensor(species_embeddings, dtype=torch.float32)
    
    # Prepare data
    encoded_sequences = [encode_sequence(seq, seq_length) for seq in sequences]
    sequence_tensor = torch.tensor(encoded_sequences, dtype=torch.long)
    label_tensor = torch.tensor(species_labels, dtype=torch.long)
    
    num_samples = len(sequences)
    
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        
        # Shuffle and batch
        indices = np.random.permutation(num_samples)
        for i in range(0, num_samples, batch_size):
            batch_indices = indices[i:i + batch_size]
            batch_seqs = sequence_tensor[batch_indices]
            batch_labels = label_tensor[batch_indices]
            
            optimizer.zero_grad()
            
            # Forward pass
            seq_embeddings = model(batch_seqs)
            
            # Get target species embeddings
            target_embeddings = species_emb_tensor[batch_labels]
            
            # Loss: cosine similarity (want to maximize, so minimize 1 - cosine)
            cosine_sim = F.cosine_similarity(seq_embeddings, target_embeddings)
            loss = (1 - cosine_sim).mean()
            
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch + 1}/{epochs}, Loss: {epoch_loss / (num_samples // batch_size):.4f}")
    
    # Generate final embeddings for all sequences
    model.eval()
    with torch.no_grad():
        final_embeddings = model(sequence_tensor).cpu().numpy()
    
    return model, final_embeddings
