import torch.nn as nn
import torch

def attention(query, key, value):
    d_k = query.shape[-1]
    scores = query @ key.transpose(-2, -1) / d_k**0.5
    weights = scores.softmax(dim=-1)
    output = weights @ value
    return output, weights



class MultiHeadAttention(nn.Module):

    def __init__(self, args, is_causal=False):
        super().__init__()
        