"""
Ablation: Replace LLM Optimizer with Heuristic Algorithm
Use rule-based heuristics for network optimization
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Hypergraph-Generator'))

from LLM_MAS_Hypergraph_Configuration import *

class HeuristicOptimizerAgent(BaseAgent):
    """Heuristic-based optimizer without LLM"""
    
    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        all_hyperedges = context['all_hyperedges']
        personas = context['personas']
        
        if not all_hyperedges:
            return self._strategy("INCREASE_CONNECTIONS", "Empty network")
        
        # Calculate network metrics
        node_degrees = {}
        for edge in all_hyperedges:
            for node in edge:
                node_degrees[node] = node_degrees.get(node, 0) + 1
        
        total_nodes = len(personas)
        connected_nodes = len(node_degrees)
        connectivity_ratio = connected_nodes / total_nodes if total_nodes > 0 else 0
        
        degrees = list(node_degrees.values())
        avg_degree = sum(degrees) / len(degrees) if degrees else 0
        max_degree = max(degrees) if degrees else 0
        min_degree = min(degrees) if degrees else 0
        
        # Calculate clustering coefficient (simplified)
        edge_sizes = [len(edge) for edge in all_hyperedges]
        avg_edge_size = sum(edge_sizes) / len(edge_sizes) if edge_sizes else 0
        
        # Calculate diversity
        genders = set()
        races = set()
        for node in node_degrees.keys():
            if node in personas:
                genders.add(personas[node]['gender'])
                races.add(personas[node]['race/ethnicity'])
        
        diversity_score = len(genders) + len(races)
        
        # Heuristic decision rules
        score_increase = 0
        score_diversity = 0
        score_reduce = 0
        score_maintain = 0
        
        # Rule 1: Low connectivity -> increase connections
        if connectivity_ratio < 0.3:
            score_increase += 10
        elif connectivity_ratio < 0.5:
            score_increase += 5
        
        # Rule 2: Low average degree -> increase connections
        if avg_degree < 2:
            score_increase += 8
        elif avg_degree < 3:
            score_increase += 4
        
        # Rule 3: High clustering -> reduce
        if max_degree > 10:
            score_reduce += 8
        if avg_edge_size > 5:
            score_reduce += 5
        
        # Rule 4: Low diversity -> enhance diversity
        if diversity_score < 6:
            score_diversity += 10
        elif diversity_score < 10:
            score_diversity += 5
        
        # Rule 5: Degree imbalance -> reduce clustering
        if max_degree > min_degree * 5:
            score_reduce += 6
        
        # Rule 6: Balanced network -> maintain
        if 0.4 <= connectivity_ratio <= 0.7 and 2 <= avg_degree <= 5:
            score_maintain += 10
        
        # Select strategy with highest score
        strategies = [
            (score_increase, "INCREASE_CONNECTIONS"),
            (score_diversity, "ENHANCE_DIVERSITY"),
            (score_reduce, "REDUCE_CLUSTERING"),
            (score_maintain, "MAINTAIN_CURRENT")
        ]
        
        selected_strategy = max(strategies, key=lambda x: x[0])[1]
        
        network_stats = {
            'total_edges': len(all_hyperedges),
            'total_nodes': total_nodes,
            'connected_nodes': connected_nodes,
            'connectivity_ratio': connectivity_ratio,
            'avg_degree': avg_degree,
            'avg_edge_size': avg_edge_size,
            'diversity_score': diversity_score
        }
        
        return self._strategy(selected_strategy, f"Metrics: conn={connectivity_ratio:.2f}, deg={avg_degree:.1f}", network_stats)
    
    def _strategy(self, strategy: str, reasoning: str, stats: Dict = None) -> Dict[str, Any]:
        return {
            'action': 'optimize',
            'agent_id': self.agent_id,
            'strategy': strategy,
            'network_stats': stats or {},
            'reasoning': f"Heuristic: {reasoning}"
        }


class HeuristicOptimizerMAS(ProtectedMASHypergraphGenerator):
    """MAS with heuristic optimizer"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agents['optimizer'] = HeuristicOptimizerAgent('heuristic_optimizer', self.model)
        print("🔧 Optimizer replaced with heuristic algorithm")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ablation: Heuristic Optimizer")
    parser.add_argument("--personas", type=str, required=True)
    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--groups_per_iter", type=int, default=5)
    parser.add_argument("--max_members", type=int, default=5)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--model", type=str, default="gpt-3.5-turbo")
    parser.add_argument("--resume", type=str, default=None)
    
    args = parser.parse_args()
    
    generator = HeuristicOptimizerMAS(
        personas_file=args.personas,
        config_hypergraph_file=args.config,
        output_path=args.output,
        groups_per_iteration=args.groups_per_iter,
        max_members_per_group=args.max_members,
        iterations=args.iterations,
        model=args.model
    )
    
    generator.run(resume_from_dir=args.resume)

