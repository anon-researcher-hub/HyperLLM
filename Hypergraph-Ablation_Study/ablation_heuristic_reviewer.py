"""
Ablation: Replace LLM Reviewer with Heuristic Algorithm
Use rule-based heuristics for edge review
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Hypergraph-Generator'))

from LLM_MAS_Hypergraph_Configuration import *

class HeuristicReviewerAgent(BaseAgent):
    """Heuristic-based reviewer without LLM"""
    
    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        hyperedge = context['hyperedge']
        personas = context['personas']
        
        # Rule 1: Basic validation
        if len(hyperedge) < 2:
            return self._reject("Too few members")
        
        if len(set(hyperedge)) < len(hyperedge):
            return self._reject("Duplicate members")
        
        # Rule 2: Check member validity
        valid_count = sum(1 for m in hyperedge if m in personas)
        if valid_count < len(hyperedge):
            return self._reject("Invalid member IDs")
        
        # Rule 3: Diversity check (not too homogeneous)
        members_data = [personas[m] for m in hyperedge if m in personas]
        genders = set(m['gender'] for m in members_data)
        races = set(m['race/ethnicity'] for m in members_data)
        
        diversity_score = len(genders) + len(races)
        
        # Rule 4: Age range check (not too extreme)
        ages = [int(m['age']) for m in members_data]
        age_range = max(ages) - min(ages)
        
        # Heuristic scoring
        score = 0
        score += diversity_score * 2
        
        if age_range < 50:  # Reasonable age range
            score += 3
        
        if len(hyperedge) >= 2 and len(hyperedge) <= 6:
            score += 2
        
        # Decision threshold
        if score >= 5:
            return self._approve("Heuristic score acceptable")
        else:
            return self._reject("Heuristic score too low")
    
    def _approve(self, reason: str) -> Dict[str, Any]:
        return {
            'action': 'review',
            'agent_id': self.agent_id,
            'decision': 'APPROVE',
            'reasoning': f"Heuristic: {reason}"
        }
    
    def _reject(self, reason: str) -> Dict[str, Any]:
        return {
            'action': 'review',
            'agent_id': self.agent_id,
            'decision': 'REJECT',
            'reasoning': f"Heuristic: {reason}"
        }


class HeuristicReviewerMAS(ProtectedMASHypergraphGenerator):
    """MAS with heuristic reviewer"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agents['reviewer'] = HeuristicReviewerAgent('heuristic_reviewer', self.model)
        print("🔧 Reviewer replaced with heuristic algorithm")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ablation: Heuristic Reviewer")
    parser.add_argument("--personas", type=str, required=True)
    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--groups_per_iter", type=int, default=5)
    parser.add_argument("--max_members", type=int, default=5)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--model", type=str, default="gpt-3.5-turbo")
    parser.add_argument("--resume", type=str, default=None)
    
    args = parser.parse_args()
    
    generator = HeuristicReviewerMAS(
        personas_file=args.personas,
        config_hypergraph_file=args.config,
        output_path=args.output,
        groups_per_iteration=args.groups_per_iter,
        max_members_per_group=args.max_members,
        iterations=args.iterations,
        model=args.model
    )
    
    generator.run(resume_from_dir=args.resume)

