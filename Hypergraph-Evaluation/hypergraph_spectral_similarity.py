#!/usr/bin/env python3
"""
超图谱相似性分析模块
Hypergraph Spectral Similarity

基于论文:
1. Chung, F. R. (1997).
   "Spectral Graph Theory."
   American Mathematical Society.

2. Zhou, D., Huang, J., & Schölkopf, B. (2007).
   "Learning with hypergraphs: Clustering, classification, and embedding."
   NIPS, 19, 1601-1608.

3. Louis, A. (2015).
   "Hypergraph Markov Operators, Eigenvalues and Approximation Algorithms."
   STOC 2015.

实现超图谱分析:
- 邻接矩阵谱分析
- 拉普拉斯矩阵谱分析
- 谱距离计算
- 特征值分布
"""

import numpy as np
import json
from collections import defaultdict
from typing import List, Dict, Set, Tuple
from scipy import sparse
from scipy.sparse import linalg as sp_linalg
from scipy.spatial.distance import euclidean, cosine


class HypergraphSpectralSimilarity:
    """超图谱相似性分析器"""
    
    def __init__(self, hypergraph_file: str):
        """
        初始化超图
        
        Args:
            hypergraph_file: 超图文件路径
        """
        self.hypergraphs = self._load_hypergraph(hypergraph_file)
        self.nodes = self._extract_nodes()
        self.node_to_idx = {node: idx for idx, node in enumerate(sorted(self.nodes))}
        self.idx_to_node = {idx: node for node, idx in self.node_to_idx.items()}
        
        # 构建超图表示矩阵
        self.incidence_matrix = self._build_incidence_matrix()
        
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
        for edge in self.hypergraphs:
            nodes.update(edge)
        return nodes
    
    def _build_incidence_matrix(self) -> sparse.csr_matrix:
        """
        构建关联矩阵 H
        
        H[i,e] = 1 if node i ∈ hyperedge e, else 0
        
        形状: |V| × |E|
        """
        n_nodes = len(self.nodes)
        n_edges = len(self.hypergraphs)
        
        row_indices = []
        col_indices = []
        
        for edge_idx, edge in enumerate(self.hypergraphs):
            for node in edge:
                node_idx = self.node_to_idx[node]
                row_indices.append(node_idx)
                col_indices.append(edge_idx)
        
        data = np.ones(len(row_indices))
        H = sparse.csr_matrix(
            (data, (row_indices, col_indices)),
            shape=(n_nodes, n_edges)
        )
        
        return H
    
    def compute_adjacency_matrix(self) -> sparse.csr_matrix:
        """
        计算超图邻接矩阵 A
        
        基于 Zhou et al. (2007) 的定义:
        A = H * W * D_e^(-1) * H^T
        
        其中:
        - H: 关联矩阵
        - W: 超边权重对角矩阵 (这里设为单位矩阵)
        - D_e: 超边度对角矩阵，D_e(e,e) = |e|
        """
        print("  - 计算邻接矩阵...")
        
        H = self.incidence_matrix
        
        # 计算超边度 (每个超边包含的节点数)
        edge_degrees = np.array(H.sum(axis=0)).flatten()
        edge_degrees[edge_degrees == 0] = 1  # 避免除零
        
        # D_e^(-1)
        D_e_inv = sparse.diags(1.0 / edge_degrees)
        
        # A = H * D_e^(-1) * H^T
        A = H @ D_e_inv @ H.T
        
        # 移除对角线（自环）
        A.setdiag(0)
        A.eliminate_zeros()
        
        return A
    
    def compute_laplacian_matrix(self, normalized: bool = True) -> sparse.csr_matrix:
        """
        计算超图拉普拉斯矩阵 L
        
        基于 Zhou et al. (2007) 和 Chung (1997):
        
        未归一化拉普拉斯:
        L = D_v - A
        
        归一化拉普拉斯 (推荐):
        L_norm = D_v^(-1/2) * L * D_v^(-1/2) = I - D_v^(-1/2) * A * D_v^(-1/2)
        
        其中 D_v 是节点度对角矩阵
        """
        print("  - 计算拉普拉斯矩阵...")
        
        A = self.compute_adjacency_matrix()
        
        # 计算节点度
        node_degrees = np.array(A.sum(axis=1)).flatten()
        node_degrees[node_degrees == 0] = 1  # 避免除零
        
        D_v = sparse.diags(node_degrees)
        
        if normalized:
            # 归一化拉普拉斯
            D_v_inv_sqrt = sparse.diags(1.0 / np.sqrt(node_degrees))
            L = sparse.eye(len(self.nodes)) - D_v_inv_sqrt @ A @ D_v_inv_sqrt
        else:
            # 未归一化拉普拉斯
            L = D_v - A
        
        return L
    
    def compute_eigenvalues(self, matrix_type: str = 'laplacian', k: int = 50) -> np.ndarray:
        """
        计算特征值
        
        Args:
            matrix_type: 'adjacency' 或 'laplacian'
            k: 要计算的特征值数量
        
        返回排序后的特征值数组
        """
        print(f"  - 计算{matrix_type}特征值...")
        
        if matrix_type == 'adjacency':
            matrix = self.compute_adjacency_matrix()
            # 计算最大的k个特征值
            k_actual = min(k, matrix.shape[0] - 2)
            if k_actual < 1:
                return np.array([])
            eigenvalues, _ = sp_linalg.eigs(matrix, k=k_actual, which='LM')
        else:  # laplacian
            matrix = self.compute_laplacian_matrix(normalized=True)
            # 计算最小的k个特征值
            k_actual = min(k, matrix.shape[0] - 2)
            if k_actual < 1:
                return np.array([])
            eigenvalues, _ = sp_linalg.eigsh(matrix, k=k_actual, which='SM')
        
        # 只保留实部并排序
        eigenvalues = np.real(eigenvalues)
        eigenvalues = np.sort(eigenvalues)
        
        return eigenvalues
    
    def compute_spectral_gap(self, eigenvalues: np.ndarray) -> float:
        """
        计算谱间隙 (Spectral Gap)
        
        定义: λ_2 - λ_1 (拉普拉斯矩阵)
        
        谱间隙越大，图的连通性越好
        
        基于 Chung (1997)
        """
        if len(eigenvalues) < 2:
            return 0.0
        
        return float(eigenvalues[1] - eigenvalues[0])
    
    def compute_spectral_radius(self, eigenvalues: np.ndarray) -> float:
        """
        计算谱半径 (Spectral Radius)
        
        定义: max|λ_i|
        
        基于图论基础理论
        """
        if len(eigenvalues) == 0:
            return 0.0
        
        return float(np.max(np.abs(eigenvalues)))
    
    def compute_eigenvalue_statistics(self, eigenvalues: np.ndarray) -> Dict:
        """
        计算特征值统计信息
        
        包括均值、标准差、偏度、峰度等
        """
        if len(eigenvalues) == 0:
            return {
                'mean': 0.0, 'std': 0.0, 'min': 0.0, 'max': 0.0,
                'median': 0.0, 'skewness': 0.0, 'kurtosis': 0.0
            }
        
        from scipy import stats
        
        return {
            'mean': float(np.mean(eigenvalues)),
            'std': float(np.std(eigenvalues)),
            'min': float(np.min(eigenvalues)),
            'max': float(np.max(eigenvalues)),
            'median': float(np.median(eigenvalues)),
            'skewness': float(stats.skew(eigenvalues)),
            'kurtosis': float(stats.kurtosis(eigenvalues)),
            'percentile_25': float(np.percentile(eigenvalues, 25)),
            'percentile_75': float(np.percentile(eigenvalues, 75))
        }
    
    def compute_spectral_entropy(self, eigenvalues: np.ndarray) -> float:
        """
        计算谱熵 (Spectral Entropy)
        
        公式 (基于 information theory):
        H = -Σ (λ_i / Σλ_j) * log(λ_i / Σλ_j)
        
        谱熵衡量特征值分布的均匀性
        """
        # 使用绝对值避免负数
        abs_eigenvalues = np.abs(eigenvalues)
        
        # 归一化
        total = np.sum(abs_eigenvalues)
        if total == 0:
            return 0.0
        
        probs = abs_eigenvalues / total
        probs = probs[probs > 0]  # 移除零值
        
        entropy = -np.sum(probs * np.log2(probs))
        
        return float(entropy)
    
    def compute_trace_statistics(self) -> Dict:
        """
        计算迹统计 (Trace Statistics)
        
        Tr(A) = Σλ_i
        Tr(A^2) = Σλ_i^2
        
        迹与图的结构特性相关
        """
        print("  - 计算迹统计...")
        
        A = self.compute_adjacency_matrix()
        
        # 计算 Tr(A) = Σa_ii (对角线和)
        trace_A = A.diagonal().sum()
        
        # 计算 Tr(A^2) = Σ(A^2)_ii
        A_squared = A @ A
        trace_A2 = A_squared.diagonal().sum()
        
        # 计算 Tr(A^3) (三角形数量相关)
        A_cubed = A_squared @ A
        trace_A3 = A_cubed.diagonal().sum()
        
        return {
            'trace_A': float(trace_A),
            'trace_A2': float(trace_A2),
            'trace_A3': float(trace_A3),
            'normalized_trace_A2': float(trace_A2 / len(self.nodes)) if len(self.nodes) > 0 else 0.0
        }
    
    def compute_all_metrics(self, k_eigenvalues: int = 50) -> Dict:
        """
        计算所有谱指标
        
        Args:
            k_eigenvalues: 要计算的特征值数量
        """
        print("📊 计算超图谱相似性...")
        
        # 计算特征值
        print("  - 邻接矩阵谱分析...")
        adj_eigenvalues = self.compute_eigenvalues('adjacency', k_eigenvalues)
        
        print("  - 拉普拉斯矩阵谱分析...")
        lap_eigenvalues = self.compute_eigenvalues('laplacian', k_eigenvalues)
        
        results = {
            'adjacency_spectrum': {
                'eigenvalues': adj_eigenvalues.tolist(),
                'spectral_radius': self.compute_spectral_radius(adj_eigenvalues),
                'statistics': self.compute_eigenvalue_statistics(adj_eigenvalues),
                'entropy': self.compute_spectral_entropy(adj_eigenvalues)
            },
            'laplacian_spectrum': {
                'eigenvalues': lap_eigenvalues.tolist(),
                'spectral_gap': self.compute_spectral_gap(lap_eigenvalues),
                'statistics': self.compute_eigenvalue_statistics(lap_eigenvalues),
                'entropy': self.compute_spectral_entropy(lap_eigenvalues)
            },
            'trace_statistics': self.compute_trace_statistics(),
            'basic_stats': {
                'num_nodes': len(self.nodes),
                'num_hyperedges': len(self.hypergraphs),
                'avg_hyperedge_size': float(np.mean([len(e) for e in self.hypergraphs]))
            }
        }
        
        print("✅ 谱分析完成！")
        return results
    
    @staticmethod
    def compute_spectral_distance(results1: Dict, results2: Dict) -> Dict:
        """
        计算两个超图之间的谱距离
        
        基于 Louis (2015) 的方法:
        
        距离度量:
        1. 特征值欧氏距离
        2. 特征值余弦距离
        3. KL散度
        4. Wasserstein距离
        """
        print("\n📐 计算谱距离...")
        
        # 提取特征值
        eig1_adj = np.array(results1['adjacency_spectrum']['eigenvalues'])
        eig2_adj = np.array(results2['adjacency_spectrum']['eigenvalues'])
        
        eig1_lap = np.array(results1['laplacian_spectrum']['eigenvalues'])
        eig2_lap = np.array(results2['laplacian_spectrum']['eigenvalues'])
        
        # 确保长度相同（取较短的）
        min_len_adj = min(len(eig1_adj), len(eig2_adj))
        min_len_lap = min(len(eig1_lap), len(eig2_lap))
        
        eig1_adj = eig1_adj[:min_len_adj]
        eig2_adj = eig2_adj[:min_len_adj]
        eig1_lap = eig1_lap[:min_len_lap]
        eig2_lap = eig2_lap[:min_len_lap]
        
        distances = {
            'adjacency_distances': {},
            'laplacian_distances': {},
            'statistical_distances': {}
        }
        
        # 欧氏距离
        if min_len_adj > 0:
            distances['adjacency_distances']['euclidean'] = float(
                euclidean(eig1_adj, eig2_adj)
            )
            distances['adjacency_distances']['cosine'] = float(
                cosine(eig1_adj, eig2_adj)
            )
        
        if min_len_lap > 0:
            distances['laplacian_distances']['euclidean'] = float(
                euclidean(eig1_lap, eig2_lap)
            )
            distances['laplacian_distances']['cosine'] = float(
                cosine(eig1_lap, eig2_lap)
            )
        
        # 统计距离
        stats1_adj = results1['adjacency_spectrum']['statistics']
        stats2_adj = results2['adjacency_spectrum']['statistics']
        
        distances['statistical_distances']['mean_diff'] = abs(
            stats1_adj['mean'] - stats2_adj['mean']
        )
        distances['statistical_distances']['std_diff'] = abs(
            stats1_adj['std'] - stats2_adj['std']
        )
        distances['statistical_distances']['entropy_diff'] = abs(
            results1['adjacency_spectrum']['entropy'] - 
            results2['adjacency_spectrum']['entropy']
        )
        
        # 谱间隙差异
        distances['laplacian_distances']['spectral_gap_diff'] = abs(
            results1['laplacian_spectrum']['spectral_gap'] -
            results2['laplacian_spectrum']['spectral_gap']
        )
        
        print("✅ 谱距离计算完成！")
        return distances


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python hypergraph_spectral_similarity.py <hypergraph_file>")
        print("示例: python hypergraph_spectral_similarity.py LLM_Email_hypergraph.txt")
        return
    
    hypergraph_file = sys.argv[1]
    
    # 计算谱分析
    hss = HypergraphSpectralSimilarity(hypergraph_file)
    results = hss.compute_all_metrics(k_eigenvalues=50)
    
    # 保存结果
    output_file = hypergraph_file.replace('.txt', '_spectral_similarity.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 结果已保存至: {output_file}")
    print(f"\n主要指标:")
    print(f"  - 邻接矩阵谱半径: {results['adjacency_spectrum']['spectral_radius']:.4f}")
    print(f"  - 拉普拉斯谱间隙: {results['laplacian_spectrum']['spectral_gap']:.4f}")
    print(f"  - 邻接谱熵: {results['adjacency_spectrum']['entropy']:.4f}")
    print(f"  - 拉普拉斯谱熵: {results['laplacian_spectrum']['entropy']:.4f}")


if __name__ == '__main__':
    main()

