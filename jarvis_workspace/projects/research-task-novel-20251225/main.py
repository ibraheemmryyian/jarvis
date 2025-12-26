import torch
from sparse_attention import SparseAttention

# Test case
d_model = 512 
num_heads = 8
seq_len = 100
batch_size = 4

# Create random input tensor
x = torch.randn(batch_size, seq_len, d_model)

# Instantiate the modules
sparse_attn = SparseAttention(d_model, num_heads)
base_attn = nn.MultiheadAttention(embed_dim=d_model, num_heads=num_heads)

# Run both attention modules and compare output shapes
output_sparse = sparse_attn(x)
output_base = base_attn(x)[0]

print(f"Sparse Attention Output Shape: {output_sparse.shape}")
print(f"Base Attention Output Shape: {output_base.shape}")

# Save results to CSV
import csv

with open('results/benchmark_results.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=['Module', 'OutputShape'])
    writer.writeheader()
    writer.writerow({'Module': 'SparseAttention', 'OutputShape': str(output_sparse.shape)})
    writer.writerow({'Module': 'MultiheadAttention', 'OutputShape': str(output_base.shape)})