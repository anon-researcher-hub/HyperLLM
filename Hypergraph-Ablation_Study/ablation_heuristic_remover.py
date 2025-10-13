"""
Ablation: Replace LLM Remover with Heuristic Algorithm
Use rule-based heuristics for edge removal
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Hypergraph-Generator'))

from LLM_MAS_Hypergraph_Configuration import *

class HeuristicRemoverAgent(BaseAgent):
    """Heuristic-based remover without LLM"""
    
    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        all_hyperedges = context['all_hyperedges']
        personas = context['personas']
        iteration = context.get('iteration', 0)
        
        if not all_hyperedges or iteration < 3:
            return {
                'action': 'remove',
                'agent_id': self.agent_id,
                'edges_to_remove': [],
                'reasoning': 'Heuristic: early phase, no removal'
            }
        
        # Calculate node degrees
        node_degrees = {}
        for edge in all_hyperedges:
            for node in edge:
                node_degrees[node] = node_degrees.get(node, 0) + 1
        
        # Score each edge for removal
        edge_scores = []
        for idx, edge in enumerate(all_hyperedges):
            score = 0
            
            # Rule 1: Invalid edges (high priority removal)
            valid_members = [m for m in edge if m in personas]
            if len(valid_members) < 2:
                score -= 1000
                edge_scores.append((idx, score))
                continue
            
            # Rule 2: Redundancy check (overlapping members)
            overlap_count = 0
            for other_edge in all_hyperedges:
                if other_edge == edge:
                    continue
                overlap = len(set(edge) & set(other_edge))
                if overlap >= len(edge) * 0.8:
                    overlap_count += 1
            score -= overlap_count * 5
            
            # Rule 3: Low-degree nodes (prefer keeping)
            avg_degree = sum(node_degrees.get(node, 0) for node in edge) / len(edge)
            score += avg_degree * 2
            
            # Rule 4: Diversity score (prefer diverse edges)
            members_data = [personas[m] for m in valid_members]
            genders = len(set(m['gender'] for m in members_data))
            races = len(set(m['race/ethnicity'] for m in members_data))
            score += (genders + races) * 1.5
            
            # Rule 5: Size penalty (very small or very large)
            if len(edge) < 2 or len(edge) > 8:
                score -= 10
            
            edge_scores.append((idx, score))
        
        # Sort by score (lowest = most likely to remove)
        edge_scores.sort(key=lambda x: x[1])
        
        # Remove bottom 10% or at least 1
        num_to_remove = max(1, len(all_hyperedges) // 10)
        edges_to_remove = [idx for idx, score in edge_scores[:num_to_remove] if score < 0]
        
        return {
            'action': 'remove',
            'agent_id': self.agent_id,
            'edges_to_remove': edges_to_remove[:3],  # Max 3 per iteration
            'reasoning': f'Heuristic: removed {len(edges_to_remove[:3])} low-quality edges'
        }


class HeuristicRemoverMAS(ProtectedMASHypergraphGenerator):
    """MAS with heuristic remover"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agents['remover'] = HeuristicRemoverAgent('heuristic_remover', self.model)
        print("🔧 Remover replaced with heuristic algorithm")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ablation: Heuristic Remover")
    parser.add_argument("--personas", type=str, required=True)
    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--groups_per_iter", type=int, default=5)
    parser.add_argument("--max_members", type=int, default=5)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--model", type=str, default="gpt-3.5-turbo")
    parser.add_argument("--resume", type=str, default=None)
    
    args = parser.parse_args()
    
    generator = HeuristicRemoverMAS(
        personas_file=args.personas,
        config_hypergraph_file=args.config,
        output_path=args.output,
        groups_per_iteration=args.groups_per_iter,
        max_members_per_group=args.max_members,
        iterations=args.iterations,
        model=args.model
    )
    
    generator.run(resume_from_dir=args.resume)

