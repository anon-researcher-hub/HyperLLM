"""
Visualization utilities for hypergraph GUI
Provides real-time plotting and analysis
"""

import json
from collections import Counter
from pathlib import Path


class HypergraphStats:
    """Calculate and format hypergraph statistics"""
    
    def __init__(self, hypergraph_file):
        """Load hypergraph from file"""
        self.hypergraph_file = hypergraph_file
        self.hyperedges = []
        self._load_hypergraph()
    
    def _load_hypergraph(self):
        """Load hyperedges from file"""
        try:
            with open(self.hypergraph_file, 'r') as f:
                for line in f:
                    nodes = line.strip().split()
                    if nodes:
                        self.hyperedges.append(nodes)
        except Exception as e:
            print(f"Error loading hypergraph: {e}")
    
    def get_basic_stats(self):
        """Calculate basic statistics"""
        if not self.hyperedges:
            return {
                'num_hyperedges': 0,
                'num_nodes': 0,
                'avg_hyperedge_size': 0,
                'min_size': 0,
                'max_size': 0
            }
        
        # Count unique nodes
        all_nodes = set()
        for edge in self.hyperedges:
            all_nodes.update(edge)
        
        # Calculate sizes
        sizes = [len(edge) for edge in self.hyperedges]
        
        return {
            'num_hyperedges': len(self.hyperedges),
            'num_nodes': len(all_nodes),
            'avg_hyperedge_size': sum(sizes) / len(sizes),
            'min_size': min(sizes),
            'max_size': max(sizes)
        }
    
    def get_size_distribution(self):
        """Get hyperedge size distribution"""
        sizes = [len(edge) for edge in self.hyperedges]
        return dict(Counter(sizes))
    
    def get_node_degrees(self):
        """Calculate node degree distribution"""
        node_degrees = {}
        for edge in self.hyperedges:
            for node in edge:
                node_degrees[node] = node_degrees.get(node, 0) + 1
        
        degree_distribution = Counter(node_degrees.values())
        return dict(degree_distribution)
    
    def format_stats_text(self):
        """Format statistics as readable text"""
        stats = self.get_basic_stats()
        size_dist = self.get_size_distribution()
        
        text = "=== Hypergraph Statistics ===\n\n"
        text += f"Number of Hyperedges: {stats['num_hyperedges']}\n"
        text += f"Number of Nodes: {stats['num_nodes']}\n"
        text += f"Average Hyperedge Size: {stats['avg_hyperedge_size']:.2f}\n"
        text += f"Min/Max Size: {stats['min_size']} / {stats['max_size']}\n\n"
        
        text += "=== Size Distribution ===\n"
        for size in sorted(size_dist.keys()):
            count = size_dist[size]
            percentage = (count / stats['num_hyperedges']) * 100
            text += f"Size {size}: {count} ({percentage:.1f}%)\n"
        
        return text


class PersonasLoader:
    """Load and display persona information"""
    
    def __init__(self, personas_file):
        """Load personas from JSON file"""
        self.personas_file = personas_file
        self.personas = {}
        self._load_personas()
    
    def _load_personas(self):
        """Load personas from file"""
        try:
            with open(self.personas_file, 'r', encoding='utf-8') as f:
                self.personas = json.load(f)
        except Exception as e:
            print(f"Error loading personas: {e}")
    
    def get_persona_info(self, node_id):
        """Get information for a specific persona"""
        if node_id in self.personas:
            return self.personas[node_id]
        return None
    
    def get_demographics_summary(self):
        """Get summary of demographics"""
        if not self.personas:
            return "No personas loaded"
        
        gender_count = Counter()
        race_count = Counter()
        age_ranges = {'18-30': 0, '31-50': 0, '51-70': 0, '70+': 0}
        
        for persona_id, persona in self.personas.items():
            gender_count[persona.get('gender', 'unknown')] += 1
            race_count[persona.get('race/ethnicity', 'unknown')] += 1
            
            age = persona.get('age', 0)
            if isinstance(age, str):
                try:
                    age = int(age)
                except:
                    age = 0
            
            if 18 <= age <= 30:
                age_ranges['18-30'] += 1
            elif 31 <= age <= 50:
                age_ranges['31-50'] += 1
            elif 51 <= age <= 70:
                age_ranges['51-70'] += 1
            elif age > 70:
                age_ranges['70+'] += 1
        
        text = "=== Demographics Summary ===\n\n"
        text += f"Total Personas: {len(self.personas)}\n\n"
        
        text += "Gender Distribution:\n"
        for gender, count in gender_count.most_common():
            percentage = (count / len(self.personas)) * 100
            text += f"  {gender}: {count} ({percentage:.1f}%)\n"
        
        text += "\nRace/Ethnicity Distribution:\n"
        for race, count in race_count.most_common():
            percentage = (count / len(self.personas)) * 100
            text += f"  {race}: {count} ({percentage:.1f}%)\n"
        
        text += "\nAge Distribution:\n"
        for age_range, count in sorted(age_ranges.items()):
            percentage = (count / len(self.personas)) * 100 if len(self.personas) > 0 else 0
            text += f"  {age_range}: {count} ({percentage:.1f}%)\n"
        
        return text


def parse_log_for_metrics(log_file):
    """Parse log file to extract generation metrics"""
    metrics = {
        'iterations': [],
        'hyperedges_per_iteration': [],
        'phases': []
    }
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                # Extract iteration info
                if 'Iteration' in line:
                    # Parse iteration number and phase
                    pass
                
                # Extract hyperedge additions
                if 'Added hyperedge' in line:
                    pass
        
    except Exception as e:
        print(f"Error parsing log: {e}")
    
    return metrics


def export_stats_to_json(hypergraph_file, output_file):
    """Export statistics to JSON file"""
    stats_calculator = HypergraphStats(hypergraph_file)
    
    stats = {
        'basic_stats': stats_calculator.get_basic_stats(),
        'size_distribution': stats_calculator.get_size_distribution(),
        'degree_distribution': stats_calculator.get_node_degrees()
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"Statistics exported to {output_file}")


if __name__ == "__main__":
    # Test functionality
    import sys
    
    if len(sys.argv) > 1:
        hypergraph_file = sys.argv[1]
        stats = HypergraphStats(hypergraph_file)
        print(stats.format_stats_text())
    else:
        print("Usage: python visualization.py <hypergraph_file>")

