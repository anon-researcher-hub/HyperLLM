"""
Ablation Study 1: Remove Relationship Remover (RemoverAgent)
Disable remover functionality, observe network evolution without removal mechanism
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Hypergraph-Generator'))

from LLM_MAS_Hypergraph_Configuration import *

class NoRemoverMASGenerator(ProtectedMASHypergraphGenerator):
    """MAS hypergraph generator with remover disabled"""
    
    def run_iteration(self, iteration: int) -> Dict[str, Any]:
        """Override iteration method, completely skip remover logic"""
        try:
            print(f"\n🔄 Ablation-NoRemover Iter {iteration + 1}/{self.num_iterations}")
            
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
            
            # 1. Network optimizer agent analysis (keep)
            optimizer_context = {
                'all_hyperedges': self.hyperedges,
                'personas': self.personas,
                'iteration': iteration
            }
            optimizer_decision = self.agents['optimizer'].make_decision(optimizer_context)
            iteration_results['actions'].append(optimizer_decision)
            print(f"📊 Network optimizer suggestion: {optimizer_decision['strategy']}")
            
            # 2. Remover agent - completely disabled
            print("🚫 Ablation: Remover disabled")
            iteration_results['actions'].append({
                'action': 'remove',
                'agent_id': 'remover_disabled',
                'edges_to_remove': [],
                'reasoning': 'Ablation: remover functionality disabled'
            })
            
            # 3. Relationship generator agent (keep original logic)
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
                
                # 4. Review logic (keep)
                if len(generator_decision['selected_members']) > 1:
                    if is_building_phase:
                        self._current_hyperedges = self.hyperedges
                        should_approve = self._lenient_quality_check(generator_decision['selected_members'], self.personas)
                        if should_approve:
                            self.hyperedges.append(generator_decision['selected_members'])
                            print(f"✅ Add edge(NoRemover, size {len(generator_decision['selected_members'])}): {' '.join(generator_decision['selected_members'])}")
                            generated_count += 1
                            self.current_edge_index += 1
                    else:
                        should_approve = self._moderate_llm_review(generator_decision['selected_members'], self.personas, self.hyperedges)
                        if should_approve:
                            self.hyperedges.append(generator_decision['selected_members'])
                            print(f"✅ Add edge(NoRemover, size {len(generator_decision['selected_members'])}): {' '.join(generator_decision['selected_members'])}")
                            generated_count += 1
                            self.current_edge_index += 1
            
            iteration_results['hyperedges_after'] = len(self.hyperedges)
            self.evolution_history.append(iteration_results)
            
            self.save_iteration_snapshot(iteration, iteration_results)
            self.save_checkpoint(iteration)
            
            return iteration_results
            
        except Exception as e:
            print(f"⚠️ Iteration {iteration} exception: {e}")
            raise


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ablation Study 1: MAS Hypergraph Generator without Remover")
    parser.add_argument("--personas", type=str, required=True)
    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--groups_per_iter", type=int, default=5)
    parser.add_argument("--max_members", type=int, default=5)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--model", type=str, default="gpt-3.5-turbo")
    parser.add_argument("--resume", type=str, default=None)
    
    args = parser.parse_args()
    
    generator = NoRemoverMASGenerator(
        personas_file=args.personas,
        config_hypergraph_file=args.config,
        output_path=args.output,
        groups_per_iteration=args.groups_per_iter,
        max_members_per_group=args.max_members,
        iterations=args.iterations,
        model=args.model
    )
    
    generator.run(resume_from_dir=args.resume)

