"""
Ablation: Remove ReviewerAgent
Direct approve all generated edges without LLM review
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Hypergraph-Generator'))

from LLM_MAS_Hypergraph_Configuration import *

class NoReviewerMASGenerator(ProtectedMASHypergraphGenerator):
    """MAS generator with reviewer disabled"""
    
    def run_iteration(self, iteration: int) -> Dict[str, Any]:
        """Override iteration: skip reviewer logic"""
        try:
            print(f"\n🔄 Ablation-NoReviewer Iteration {iteration + 1}/{self.num_iterations}")
            
            iteration_results = {
                'iteration': iteration,
                'timestamp': datetime.now().isoformat(),
                'actions': [],
                'hyperedges_before': len(self.hyperedges),
                'hyperedges_after': 0
            }
            
            current_edges = len(self.hyperedges)
            target_base_edges = max(30, self.total_groups // 2) 
            is_building_phase = current_edges < target_base_edges or iteration < 8
            
            # 1. Optimizer agent (keep)
            optimizer_context = {
                'all_hyperedges': self.hyperedges,
                'personas': self.personas,
                'iteration': iteration
            }
            optimizer_decision = self.agents['optimizer'].make_decision(optimizer_context)
            iteration_results['actions'].append(optimizer_decision)
            print(f"📊 Optimizer strategy: {optimizer_decision['strategy']}")
            
            # 2. Remover agent (keep)
            if not is_building_phase and iteration >= 8 and current_edges > target_base_edges * 1.5:
                remover_context = {
                    'all_hyperedges': self.hyperedges,
                    'personas': self.personas,
                    'iteration': iteration
                }
                remover_decision = self.agents['remover'].make_decision(remover_context)
                iteration_results['actions'].append(remover_decision)
                
                edges_to_remove = sorted(remover_decision['edges_to_remove'], reverse=True)[:2]
                for edge_idx in edges_to_remove:
                    if 0 <= edge_idx < len(self.hyperedges):
                        removed_edge = self.hyperedges.pop(edge_idx)
                        print(f"🗑️ Remove edge: {' '.join(removed_edge)}")
            
            # 3. Generator agent (keep)
            all_persons = list(self.personas.keys())
            generated_count = 0
            max_attempts = self.groups_per_iteration * 5 if is_building_phase else self.groups_per_iteration * 2
            
            for attempt in range(max_attempts):
                if generated_count >= self.groups_per_iteration or self.current_edge_index >= len(self.edge_size_sequence):
                    break
                    
                target_edge_size = self.edge_size_sequence[self.current_edge_index]
                
                if is_building_phase and len(self.hyperedges) > 0:
                    node_degrees = {}
                    for edge in self.hyperedges:
                        for node in edge:
                            node_degrees[node] = node_degrees.get(node, 0) + 1
                    
                    if random.random() < 0.85 and node_degrees:
                        nodes_with_degrees = list(node_degrees.items())
                        weights = [degree + 1 for _, degree in nodes_with_degrees]
                        main_person = random.choices([node for node, _ in nodes_with_degrees], weights=weights)[0]
                    else:
                        main_person = random.choice(all_persons)
                else:
                    main_person = random.choice(all_persons)
                
                generator_context = {
                    'person_id': main_person,
                    'person_data': self.personas[main_person],
                    'existing_hyperedges': self.hyperedges,
                    'personas': self.personas,
                    'max_members': self.max_members_per_group,
                    'target_edge_size': target_edge_size,
                    'is_building_phase': is_building_phase,
                    'current_iteration': iteration
                }
                
                generator_decision = self.agents['generator'].make_decision(generator_context)
                iteration_results['actions'].append(generator_decision)
                
                # 4. Reviewer disabled - direct approve
                if len(generator_decision['selected_members']) > 1:
                    print("🚫 Ablation: Reviewer disabled, direct approve")
                    self.hyperedges.append(generator_decision['selected_members'])
                    print(f"✅ Add edge(NoReviewer, size{len(generator_decision['selected_members'])}): {' '.join(generator_decision['selected_members'])}")
                    generated_count += 1
                    self.current_edge_index += 1
                    
                    iteration_results['actions'].append({
                        'action': 'review',
                        'agent_id': 'reviewer_disabled',
                        'decision': 'APPROVE',
                        'reasoning': 'Ablation: reviewer disabled'
                    })
            
            iteration_results['hyperedges_after'] = len(self.hyperedges)
            self.evolution_history.append(iteration_results)
            
            self.save_iteration_snapshot(iteration, iteration_results)
            self.save_checkpoint(iteration)
            
            return iteration_results
            
        except Exception as e:
            print(f"⚠️ Iteration {iteration} error: {e}")
            raise


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ablation: NoReviewer MAS Generator")
    parser.add_argument("--personas", type=str, required=True)
    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--groups_per_iter", type=int, default=5)
    parser.add_argument("--max_members", type=int, default=5)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--model", type=str, default="gpt-3.5-turbo")
    parser.add_argument("--resume", type=str, default=None)
    
    args = parser.parse_args()
    
    generator = NoReviewerMASGenerator(
        personas_file=args.personas,
        config_hypergraph_file=args.config,
        output_path=args.output,
        groups_per_iteration=args.groups_per_iter,
        max_members_per_group=args.max_members,
        iterations=args.iterations,
        model=args.model
    )
    
    generator.run(resume_from_dir=args.resume)

