#!/usr/bin/env python3

import numpy as np
import json
from collections import defaultdict, Counter
from itertools import combinations
from typing import List, Dict, Set, Tuple


class HypergraphStructuralCounts:

    
    def __init__(self, hypergraph_file: str):

        self.hyperedges = self._load_hypergraph(hypergraph_file)
        self.nodes = self._extract_nodes()
        self.node_to_edges = self._build_node_edge_mapping()
        
    def _load_hypergraph(self, file_path: str) -> List[Set[str]]:

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
    
    def count_wedges(self) -> Dict:
        """
        计算楔形结构 (Wedge)
        
        定义: 楔形是两个相交的超边，共享至少一个节点
        
        公式 (基于 Benson et al. 2018):
        W = Σ_{e1,e2} I(|e1 ∩ e2| >= 1 ∧ e1 ≠ e2)
        
        分类:
        - k-wedge: 两个超边共享 k 个节点
        - 节点楔形: 通过特定节点连接的楔形对数
        """
        print("  - 计算楔形结构 (Wedge)...")
        
        wedge_counts = {
            'total_wedges': 0,
            'wedges_by_intersection_size': defaultdict(int),
            'node_wedge_counts': {},
            'avg_wedges_per_node': 0.0
        }
        
        # 计算所有超边对的交集
        num_edges = len(self.hyperedges)
        for i in range(num_edges):
            for j in range(i + 1, num_edges):
                intersection = self.hyperedges[i] & self.hyperedges[j]
                intersection_size = len(intersection)
                
                if intersection_size > 0:
                    wedge_counts['total_wedges'] += 1
                    wedge_counts['wedges_by_intersection_size'][intersection_size] += 1
        
        # 计算每个节点参与的楔形数
        for node in self.nodes:
            node_edges = self.node_to_edges[node]
            # 该节点参与的楔形数 = C(度数, 2)
            degree = len(node_edges)
            node_wedges = degree * (degree - 1) // 2
            wedge_counts['node_wedge_counts'][node] = node_wedges
        
        wedge_counts['avg_wedges_per_node'] = np.mean(
            list(wedge_counts['node_wedge_counts'].values())
        ) if wedge_counts['node_wedge_counts'] else 0.0
        
        return dict(wedge_counts)
    
    def count_claws(self) -> Dict:
        """
        计算爪形结构 (Claw)
        
        定义: 爪形是一个中心节点连接多个超边的星形结构
        
        公式 (基于 Lee et al. 2020):
        Claw_k(v) = C(deg(v), k) 其中 deg(v) 是节点 v 的度数
        
        k-claw: 中心节点连接 k 个超边
        """
        print("  - 计算爪形结构 (Claw)...")
        
        claw_counts = {
            'node_degrees': {},
            'degree_distribution': {},
            'claw_3': 0,  # 3-爪 (最常见)
            'claw_4': 0,  # 4-爪
            'claw_5_plus': 0,  # 5+爪
            'max_claw_size': 0
        }
        
        # 计算每个节点的度数分布
        degree_list = []
        for node in self.nodes:
            degree = len(self.node_to_edges[node])
            claw_counts['node_degrees'][node] = degree
            degree_list.append(degree)
            
            # 计算不同大小的爪形
            if degree >= 3:
                claw_counts['claw_3'] += self._binomial(degree, 3)
            if degree >= 4:
                claw_counts['claw_4'] += self._binomial(degree, 4)
            if degree >= 5:
                claw_counts['claw_5_plus'] += sum(
                    self._binomial(degree, k) for k in range(5, degree + 1)
                )
        
        # 度分布统计
        degree_counter = Counter(degree_list)
        claw_counts['degree_distribution'] = dict(degree_counter)
        claw_counts['max_claw_size'] = max(degree_list) if degree_list else 0
        claw_counts['avg_degree'] = float(np.mean(degree_list)) if degree_list else 0.0
        claw_counts['std_degree'] = float(np.std(degree_list)) if degree_list else 0.0
        
        return claw_counts
    
    def _binomial(self, n: int, k: int) -> int:
        """计算二项式系数 C(n, k)"""
        if k > n or k < 0:
            return 0
        if k == 0 or k == n:
            return 1
        
        # 优化计算
        k = min(k, n - k)
        result = 1
        for i in range(k):
            result = result * (n - i) // (i + 1)
        return result
    
    def count_triangles(self, max_samples=1000000) -> Dict:
        """
        计算三角形闭包结构
        
        定义: 三个超边通过共享节点形成的闭合三角形
        
        基于 Benson et al. (2018) 的简单复形闭包理论:
        Triangle = {(e1, e2, e3): e1 ∩ e2 ≠ ∅, e2 ∩ e3 ≠ ∅, e1 ∩ e3 ≠ ∅}
        
        Args:
            max_samples: 最大检查三元组数量，避免内存溢出（默认100万）
        """
        print("  - 计算三角形闭包结构...")
        
        triangle_counts = {
            'total_triangles': 0,
            'complete_triangles': 0,  # 三个超边两两相交
            'partial_triangles': 0,   # 部分相交
            'avg_triangle_size': 0.0,
            'sampled': False
        }
        
        num_edges = len(self.hyperedges)
        
        # 使用在线算法计算平均值，避免存储所有数据
        triangle_size_sum = 0
        triangle_size_count = 0
        
        # 计算总组合数
        total_combinations = num_edges * (num_edges - 1) * (num_edges - 2) // 6
        
        # 如果组合数太大，使用采样
        if total_combinations > max_samples:
            import random
            print(f"    ⚠️  超边数量较大 ({num_edges}条)，总组合数: {total_combinations:,}")
            print(f"    使用采样方法 (采样 {max_samples:,} 个三元组)...")
            triangle_counts['sampled'] = True
            
            sampled = 0
            while sampled < max_samples:
                # 随机采样三个不同的超边
                i, j, k = sorted(random.sample(range(num_edges), 3))
                e1, e2, e3 = self.hyperedges[i], self.hyperedges[j], self.hyperedges[k]
                
                # 检查三个超边的交集情况
                int_12 = len(e1 & e2)
                int_23 = len(e2 & e3)
                int_13 = len(e1 & e3)
                
                if int_12 > 0 and int_23 > 0 and int_13 > 0:
                    triangle_counts['total_triangles'] += 1
                    
                    # 检查是否为完全三角形
                    common = e1 & e2 & e3
                    if len(common) > 0:
                        triangle_counts['complete_triangles'] += 1
                    else:
                        triangle_counts['partial_triangles'] += 1
                    
                    # 在线计算平均大小
                    union_size = len(e1 | e2 | e3)
                    triangle_size_sum += union_size
                    triangle_size_count += 1
                
                sampled += 1
                if sampled % 100000 == 0:
                    print(f"    已采样 {sampled:,} / {max_samples:,} 个三元组...")
            
            # 根据采样比例估算总数
            sampling_ratio = max_samples / total_combinations
            triangle_counts['total_triangles'] = int(triangle_counts['total_triangles'] / sampling_ratio)
            triangle_counts['complete_triangles'] = int(triangle_counts['complete_triangles'] / sampling_ratio)
            triangle_counts['partial_triangles'] = int(triangle_counts['partial_triangles'] / sampling_ratio)
            print(f"    📊 采样完成，估算总三角形数: {triangle_counts['total_triangles']:,}")
            
        else:
            # 完整计算（小规模超图）
            print(f"    超边数量: {num_edges}，完整计算所有 {total_combinations:,} 个三元组...")
            count = 0
            for i in range(num_edges):
                for j in range(i + 1, num_edges):
                    for k in range(j + 1, num_edges):
                        e1, e2, e3 = self.hyperedges[i], self.hyperedges[j], self.hyperedges[k]
                        
                        # 检查三个超边的交集情况
                        int_12 = len(e1 & e2)
                        int_23 = len(e2 & e3)
                        int_13 = len(e1 & e3)
                        
                        if int_12 > 0 and int_23 > 0 and int_13 > 0:
                            triangle_counts['total_triangles'] += 1
                            
                            # 检查是否为完全三角形
                            common = e1 & e2 & e3
                            if len(common) > 0:
                                triangle_counts['complete_triangles'] += 1
                            else:
                                triangle_counts['partial_triangles'] += 1
                            
                            # 在线计算平均大小（不存储列表）
                            union_size = len(e1 | e2 | e3)
                            triangle_size_sum += union_size
                            triangle_size_count += 1
                        
                        count += 1
                        if count % 100000 == 0:
                            print(f"    已检查 {count:,} / {total_combinations:,} 个三元组...")
        
        # 计算平均三角形大小
        if triangle_size_count > 0:
            triangle_counts['avg_triangle_size'] = float(triangle_size_sum / triangle_size_count)
        
        print(f"    ✅ 完成！发现 {triangle_counts['total_triangles']:,} 个三角形模式")
        
        return triangle_counts
    
    def count_star_patterns(self) -> Dict:
        """
        计算星形模式
        
        定义: 星形模式是多个超边通过单个中心节点连接
        
        基于节点度中心性的星形模式分类:
        - Low-degree stars: degree <= 5
        - Medium-degree stars: 5 < degree <= 20
        - High-degree stars: degree > 20
        """
        print("  - 计算星形模式...")
        
        star_patterns = {
            'low_degree_stars': 0,    # 度 <= 5
            'medium_degree_stars': 0,  # 5 < 度 <= 20
            'high_degree_stars': 0,    # 度 > 20
            'hub_nodes': [],           # 高度节点列表
            'star_pattern_distribution': {}
        }
        
        degree_categories = defaultdict(int)
        
        for node in self.nodes:
            degree = len(self.node_to_edges[node])
            
            if degree <= 5:
                star_patterns['low_degree_stars'] += 1
                degree_categories['low'] += 1
            elif degree <= 20:
                star_patterns['medium_degree_stars'] += 1
                degree_categories['medium'] += 1
            else:
                star_patterns['high_degree_stars'] += 1
                degree_categories['high'] += 1
                star_patterns['hub_nodes'].append({
                    'node': node,
                    'degree': degree
                })
        
        # 按度数排序hub节点
        star_patterns['hub_nodes'] = sorted(
            star_patterns['hub_nodes'],
            key=lambda x: x['degree'],
            reverse=True
        )[:10]  # 只保留前10个
        
        star_patterns['star_pattern_distribution'] = dict(degree_categories)
        
        return star_patterns
    
    def compute_structural_diversity(self) -> Dict:
        """
        计算结构多样性指标
        
        基于超边大小和节点度的分布熵来衡量结构多样性
        
        Shannon熵公式:
        H = -Σ p_i * log(p_i)
        """
        print("  - 计算结构多样性...")
        
        # 超边大小分布熵
        size_distribution = Counter(len(e) for e in self.hyperedges)
        total_edges = len(self.hyperedges)
        size_probs = {k: v / total_edges for k, v in size_distribution.items()}
        size_entropy = -sum(p * np.log2(p) for p in size_probs.values() if p > 0)
        
        # 节点度分布熵
        degree_distribution = Counter(len(self.node_to_edges[n]) for n in self.nodes)
        total_nodes = len(self.nodes)
        degree_probs = {k: v / total_nodes for k, v in degree_distribution.items()}
        degree_entropy = -sum(p * np.log2(p) for p in degree_probs.values() if p > 0)
        
        return {
            'hyperedge_size_entropy': float(size_entropy),
            'node_degree_entropy': float(degree_entropy),
            'size_distribution': dict(size_distribution),
            'degree_distribution': dict(degree_distribution),
            'normalized_size_entropy': float(size_entropy / np.log2(len(size_distribution))) if len(size_distribution) > 1 else 0.0,
            'normalized_degree_entropy': float(degree_entropy / np.log2(len(degree_distribution))) if len(degree_distribution) > 1 else 0.0
        }
    
    def compute_all_metrics(self) -> Dict:
        """计算所有结构计数指标"""
        print("📊 计算超图结构计数...")
        
        results = {
            'wedge_counts': self.count_wedges(),
            'claw_counts': self.count_claws(),
            'triangle_counts': self.count_triangles(),
            'star_patterns': self.count_star_patterns(),
            'structural_diversity': self.compute_structural_diversity()
        }
        
        # 添加基础统计
        results['basic_stats'] = {
            'num_nodes': len(self.nodes),
            'num_hyperedges': len(self.hyperedges),
            'avg_hyperedge_size': float(np.mean([len(e) for e in self.hyperedges]))
        }
        
        print("✅ 结构计数完成！")
        return results


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python hypergraph_structural_counts.py <hypergraph_file>")
        print("示例: python hypergraph_structural_counts.py LLM_Email_hypergraph.txt")
        return
    
    hypergraph_file = sys.argv[1]
    
    # 计算结构计数
    hsc = HypergraphStructuralCounts(hypergraph_file)
    results = hsc.compute_all_metrics()
    
    # 保存结果
    output_file = hypergraph_file.replace('.txt', '_structural_counts.json')
    
    # 移除大型数据以减小文件大小
    save_results = results.copy()
    if 'node_wedge_counts' in save_results.get('wedge_counts', {}):
        del save_results['wedge_counts']['node_wedge_counts']
    if 'node_degrees' in save_results.get('claw_counts', {}):
        del save_results['claw_counts']['node_degrees']
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(save_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 结果已保存至: {output_file}")
    print(f"\n主要指标:")
    print(f"  - 总楔形数: {results['wedge_counts']['total_wedges']}")
    print(f"  - 3-爪数量: {results['claw_counts']['claw_3']}")
    print(f"  - 三角形总数: {results['triangle_counts']['total_triangles']}")
    print(f"  - 高度中心节点数: {results['star_patterns']['high_degree_stars']}")


if __name__ == '__main__':
    main()

