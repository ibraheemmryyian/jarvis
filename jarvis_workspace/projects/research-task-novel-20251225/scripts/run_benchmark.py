import time
import torch
from algorithm import NovelAttention
from baseline import MultiHeadedSelfAttention

def run_benchmark(attention_fn, batch_size, seq_length):
    input_tensor = torch.randn((batch_size, seq_length, 128))
    
    start_time = time.time()
    output = attention_fn(input_tensor)
    end_time = time.time()
    
    return end_time - start_time, output.shape

def main():
    novel_attention = NovelAttention(config)
    baseline_attention = MultiHeadedSelfAttention(128, 4)

    batch_size = 32
    seq_length = 64
    
    novel_time, novel_output_shape = run_benchmark(novel_attention, batch_size, seq_length)
    baseline_time, baseline_output_shape = run_benchmark(baseline_attention, batch_size, seq_length)
    
    print(f"Novel Attention: {novel_time:.4f}s, Output Shape: {novel_output_shape}")
    print(f"Baseline Attention: {baseline_time:.4f}s, Output Shape: {baseline_output_shape}")

if __name__ == "__main__":
    main()