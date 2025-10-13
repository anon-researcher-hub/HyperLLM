"""
Ablation Study 3: Remove LLM, use statistical methods only
Replace LLM semantic understanding with statistical methods, observe pure statistical approach performance
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Hypergraph-Generator'))

from LLM_MAS_Hypergraph_Configuration import *
import random
from collections import Counter

class StatisticalOnlyGenerator(ProtectedMASHypergraphGenerator):
    """Hypergraph generator using only statistical information (no LLM)"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("🚫 Ablation: LLM disabled, using pure statistical methods")
    
    def _statistical_generate(self, person_id: str, target_size: int) -> List[str]:
        """Statistical relationship generation (replaces LLM generator) - optimized version"""
        node_degrees = {}
        for edge in self.hyperedges:
            for node in edge:
                node_degrees[node] = node_degrees.get(node, 0) + 1
        
        person_data = self.personas[person_id]
        candidates = []
        
        for other_id, other_data in self.personas.items():
            if other_id == person_id:
                continue
            
            similarity_score = 1
            if other_data['gender'] == person_data['gender']:
                similarity_score += 1
            if other_data['race/ethnicity'] == person_data['race/ethnicity']:
                similarity_score += 2
            if abs(int(other_data['age']) - int(person_data['age'])) <= 10:
                similarity_score += 1
            if other_data['religion'] == person_data['religion']:
                similarity_score += 1
            if other_data['political affiliation'] == person_data['political affiliation']:
                similarity_score += 1
            
            degree_weight = node_degrees.get(other_id, 0) + 1
            final_score = similarity_score * degree_weight
            
            candidates.append((other_id, final_score))
        
        if not candidates:
            available = [pid for pid in self.personas.keys() if pid != person_id]
            if len(available) >= target_size - 1:
                selected = random.sample(available, target_size - 1)
            else:
                selected = available
            return [person_id] + selected
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        selected = []
        num_to_select = min(target_size - 1, len(candidates))
        
        num_high_score = max(1, int(num_to_select * 0.8))
        top_candidates = candidates[:min(50, len(candidates))]
        
        weights = [max(1, score) for _, score in top_candidates]
        high_score_selected = []
        for _ in range(num_high_score):
            if not top_candidates:
                break
            chosen_idx = random.choices(range(len(top_candidates)), weights=weights)[0]
            high_score_selected.append(top_candidates[chosen_idx][0])
            top_candidates.pop(chosen_idx)
            weights.pop(chosen_idx)
        
        selected.extend(high_score_selected)
        
        remaining_needed = num_to_select - len(selected)
        if remaining_needed > 0:
            used_ids = set(selected + [person_id])
            available = [cid for cid, _ in candidates if cid not in used_ids]
            if available:
                random_selected = random.sample(available, min(remaining_needed, len(available)))
                selected.extend(random_selected)
        
        return [person_id] + selected
    
    def _statistical_review(self, hyperedge: List[str]) -> bool:
        """Statistical relationship review (replaces LLM reviewer) - very lenient version"""
        if len(hyperedge) < 2:
            return False
        
        valid_count = sum(1 for member in hyperedge if member in self.personas)
        if valid_count < 2:
            return False
        
        if len(set(hyperedge)) < len(hyperedge):
            return False
        
        return True
    
    def _statistical_remove(self, iteration: int) -> List[int]:
        """Statistical relationship removal (replaces LLM remover)"""
        if len(self.hyperedges) < 10 or iteration < 5:
            return []
        
        edge_scores = []
        for idx, edge in enumerate(self.hyperedges):
            if len(edge) < 2:
                edge_scores.append((idx, -100))
                continue
            
            diversity = 0
            valid_members = [m for m in edge if m in self.personas]
            
            if len(valid_members) < 2:
                edge_scores.append((idx, -100))
                continue
            
            ages = [int(self.personas[m]['age']) for m in valid_members]
            age_variance = max(ages) - min(ages)
            
            genders = [self.personas[m]['gender'] for m in valid_members]
            races = [self.personas[m]['race/ethnicity'] for m in valid_members]
            
            diversity = len(set(genders)) + len(set(races)) + (age_variance / 10)
            edge_scores.append((idx, diversity))
        
        edge_scores.sort(key=lambda x: x[1])
        to_remove = [idx for idx, score in edge_scores[:max(1, len(self.hyperedges) // 20)] if score < 0]
        
        return to_remove
    
    def _statistical_remove_for_evolution(self, num_to_remove: int) -> List[int]:
        """Evolution phase removal: remove specified number of low-quality hyperedges"""
        if len(self.hyperedges) == 0 or num_to_remove == 0:
            return []
        
        edge_scores = []
        node_degrees = {}
        
        for edge in self.hyperedges:
            for node in edge:
                node_degrees[node] = node_degrees.get(node, 0) + 1
        
        for idx, edge in enumerate(self.hyperedges):
            if len(edge) < 2:
                edge_scores.append((idx, -1000))
                continue
            
            quality_score = 0
            
            avg_degree = sum(node_degrees.get(node, 0) for node in edge) / len(edge)
            quality_score += avg_degree * 0.3
            
            valid_members = [m for m in edge if m in self.personas]
            if len(valid_members) >= 2:
                ages = [int(self.personas[m]['age']) for m in valid_members]
                genders = [self.personas[m]['gender'] for m in valid_members]
                races = [self.personas[m]['race/ethnicity'] for m in valid_members]
                
                age_variance = max(ages) - min(ages)
                gender_diversity = len(set(genders))
                race_diversity = len(set(races))
                
                quality_score += (gender_diversity + race_diversity * 2 + age_variance / 10) * 0.7
            
            edge_scores.append((idx, quality_score))
        
        edge_scores.sort(key=lambda x: x[1])
        to_remove = [idx for idx, score in edge_scores[:num_to_remove]]
        
        return to_remove
    
    def _statistical_optimize_strategy(self) -> str:
        """Statistical network optimization strategy (replaces LLM optimizer)"""
        if not self.hyperedges:
            return "INCREASE_CONNECTIONS"
        
        node_degrees = {}
        for edge in self.hyperedges:
            for node in edge:
                node_degrees[node] = node_degrees.get(node, 0) + 1
        
        connected_nodes = len(node_degrees)
        total_nodes = len(self.personas)
        connectivity_ratio = connected_nodes / total_nodes if total_nodes > 0 else 0
        
        degrees = list(node_degrees.values())
        avg_degree = sum(degrees) / len(degrees) if degrees else 0
        
        if connectivity_ratio < 0.5:
            return "INCREASE_CONNECTIONS"
        elif avg_degree > 5:
            return "REDUCE_CLUSTERING"
        else:
            return "MAINTAIN_CURRENT"
    
    def run_iteration(self, iteration: int) -> Dict[str, Any]:
        """Iteration using pure statistical methods (no LLM calls) - supports building and evolution phases"""
        try:
            current_edges = len(self.hyperedges)
            
            is_evolution_phase = self.current_edge_index >= len(self.edge_size_sequence)
            
            if is_evolution_phase:
                phase_name = "Evolution-Dynamic Balance"
            else:
                phase_name = "Building-Rapid Generation"
            
            print(f"\n🔄 Ablation-NoLLM(Pure Statistics) Iter {iteration + 1}/{self.num_iterations} [{phase_name}]")
            
            iteration_results = {
                'iteration': iteration,
                'timestamp': datetime.now().isoformat(),
                'actions': [],
                'hyperedges_before': len(self.hyperedges),
                'hyperedges_after': 0,
                'phase': 'evolution' if is_evolution_phase else 'building'
            }
            
            strategy = self._statistical_optimize_strategy()
            print(f"📊 Statistical optimization strategy: {strategy}")
            iteration_results['actions'].append({
                'action': 'optimize',
                'agent_id': 'statistical_optimizer',
                'strategy': strategy,
                'reasoning': 'Optimization decision based on statistical metrics'
            })
            
            if is_evolution_phase:
                print(f"🔄 Evolution phase: Current edges {current_edges}, entering dynamic balance mode")
                
                num_to_remove = min(self.groups_per_iteration, len(self.hyperedges) // 10)
                edges_to_remove = self._statistical_remove_for_evolution(num_to_remove)
                
                removed_count = 0
                for edge_idx in sorted(edges_to_remove, reverse=True):
                    if 0 <= edge_idx < len(self.hyperedges):
                        removed_edge = self.hyperedges.pop(edge_idx)
                        print(f"🗑️ Evolution removal: {' '.join(removed_edge)}")
                        removed_count += 1
                
                print(f"🗑️ Evolution phase removed {removed_count} edges")
                
                iteration_results['actions'].append({
                    'action': 'remove',
                    'agent_id': 'evolution_remover',
                    'edges_to_remove': edges_to_remove,
                    'removed_count': removed_count,
                    'reasoning': 'Evolution phase removes low-quality edges for dynamic balance'
                })
                
                all_persons = list(self.personas.keys())
                generated_count = 0
                target_generate = removed_count
                max_attempts = target_generate * 3
                
                available_sizes = list(self.edge_size_distribution.keys())
                
                print(f"➕ Target generate {target_generate} new edges for balance")
            
            else:
                print(f"🏗️ Building phase: Current edges {current_edges}/{len(self.edge_size_sequence)}, rapid generation...")
                
                iteration_results['actions'].append({
                    'action': 'remove',
                    'agent_id': 'building_no_remove',
                    'edges_to_remove': [],
                    'reasoning': 'Building phase does not remove edges'
                })
                
                all_persons = list(self.personas.keys())
                generated_count = 0
                max_attempts = self.groups_per_iteration * 3
            
            for attempt in range(max_attempts):
                if not is_evolution_phase:
                    if generated_count >= self.groups_per_iteration or self.current_edge_index >= len(self.edge_size_sequence):
                        break
                    target_edge_size = self.edge_size_sequence[self.current_edge_index]
                else:
                    if generated_count >= target_generate:
                        break
                    target_edge_size = random.choice(available_sizes)
                
                if len(self.hyperedges) > 0:
                    node_degrees = {}
                    for edge in self.hyperedges:
                        for node in edge:
                            node_degrees[node] = node_degrees.get(node, 0) + 1
                    
                    if random.random() < 0.8 and node_degrees:
                        nodes_with_degrees = list(node_degrees.items())
                        weights = [degree + 1 for _, degree in nodes_with_degrees]
                        main_person = random.choices([node for node, _ in nodes_with_degrees], weights=weights)[0]
                    else:
                        main_person = random.choice(all_persons)
                else:
                    main_person = random.choice(all_persons)
                
                new_edge = self._statistical_generate(main_person, target_edge_size)
                
                iteration_results['actions'].append({
                    'action': 'generate',
                    'agent_id': 'statistical_generator',
                    'selected_members': new_edge,
                    'reasoning': 'Statistical generation based on similarity and preferential attachment'
                })
                
                if len(new_edge) >= 2 and len(set(new_edge)) == len(new_edge):
                    self.hyperedges.append(new_edge)
                    
                    if is_evolution_phase:
                        print(f"✅ Evolution generated edge(size {len(new_edge)}): {' '.join(new_edge)}")
                    else:
                        print(f"✅ Building generated edge(size {len(new_edge)}): {' '.join(new_edge)}")
                    
                    generated_count += 1
                    
                    if not is_evolution_phase:
                        self.current_edge_index += 1
                    
                    iteration_results['actions'].append({
                        'action': 'review',
                        'agent_id': 'no_review',
                        'hyperedge': new_edge,
                        'decision': 'APPROVE',
                        'reasoning': 'No review, direct approval',
                        'phase': 'evolution' if is_evolution_phase else 'building'
                    })
            
            iteration_results['hyperedges_after'] = len(self.hyperedges)
            iteration_results['generated_count'] = generated_count
            self.evolution_history.append(iteration_results)
            
            if is_evolution_phase:
                print(f"📈 Evolution iteration complete: {iteration_results['hyperedges_before']} → {iteration_results['hyperedges_after']} edges")
                print(f"   Removed: {removed_count}, Added: {generated_count}, Net change: {iteration_results['hyperedges_after'] - iteration_results['hyperedges_before']}")
            else:
                progress_percent = (self.current_edge_index / len(self.edge_size_sequence)) * 100 if len(self.edge_size_sequence) > 0 else 0
                print(f"📈 Building iteration complete: {iteration_results['hyperedges_before']} → {iteration_results['hyperedges_after']} edges (progress: {progress_percent:.1f}%)")
            
            self.save_iteration_snapshot(iteration, iteration_results)
            self.save_checkpoint(iteration)
            
            return iteration_results
            
        except Exception as e:
            print(f"⚠️ Iteration {iteration} exception: {e}")
            raise


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ablation Study 3: Pure Statistical Hypergraph Generator without LLM")
    parser.add_argument("--personas", type=str, required=True)
    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--groups_per_iter", type=int, default=5)
    parser.add_argument("--max_members", type=int, default=5)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--model", type=str, default="gpt-3.5-turbo")
    parser.add_argument("--resume", type=str, default=None)
    
    args = parser.parse_args()
    
    generator = StatisticalOnlyGenerator(
        personas_file=args.personas,
        config_hypergraph_file=args.config,
        output_path=args.output,
        groups_per_iteration=args.groups_per_iter,
        max_members_per_group=args.max_members,
        iterations=args.iterations,
        model=args.model
    )
    
    generator.run(resume_from_dir=args.resume)

