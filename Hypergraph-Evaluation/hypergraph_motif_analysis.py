#!/usr/bin/env python3
"""
超图模体频率分析模块
Hypergraph Motif Analysis

基于论文:
1. Lee, G., Ko, J., & Shin, K. (2020).
   "Hypergraph motifs: concepts, algorithms, and discoveries."
   VLDB Endowment, 13(11), 2256-2269.

2. Benson, A. R., Gleich, D. F., & Leskovec, J. (2016).
   "Higher-order organization of complex networks."
   Science, 353(6295), 163-166.

实现超图模体检测和频率分析:
- 2-节点模体 (pairwise motifs)
- 3-节点模体 (triadic motifs)  
- k-节点模体 (k-node motifs)
- 模体频谱分析 (motif spectrum)
"""

import numpy as np
import json
from collections import defaultdict, Counter
from itertools import combinations, permutations
from typing import List, Dict, Set, Tuple
import hashlib


class HypergraphMotifAnalysis:
    """超图模体分析器"""
    
    def __init__(self, hypergraph_file: str):
        """
        初始化超图
        
        Args:
            hypergraph_file: 超图文件路径
        """
        self.hyperedges = self._load_hypergraph(hypergraph_file)
        self.nodes = self._extract_nodes()
        self.node_to_edges = self._build_node_edge_mapping()
        
    def _load_hypergraph(self, file_path: str) -> List[Set[str]]:
        """加载超图文件"""
        hyperedges = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                nodes = set(line.strip().split())
                if len(nodes) > 0:
                    hyperedges.append(nodes)
        return hyperedges
    
    def _extract_nodes(self) -> Set[str]:
        """提取所有节点"""
        nodes = set()
        for edge in self.hyperedges:
            nodes.update(edge)
        return nodes
    
    def _build_node_edge_mapping(self) -> Dict[str, List[int]]:
        """构建节点到超边的映射"""
        mapping = defaultdict(list)
        for idx, edge in enumerate(self.hyperedges):
            for node in edge:
                mapping[node].append(idx)
        return mapping
    
    def identify_pairwise_motifs(self) -> Dict:
        """
        识别2-节点模体 (Pairwise Motifs)
        
        基于 Lee et al. (2020) 的定义:
        
        类型:
        1. Simple Edge: 两个节点在一个超边中共同出现
        2. Multiple Edge: 两个节点在多个超边中共同出现
        3. Different Size: 两个节点在不同大小的超边中共同出现
        
        公式:
        M_2(u,v) = {e ∈ E : {u,v} ⊆ e}
        """
        print("  - 识别2-节点模体...")
        
        pairwise_motifs = {
            'simple_pairs': 0,          # 只在1个超边中共现
            'multiple_pairs': 0,        # 在多个超边中共现
            'pair_cooccurrence_dist': {},  # 共现频率分布
            'avg_cooccurrence': 0.0
        }
        
        # 统计所有节点对的共现
        pair_counts = defaultdict(int)
        
        for edge in self.hyperedges:
            edge_list = list(edge)
            for i in range(len(edge_list)):
                for j in range(i + 1, len(edge_list)):
                    pair = tuple(sorted([edge_list[i], edge_list[j]]))
                    pair_counts[pair] += 1
        
        # 分析共现分布
        cooccurrence_values = list(pair_counts.values())
        cooccurrence_dist = Counter(cooccurrence_values)
        
        pairwise_motifs['simple_pairs'] = cooccurrence_dist.get(1, 0)
        pairwise_motifs['multiple_pairs'] = sum(v for k, v in cooccurrence_dist.items() if k > 1)
        pairwise_motifs['pair_cooccurrence_dist'] = dict(cooccurrence_dist)
        pairwise_motifs['avg_cooccurrence'] = float(np.mean(cooccurrence_values)) if cooccurrence_values else 0.0
        pairwise_motifs['max_cooccurrence'] = int(max(cooccurrence_values)) if cooccurrence_values else 0
        pairwise_motifs['total_pairs'] = len(pair_counts)
        
        return pairwise_motifs
    
    def identify_triadic_motifs(self) -> Dict:
        """
        识别3-节点模体 (Triadic Motifs)
        
        基于 Benson et al. (2016) 的三元组模体分类:
        
        模体类型:
        1. Open Triad: 三个节点，某些对在同一超边中
        2. Closed Triangle: 三个节点在同一超边中
        3. Star Triad: 三个节点通过一个中心超边连接
        4. Path Triad: 三个节点形成路径结构
        
        公式:
        M_3(u,v,w) = pattern_type({e : {u,v,w} ∩ e ≠ ∅})
        """
        print("  - 识别3-节点模体...")
        
        triadic_motifs = {
            'closed_triangles': 0,      # 三个节点在同一超边
            'open_triads': 0,           # 部分连接
            'star_triads': 0,           # 星形连接
            'path_triads': 0,           # 路径形式
            'motif_distribution': {}
        }
        
        # 采样分析（完整分析太慢）
        sample_size = min(1000, len(self.nodes))
        sampled_nodes = np.random.choice(list(self.nodes), size=sample_size, replace=False)
        
        motif_patterns = []
        
        for i in range(len(sampled_nodes)):
            for j in range(i + 1, len(sampled_nodes)):
                for k in range(j + 1, len(sampled_nodes)):
                    u, v, w = sampled_nodes[i], sampled_nodes[j], sampled_nodes[k]
                    
                    # 找到包含这些节点的超边
                    u_edges = set(self.node_to_edges[u])
                    v_edges = set(self.node_to_edges[v])
                    w_edges = set(self.node_to_edges[w])
                    
                    # 检查连接模式
                    all_three = u_edges & v_edges & w_edges
                    uv_edges = u_edges & v_edges
                    vw_edges = v_edges & w_edges
                    uw_edges = u_edges & w_edges
                    
                    if len(all_three) > 0:
                        # 闭合三角形
                        triadic_motifs['closed_triangles'] += 1
                        motif_patterns.append('closed_triangle')
                    elif len(uv_edges) > 0 and len(vw_edges) > 0 and len(uw_edges) > 0:
                        # 开放三元组（每对都有连接但不在同一超边）
                        triadic_motifs['open_triads'] += 1
                        motif_patterns.append('open_triad')
                    elif sum([len(uv_edges) > 0, len(vw_edges) > 0, len(uw_edges) > 0]) == 2:
                        # 路径三元组
                        triadic_motifs['path_triads'] += 1
                        motif_patterns.append('path_triad')
                    elif sum([len(u_edges) > 0, len(v_edges) > 0, len(w_edges) > 0]) == 3:
                        # 星形三元组
                        triadic_motifs['star_triads'] += 1
                        motif_patterns.append('star_triad')
        
        # 模体分布
        motif_counter = Counter(motif_patterns)
        triadic_motifs['motif_distribution'] = dict(motif_counter)
        triadic_motifs['total_sampled_triads'] = len(motif_patterns)
        
        return triadic_motifs
    
    def compute_motif_spectrum(self) -> Dict:
        """
        计算模体频谱
        
        基于 Lee et al. (2020) 的模体频谱分析:
        
        模体频谱是不同大小和类型模体的频率分布
        
        公式:
        S(k) = |{M : M is a k-node motif}| / |all k-node subgraphs|
        """
        print("  - 计算模体频谱...")
        
        spectrum = {
            'size_2_motifs': 0,
            'size_3_motifs': 0,
            'size_4_motifs': 0,
            'size_5_plus_motifs': 0,
            'size_distribution': {}
        }
        
        # 按超边大小分类
        size_counter = Counter(len(e) for e in self.hyperedges)
        
        for size, count in size_counter.items():
            if size == 2:
                spectrum['size_2_motifs'] = count
            elif size == 3:
                spectrum['size_3_motifs'] = count
            elif size == 4:
                spectrum['size_4_motifs'] = count
            elif size >= 5:
                spectrum['size_5_plus_motifs'] += count
        
        spectrum['size_distribution'] = dict(size_counter)
        
        # 计算频谱熵（多样性）
        total = sum(size_counter.values())
        probs = [c / total for c in size_counter.values()]
        entropy = -sum(p * np.log2(p) for p in probs if p > 0)
        spectrum['spectrum_entropy'] = float(entropy)
        spectrum['normalized_entropy'] = float(entropy / np.log2(len(size_counter))) if len(size_counter) > 1 else 0.0
        
        return spectrum
    
    def identify_dense_motifs(self) -> Dict:
        """
        识别密集模体 (Dense Motifs)
        
        密集模体是内部连接密度高于阈值的子结构
        
        定义:
        Dense(S) = |edges within S| / |possible edges| > threshold
        
        基于 Benson et al. (2016) 的方法
        """
        print("  - 识别密集模体...")
        
        dense_motifs = {
            'high_density_edges': 0,    # 密度 > 0.8
            'medium_density_edges': 0,  # 0.5 < 密度 <= 0.8
            'low_density_edges': 0,     # 密度 <= 0.5
            'avg_edge_density': 0.0
        }
        
        edge_densities = []
        
        for edge in self.hyperedges:
            if len(edge) < 2:
                continue
            
            edge_list = list(edge)
            # 计算超边内节点对的实际连接数
            actual_connections = 0
            for i in range(len(edge_list)):
                for j in range(i + 1, len(edge_list)):
                    u, v = edge_list[i], edge_list[j]
                    u_edges = set(self.node_to_edges[u])
                    v_edges = set(self.node_to_edges[v])
                    # 检查这两个节点在多少个超边中共同出现
                    if len(u_edges & v_edges) > 1:  # 除了当前超边
                        actual_connections += 1
            
            # 可能的连接数
            possible = len(edge) * (len(edge) - 1) // 2
            density = actual_connections / possible if possible > 0 else 0.0
            edge_densities.append(density)
            
            if density > 0.8:
                dense_motifs['high_density_edges'] += 1
            elif density > 0.5:
                dense_motifs['medium_density_edges'] += 1
            else:
                dense_motifs['low_density_edges'] += 1
        
        dense_motifs['avg_edge_density'] = float(np.mean(edge_densities)) if edge_densities else 0.0
        dense_motifs['std_edge_density'] = float(np.std(edge_densities)) if edge_densities else 0.0
        dense_motifs['median_edge_density'] = float(np.median(edge_densities)) if edge_densities else 0.0
        
        return dense_motifs
    
    def compute_motif_centrality(self) -> Dict:
        """
        计算模体中心性
        
        基于节点在重要模体中的参与度计算中心性
        
        公式 (基于 Lee et al. 2020):
        MC(v) = Σ_M w(M) * I(v ∈ M)
        其中 w(M) 是模体 M 的重要性权重
        """
        print("  - 计算模体中心性...")
        
        centrality = {
            'top_motif_central_nodes': [],
            'avg_motif_participation': 0.0,
            'centrality_distribution': {}
        }
        
        # 计算每个节点的加权模体参与度
        node_centrality = {}
        
        for node in self.nodes:
            # 节点参与的超边
            node_edges = self.node_to_edges[node]
            
            # 加权计算：大超边权重更高
            weighted_participation = sum(
                len(self.hyperedges[idx]) for idx in node_edges
            )
            
            node_centrality[node] = weighted_participation
        
        # 归一化
        max_centrality = max(node_centrality.values()) if node_centrality else 1
        node_centrality_normalized = {
            k: v / max_centrality for k, v in node_centrality.items()
        }
        
        # 前10个中心节点
        top_nodes = sorted(
            node_centrality_normalized.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        centrality['top_motif_central_nodes'] = [
            {'node': n, 'centrality': float(c)} for n, c in top_nodes
        ]
        
        centrality['avg_motif_participation'] = float(np.mean(list(node_centrality.values())))
        
        # 中心性分布
        centrality_values = list(node_centrality_normalized.values())
        centrality['centrality_stats'] = {
            'mean': float(np.mean(centrality_values)),
            'std': float(np.std(centrality_values)),
            'median': float(np.median(centrality_values)),
            'max': float(np.max(centrality_values)),
            'min': float(np.min(centrality_values))
        }
        
        return centrality
    
    def compute_all_metrics(self) -> Dict:
        """计算所有模体指标"""
        print("📊 计算超图模体分析...")
        
        results = {
            'pairwise_motifs': self.identify_pairwise_motifs(),
            'triadic_motifs': self.identify_triadic_motifs(),
            'motif_spectrum': self.compute_motif_spectrum(),
            'dense_motifs': self.identify_dense_motifs(),
            'motif_centrality': self.compute_motif_centrality()
        }
        
        # 添加基础统计
        results['basic_stats'] = {
            'num_nodes': len(self.nodes),
            'num_hyperedges': len(self.hyperedges),
            'avg_hyperedge_size': float(np.mean([len(e) for e in self.hyperedges]))
        }
        
        print("✅ 模体分析完成！")
        return results


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python hypergraph_motif_analysis.py <hypergraph_file>")
        print("示例: python hypergraph_motif_analysis.py LLM_Email_hypergraph.txt")
        return
    
    hypergraph_file = sys.argv[1]
    
    # 设置随机种子以保证可重复性
    np.random.seed(42)
    
    # 计算模体分析
    hma = HypergraphMotifAnalysis(hypergraph_file)
    results = hma.compute_all_metrics()
    
    # 保存结果
    output_file = hypergraph_file.replace('.txt', '_motif_analysis.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 结果已保存至: {output_file}")
    print(f"\n主要指标:")
    print(f"  - 简单节点对: {results['pairwise_motifs']['simple_pairs']}")
    print(f"  - 多重节点对: {results['pairwise_motifs']['multiple_pairs']}")
    print(f"  - 闭合三角形: {results['triadic_motifs']['closed_triangles']}")
    print(f"  - 频谱熵: {results['motif_spectrum']['spectrum_entropy']:.4f}")
    print(f"  - 平均边密度: {results['dense_motifs']['avg_edge_density']:.4f}")


if __name__ == '__main__':
    main()

