class HierarchicalMoE(nn.Module):
    def __init__(self, num_experts, hidden_size, num_clusters):
        super().__init__()
        
        self.experts = nn.ModuleList([nn.Linear(hidden_size, hidden_size) for _ in range(num_experts)])
        self.cluster_assigner = nn.Linear(hidden_size, num_clusters)
        self.cluster_centers = nn.Parameter(torch.randn(num_clusters, hidden_size))
        
    def forward(self, x):
        cluster_assignments = self.cluster_assigner(x)
        expert_activations = torch.softmax(cluster_assignments, dim=1)
        
        # Compute cluster centroids
        cluster_centroids = (expert_activations.unsqueeze(2) * self.cluster_centers).sum(dim=1)
        
        # Routing: Use cluster centroids as gating vectors
        routing_weights = torch.sigmoid(torch.matmul(x, cluster_centroids.transpose(1, 2)))
        
        # Apply experts based on routing weights and cluster centroids
        expert_outputs = [experts[i](x) for i in range(num_experts)]
        outputs = sum([o * r for o,r in zip(expert_outputs, routing_weights)])
        
        return outputs