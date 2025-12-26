import time

def benchmark(model, input_data):
    start_time = time.time()
    output = model(input_data)
    end_time = time.time()
    
    speed = (end_time - start_time) / len(input_data)
    memory_usage = ...
    
    return {
        'speed': speed,
        'memory_usage': memory_usage
    }

# Run benchmarks and save results
results = benchmark(sparse_transformer, input_data)
with open('results/benchmark_results.csv', 'w') as f:
    f.write(f'speed,{results['speed']}\nmemory_usage,{results['memory_usage']}')