"""
Ablation: Replace LLM Generator with Heuristic Algorithm
Use rule-based heuristics for edge generation
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Hypergraph-Generator'))

from LLM_MAS_Hypergraph_Configuration import *

class HeuristicGeneratorAgent(BaseAgent):
    """Heuristic-based generator without LLM"""
    
    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        person_id = context['person_id']
        person_data = context['person_data']
        existing_hyperedges = context['existing_hyperedges']
        personas = context['personas']
        target_size = context.get('target_edge_size', 3)
        
        # Calculate node degrees for preferential attachment
        node_degrees = {}
        for edge in existing_hyperedges:
            for node in edge:
                node_degrees[node] = node_degrees.get(node, 0) + 1
        
        # Heuristic scoring for candidates
        candidates = []
        for other_id, other_data in personas.items():
            if other_id == person_id:
                continue
            
            score = 0
            
            # Feature similarity (moderate weight)
            if other_data['gender'] == person_data['gender']:
                score += 2
            if other_data['race/ethnicity'] == person_data['race/ethnicity']:
                score += 3
            if abs(int(other_data['age']) - int(person_data['age'])) <= 10:
                score += 2
            if other_data['religion'] == person_data['religion']:
                score += 2
            if other_data['political affiliation'] == person_data['political affiliation']:
                score += 2
            
            # Preferential attachment (strong weight)
            degree_score = node_degrees.get(other_id, 0)
            score += degree_score * 3
            
            # Diversity bonus (weak weight)
            if other_data['gender'] != person_data['gender']:
                score += 1
            
            candidates.append((other_id, score))
        
        # Weighted random selection from top candidates
        candidates.sort(key=lambda x: x[1], reverse=True)
        top_k = min(len(candidates), max(10, target_size * 3))
        top_candidates = candidates[:top_k]
        
        selected = []
        weights = [max(1, score) for _, score in top_candidates]
        
        for _ in range(min(target_size - 1, len(top_candidates))):
            if not top_candidates:
                break
            idx = random.choices(range(len(top_candidates)), weights=weights)[0]
            selected.append(top_candidates[idx][0])
            top_candidates.pop(idx)
            weights.pop(idx)
        
        return {
            'action': 'generate',
            'agent_id': self.agent_id,
            'person_id': person_id,
            'selected_members': [person_id] + selected,
            'reasoning': 'Heuristic: similarity + preferential attachment',
            'phase': 'heuristic'
        }


class HeuristicGeneratorMAS(ProtectedMASHypergraphGenerator):
    """MAS with heuristic generator"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agents['generator'] = HeuristicGeneratorAgent('heuristic_generator', self.model)
        print("🔧 Generator replaced with heuristic algorithm")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ablation: Heuristic Generator")
    parser.add_argument("--personas", type=str, required=True)
    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--groups_per_iter", type=int, default=5)
    parser.add_argument("--max_members", type=int, default=5)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--model", type=str, default="gpt-3.5-turbo")
    parser.add_argument("--resume", type=str, default=None)
    
    args = parser.parse_args()
    
    generator = HeuristicGeneratorMAS(
        personas_file=args.personas,
        config_hypergraph_file=args.config,
        output_path=args.output,
        groups_per_iteration=args.groups_per_iter,
        max_members_per_group=args.max_members,
        iterations=args.iterations,
        model=args.model
    )
    
    generator.run(resume_from_dir=args.resume)

