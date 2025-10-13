#!/usr/bin/env python3
"""
Hypergraph Clustering Coefficient


1. Estrada, E., & Rodríguez-Velázquez, J. A. (2006). 
   "Subgraph centrality and clustering in complex hyper-networks."
   Physica A: Statistical Mechanics and its Applications, 364, 581-594.

2. Gallagher, R. J., & Goldberg, D. S. (2013).
   "Clustering coefficients in protein interaction hypernetworks."
   ACM-BCB 2013.

- Node-based clustering coefficient
- Hyperedge-based clustering coefficient  
- Global clustering coefficient
"""

import numpy as np
import json
from collections import defaultdict, Counter
from itertools import combinations
from typing import List, Dict, Set, Tuple


class HypergraphClusteringCoefficient:
    
    def __init__(self, hypergraph_file: str):

        self.hyperedges = self._load_hypergraph(hypergraph_file)
        self.nodes = self._extract_nodes()
        self.node_to_edges = self._build_node_edge_mapping()
        self.edge_sizes = [len(e) for e in self.hyperedges]
        
    def _load_hypergraph(self, file_path: str) -> List[Set[str]]:

        hyperedges = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                nodes = set(line.strip().split())
                if len(nodes) > 0:
                    hyperedges.append(nodes)
        return hyperedges
    
    def _extract_nodes(self) -> Set[str]:

        nodes = set()
        for edge in self.hyperedges:
            nodes.update(edge)
        return nodes
    
    def _build_node_edge_mapping(self) -> Dict[str, List[int]]:

        mapping = defaultdict(list)
        for idx, edge in enumerate(self.hyperedges):
            for node in edge:
                mapping[node].append(idx)
        return mapping
    
    def compute_node_clustering_coefficient(self, node: str) -> float:
        """Gallagher & Goldberg (2013)
        """
        edge_indices = self.node_to_edges[node]
        if len(edge_indices) == 0:
            return 0.0
        
        neighbors = set()
        for edge_idx in edge_indices:
            neighbors.update(self.hyperedges[edge_idx])
        neighbors.discard(node)
        
        if len(neighbors) < 2:
            return 0.0
        
        actual_connections = 0
        neighbor_list = list(neighbors)
        
        for i in range(len(neighbor_list)):
            for j in range(i + 1, len(neighbor_list)):
                u, w = neighbor_list[i], neighbor_list[j]
                u_edges = set(self.node_to_edges[u])
                w_edges = set(self.node_to_edges[w])
                if len(u_edges & w_edges) > 0:
                    actual_connections += 1
        
        possible_connections = len(neighbors) * (len(neighbors) - 1) / 2
        
        return actual_connections / possible_connections if possible_connections > 0 else 0.0
    
    def compute_hyperedge_clustering_coefficient(self, edge_idx: int) -> float:
        """
        Estrada & Rodríguez-Velázquez (2006) 方法:
        """
        edge = self.hyperedges[edge_idx]
        edge_size = len(edge)
        
        if edge_size < 2:
            return 0.0
        
        connected_pairs = 0
        edge_list = list(edge)
        
        for i in range(len(edge_list)):
            for j in range(i + 1, len(edge_list)):
                u, v = edge_list[i], edge_list[j]
                u_edges = set(self.node_to_edges[u])
                v_edges = set(self.node_to_edges[v])
                common_edges = (u_edges & v_edges) - {edge_idx}
                if len(common_edges) > 0:
                    connected_pairs += 1
        
        possible_pairs = edge_size * (edge_size - 1) / 2
        
        return connected_pairs / possible_pairs if possible_pairs > 0 else 0.0
    
    def compute_global_clustering_coefficient(self) -> float:

        if len(self.nodes) == 0:
            return 0.0
        
        total_cc = sum(self.compute_node_clustering_coefficient(node) 
                      for node in self.nodes)
        return total_cc / len(self.nodes)
    
    def compute_weighted_global_clustering_coefficient(self) -> float:

        if len(self.nodes) == 0:
            return 0.0
        
        weighted_sum = 0.0
        degree_sum = 0
        
        for node in self.nodes:
            degree = len(self.node_to_edges[node])
            cc = self.compute_node_clustering_coefficient(node)
            weighted_sum += degree * cc
            degree_sum += degree
        
        return weighted_sum / degree_sum if degree_sum > 0 else 0.0
    
    def compute_hyperedge_global_clustering_coefficient(self) -> float:

        if len(self.hyperedges) == 0:
            return 0.0
        
        total_cc = sum(self.compute_hyperedge_clustering_coefficient(i) 
                      for i in range(len(self.hyperedges)))
        return total_cc / len(self.hyperedges)
    
    def compute_size_stratified_clustering(self) -> Dict[int, float]:

        size_to_edges = defaultdict(list)
        for idx, edge in enumerate(self.hyperedges):
            size_to_edges[len(edge)].append(idx)
        
        size_clustering = {}
        for size, edge_indices in size_to_edges.items():
            if size >= 2: 
                avg_cc = np.mean([self.compute_hyperedge_clustering_coefficient(idx) 
                                 for idx in edge_indices])
                size_clustering[size] = avg_cc
        
        return dict(sorted(size_clustering.items()))
    
    def compute_all_metrics(self) -> Dict:

        print("📊 计算超图聚类系数...")
        
        # 基础统计
        print("  - 计算基础统计信息...")
        num_nodes = len(self.nodes)
        num_edges = len(self.hyperedges)
        avg_edge_size = np.mean(self.edge_sizes)
        
        # 节点聚类系数分布
        print("  - 计算节点聚类系数分布...")
        node_clustering = {}
        node_cc_values = []
        for node in self.nodes:
            cc = self.compute_node_clustering_coefficient(node)
            node_clustering[node] = cc
            node_cc_values.append(cc)
        
        # 超边聚类系数分布
        print("  - 计算超边聚类系数分布...")
        edge_cc_values = []
        for i in range(len(self.hyperedges)):
            cc = self.compute_hyperedge_clustering_coefficient(i)
            edge_cc_values.append(cc)
        
        # 全局聚类系数
        print("  - 计算全局聚类系数...")
        global_cc = self.compute_global_clustering_coefficient()
        weighted_global_cc = self.compute_weighted_global_clustering_coefficient()
        edge_global_cc = self.compute_hyperedge_global_clustering_coefficient()
        
        # 分层聚类系数
        print("  - 计算分层聚类系数...")
        size_stratified_cc = self.compute_size_stratified_clustering()
        
        results = {
            'basic_stats': {
                'num_nodes': num_nodes,
                'num_hyperedges': num_edges,
                'avg_hyperedge_size': float(avg_edge_size)
            },
            'global_clustering': {
                'average_node_clustering': float(global_cc),
                'weighted_node_clustering': float(weighted_global_cc),
                'average_edge_clustering': float(edge_global_cc)
            },
            'node_clustering_distribution': {
                'mean': float(np.mean(node_cc_values)),
                'std': float(np.std(node_cc_values)),
                'min': float(np.min(node_cc_values)),
                'max': float(np.max(node_cc_values)),
                'median': float(np.median(node_cc_values)),
                'percentile_25': float(np.percentile(node_cc_values, 25)),
                'percentile_75': float(np.percentile(node_cc_values, 75))
            },
            'edge_clustering_distribution': {
                'mean': float(np.mean(edge_cc_values)),
                'std': float(np.std(edge_cc_values)),
                'min': float(np.min(edge_cc_values)),
                'max': float(np.max(edge_cc_values)),
                'median': float(np.median(edge_cc_values)),
                'percentile_25': float(np.percentile(edge_cc_values, 25)),
                'percentile_75': float(np.percentile(edge_cc_values, 75))
            },
            'size_stratified_clustering': size_stratified_cc,
            'raw_node_clustering': node_cc_values,
            'raw_edge_clustering': edge_cc_values
        }
        
        return results


def main():

    import sys
    
    if len(sys.argv) < 2:
        print("python hypergraph_clustering_coefficient.py <hypergraph_file>")
        return
    
    hypergraph_file = sys.argv[1]
    
    # 计算聚类系数
    hcc = HypergraphClusteringCoefficient(hypergraph_file)
    results = hcc.compute_all_metrics()
    
    # 保存结果
    output_file = hypergraph_file.replace('.txt', '_clustering_coefficient.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        # 移除raw数据以减小文件大小
        save_results = {k: v for k, v in results.items() 
                       if k not in ['raw_node_clustering', 'raw_edge_clustering']}
        json.dump(save_results, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()

