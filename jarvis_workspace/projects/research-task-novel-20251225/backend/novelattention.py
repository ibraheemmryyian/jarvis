import torch
import torch.nn as nn

class NovelAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        
    def forward(self, query, key, value):
        # Compute attention scores
        attn_scores = torch.matmul(query, key.transpose(-2, -1)) / (self.config.hidden_size ** 0.5)
        
        # Apply softmax to the attention scores
        attn_weights = nn.functional.softmax(attn_scores, dim=-1)
        
        # Compute the weighted average of values based on attention weights
        attn_output = torch.matmul(attn_weights, value)
        
        return attn_output

def add_head_mask(attn_weights, head_mask, input_shape, mask_value=0.0):
    if head_mask is not None:
        attn_weights = attn_weights * head_mask
    return attn_weights

def split_heads(head, config):
    head = head.chunk(config.num_attention_heads, dim=-1)
    return [torch.unsqueeze(h, 0) for h in head]

# Usage example
config = {
    'hidden_size': 128,
    'num_attention_heads': 4,
}

query = torch.randn((1, 32, config['hidden_size']))
key = torch.randn((1, 32, config['hidden_size']))
value = torch.randn((1, 32, config['hidden_size']))

attention_layer = NovelAttention(config)
output = attention_layer(query, key, value)

print(output.shape)  # Should be (batch_size, seq_len, hidden_size)