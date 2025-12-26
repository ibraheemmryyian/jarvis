import torch
import torch.nn as nn

class SparseAttention(nn.Module):
    def __init__(self, d_model, num_heads, dropout=0.1):
        super().__init__()
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        
        self.qkv = nn.Linear(d_model, d_model * 3)
        self.fc_out = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        batch_size = x.size(0)
        
        # Linearly project and split into Q, K, V
        qkv = self.qkv(x).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        q, k, v = torch.chunk(qkv, chunks=3, dim=-1)

        # Compute attention scores (QK^T)
        attn_scores = torch.matmul(q, k.transpose(-2, -1)) / (self.head_dim ** 0.5) 

        # Apply sparse masking
        mask = torch.zeros(attn_scores.size(), dtype=torch.bool).to(x.device)
        attn_scores = attn_scores.masked_fill(mask, float('-inf'))

        # Compute attention weights and apply softmax 
        attn_weights = nn.functional.softmax(attn_scores, dim=-1)

        # Apply dropout
        attn_weights = self.dropout(attn_weights)

        # Compute attention output
        attn_output = torch.matmul(attn_weights, v).transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        
        # Linearly project to the output dimension
        attn_output = self.fc_out(attn_output)

        return attn_output