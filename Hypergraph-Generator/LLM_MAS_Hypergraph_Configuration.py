import openai
import json
import argparse
import os
import random
import time
import collections
import pickle
from datetime import datetime
from typing import List, Dict, Any

# Load OpenAI API Key
def load_api_keys(filename="api-key.txt"):
    """Load OpenAI API Key"""
    possible_paths = [
        filename,
        os.path.join(os.path.dirname(__file__), filename),
        os.path.join("Hypergraph-Generator", filename),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "r") as f:
                lines = f.readlines()
            openai_key = lines[0].strip()
            print(f"✅ Found API key file: {path}")
            return openai_key
    
    print(f"❌ Cannot find API key file, please check the following locations:")
    for path in possible_paths:
        print(f"   - {os.path.abspath(path)}")
    raise FileNotFoundError(f"API key file not found: {filename}")

openai_key = load_api_keys("api-key.txt")

# Setup OpenAI client
# IMPORTANT: Replace with your own API base URL
# Example: "https://api.openai.com/v1" or your custom endpoint
BASE_URL_OPENAI = os.environ.get("OPENAI_BASE_URL", "PLEASE_SET_YOUR_BASE_URL")

if BASE_URL_OPENAI == "PLEASE_SET_YOUR_BASE_URL":
    raise ValueError(
        "Please set OPENAI_BASE_URL environment variable or modify BASE_URL_OPENAI in the code.\n"
        "Example: export OPENAI_BASE_URL='https://api.openai.com/v1'"
    )

client = openai.OpenAI(api_key=openai_key, base_url=BASE_URL_OPENAI)


class BaseAgent:
    """Base agent class"""
    def __init__(self, agent_id: str, model: str = "gpt-3.5-turbo"):
        self.agent_id = agent_id
        self.model = model
        self.decision_history = []
    
    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Agent decision interface"""
        raise NotImplementedError


class RelationshipGeneratorAgent(BaseAgent):
    """Relationship generator agent - responsible for creating new collaborations"""
    
    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        person_id = context['person_id']
        person_data = context['person_data']
        existing_hyperedges = context['existing_hyperedges']
        personas = context['personas']
        max_members = context['max_members']
        target_size = context.get('target_edge_size', random.randint(2, max_members))
        
        is_building_phase = len(existing_hyperedges) < max(10, len(personas) // 100)
        
        if is_building_phase:
            node_degrees = self._calculate_node_degrees(existing_hyperedges)
            high_degree_candidates = self._get_preferential_attachment_candidates(
                person_id, personas, node_degrees, person_data
            )
            
            prompt = f"""
            You are a relationship generator agent in the network building phase, rapidly establishing basic connections.
            
            Preferential Attachment Mechanism (Rich Get Richer Principle):
            In network evolution, high-degree nodes are more likely to gain new connections, reflecting the real-world "rich get richer" phenomenon.
            Prioritize selecting individuals with more existing connections as collaborators.
            
            Current Individual Information:
            - ID: {person_id}
            - Gender: {person_data['gender']}
            - Race/Ethnicity: {person_data['race/ethnicity']}
            - Age: {person_data['age']}
            - Religion: {person_data['religion']}
            - Political Affiliation: {person_data['political affiliation']}
            - Current Degree: {node_degrees.get(person_id, 0)}
            
            High-Degree Candidates (Priority Selection):
            {high_degree_candidates}
            
            Building Phase Selection Strategy:
            1. Preferential Attachment: Prioritize high-degree individuals
            2. Feature Matching: Select individuals with common features among high-degree nodes
            3. Degree Balance: Appropriately select medium-degree individuals to avoid over-concentration
            4. New Node Opportunity: Give some unconnected nodes opportunities
            
            Select {target_size - 1} collaborators (target hyperedge size: {target_size})
            
            Output Format:
            Output only selected individual IDs separated by spaces, e.g.: "3 7 15"
            Do not include own ID ({person_id}).
            """
        else:
            prompt = f"""
            You are a relationship generator agent responsible for creating collaboration groups. Use Chain of Thought reasoning.

            Preferential Attachment Mechanism (Rich Get Richer Principle):
            In network evolution, high-degree nodes are more likely to gain new connections, reflecting the real-world "rich get richer" phenomenon.
            Prioritize selecting individuals with more existing connections as collaborators.
            
            Chain of Thought Analysis Steps:
            1. Individual Feature Analysis
            2. Network Status Assessment  
            3. Collaborator Screening
            4. Group Size Decision
            5. Final Decision Output

            **Thinking Tree Expansion:**
            ```
            Individual Analysis
            ├── Basic Feature Matching
            │   ├── Same Feature Priority
            │   └── Complementary Feature Consideration
            ├── Network Position Analysis
            │   ├── Current Degree
            │   └── Potential Influence
            └── Collaboration Potential Assessment
                ├── Direct Collaboration
                └── Indirect Synergy
            ```

            **Current Individual Information:**
            - ID: {person_id}
            - Gender: {person_data['gender']}
            - Race/Ethnicity: {person_data['race/ethnicity']}
            - Age: {person_data['age']}
            - Religion: {person_data['religion']}
            - Political Affiliation: {person_data['political affiliation']}

            **Existing Network Structure (recent 5 hyperedges):**
            {self._format_recent_edges(existing_hyperedges[-5:])}

            **Chain of Thought Reasoning Process:**
            
            Step 1 - Individual Feature Analysis:
            First analyze the core features of this individual, identify their positioning and value in the group.

            Step 2 - Network Status Assessment:
            Assess connection patterns in the current network, avoid over-clustering or isolation.

            Step 3 - Collaborator Screening:
            Based on similarity and complementarity principles, screen potential collaborators.

            Step 4 - Group Size Decision:
            Based on collaboration efficiency and management cost, decide optimal group size.

            Step 5 - Final Decision:
            Select {target_size - 1} collaborators (target hyperedge size: {target_size}).

            Output Format:
            Output only selected individual IDs separated by spaces, e.g.: "3 7 15"
            Do not include own ID ({person_id}).
            """

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a relationship generator agent skilled at analyzing individual features and establishing reasonable collaborations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7 if is_building_phase else 0.7,
            )

            output = response.choices[0].message.content.strip()
            
            if is_building_phase:
                selected_ids = output.split()
            else:
                lines = output.split('\n')
                selected_ids = []
                for line in reversed(lines):
                    if line.strip() and not line.startswith('Step') and not line.startswith('**'):
                        selected_ids = line.strip().split()
                        break
            
            selected_ids = [pid for pid in selected_ids if pid in personas and pid != person_id]
            decision = {
                'action': 'generate',
                'agent_id': self.agent_id,
                'person_id': person_id,
                'selected_members': [person_id] + selected_ids,
                'reasoning': output,
                'phase': 'building' if is_building_phase else 'evolution'
            }
            self.decision_history.append(decision)
            return decision

        except Exception as e:
            print(f"Relationship generator agent call failed: {e}")
            return {
                'action': 'generate',
                'agent_id': self.agent_id,
                'person_id': person_id,
                'selected_members': [person_id],
                'reasoning': f"API call failed: {e}",
                'phase': 'building' if is_building_phase else 'evolution'
            }
    
    def _format_recent_edges(self, edges: List[List[str]]) -> str:
        if not edges:
            return "No existing hyperedges"
        return "\n".join([f"Hyperedge: {' '.join(edge)}" for edge in edges])
    
    def _calculate_node_degrees(self, hyperedges: List[List[str]]) -> Dict[str, int]:
        """Calculate node degrees in hypergraph (how many hyperedges each node appears in)"""
        node_degrees = {}
        for hyperedge in hyperedges:
            for node in hyperedge:
                node_degrees[node] = node_degrees.get(node, 0) + 1
        return node_degrees
    
    def _get_preferential_attachment_candidates(self, person_id: str, personas: Dict, 
                                               node_degrees: Dict[str, int], person_data: Dict) -> str:
        """Get candidate information for preferential attachment mechanism"""
        if not node_degrees:
            return "Network initial phase, no high-degree nodes yet, using random selection strategy."
        
        high_degree_nodes = []
        medium_degree_nodes = []
        zero_degree_nodes = []
        
        for node_id, node_data in personas.items():
            if node_id == person_id:
                continue
                
            degree = node_degrees.get(node_id, 0)
            node_info = f"ID{node_id}(degree{degree}, {node_data['gender']}, {node_data['race/ethnicity']}, age {node_data['age']})"
            
            if degree >= 2:
                high_degree_nodes.append(node_info)
            elif degree == 1:
                medium_degree_nodes.append(node_info)
            else:
                zero_degree_nodes.append(node_info)
        
        result_parts = []
        
        if high_degree_nodes:
            high_degree_display = high_degree_nodes[:10]
            result_parts.append(f"🔥 High-degree nodes (degree≥2, total {len(high_degree_nodes)}):")
            result_parts.append("   " + ", ".join(high_degree_display))
            if len(high_degree_nodes) > 10:
                result_parts.append(f"   ...and {len(high_degree_nodes)-10} other high-degree nodes")
        
        if medium_degree_nodes:
            medium_degree_display = medium_degree_nodes[:5]
            result_parts.append(f"📊 Medium-degree nodes (degree=1, total {len(medium_degree_nodes)}):")
            result_parts.append("   " + ", ".join(medium_degree_display))
            if len(medium_degree_nodes) > 5:
                result_parts.append(f"   ...and {len(medium_degree_nodes)-5} other medium-degree nodes")
        
        if zero_degree_nodes:
            result_parts.append(f"🆕 Unconnected nodes (degree=0, total {len(zero_degree_nodes)}): suggest giving connection opportunities")
        
        return "\n".join(result_parts) if result_parts else "All nodes have same degree, using feature matching strategy."


class RelationshipReviewerAgent(BaseAgent):
    """Relationship reviewer agent - responsible for reviewing existing relationship rationality"""
    
    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        hyperedge = context['hyperedge']
        personas = context['personas']
        network_stats = context.get('network_stats', {})
        
        prompt = f"""
        You are a relationship reviewer agent responsible for assessing the rationality of existing collaborations. Use Chain of Thought analysis.

        **Chain of Thought Analysis Framework:**
        1. Relationship Consistency Check
        2. Group Dynamics Analysis
        3. Network Health Assessment
        4. Sustainability Judgment
        5. Review Decision

        **Thinking Tree Structure:**
        ```
        Relationship Review
        ├── Internal Consistency
        │   ├── Feature Match Degree
        │   ├── Value Alignment
        │   └── Collaboration Feasibility
        ├── External Impact
        │   ├── Network Position
        │   ├── Resource Allocation
        │   └── Conflict Potential
        └── Long-term Sustainability
            ├── Stability Expectation
            └── Development Potential
        ```

        **Collaboration to Review:**
        Hyperedge members: {' '.join(hyperedge)}

        **Member Details:**
        {self._format_member_details(hyperedge, personas)}

        **Network Statistics:**
        Total hyperedges: {network_stats.get('total_edges', 0)}
        Average hyperedge size: {network_stats.get('avg_edge_size', 0):.2f}

        **Chain of Thought Reasoning:**
        
        Step 1 - Relationship Consistency Check:
        Analyze feature match degree and potential conflicts among members.

        Step 2 - Group Dynamics Analysis:
        Assess interaction patterns and collaboration efficiency within the group.

        Step 3 - Network Health Assessment:
        Check the impact of this relationship on overall network structure.

        Step 4 - Sustainability Judgment:
        Predict long-term stability and development potential of this relationship.

        Step 5 - Review Decision:
        Give final review result based on above analysis.

        **Output Format:**
        Output only "APPROVE" or "REJECT"
        """

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a relationship reviewer agent with strict evaluation standards and fair judgment ability."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3,
            )

            output = response.choices[0].message.content.strip()
            decision = "APPROVE" if "APPROVE" in output.upper() else "REJECT"
            
            result = {
                'action': 'review',
                'agent_id': self.agent_id,
                'hyperedge': hyperedge,
                'decision': decision,
                'reasoning': output
            }
            self.decision_history.append(result)
            return result

        except Exception as e:
            print(f"Relationship reviewer agent call failed: {e}")
            return {
                'action': 'review',
                'agent_id': self.agent_id,
                'hyperedge': hyperedge,
                'decision': 'APPROVE',
                'reasoning': f"API call failed, default approve: {e}"
            }
    
    def _format_member_details(self, hyperedge: List[str], personas: Dict) -> str:
        details = []
        for member_id in hyperedge:
            if member_id in personas:
                person = personas[member_id]
                details.append(f"ID {member_id}: {person['gender']}, {person['race/ethnicity']}, age {person['age']}, {person['religion']}, {person['political affiliation']}")
        return "\n".join(details)


class RelationshipRemoverAgent(BaseAgent):
    """Relationship remover agent - responsible for removing unreasonable or outdated relationships"""
    
    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        all_hyperedges = context['all_hyperedges']
        personas = context['personas']
        iteration = context.get('iteration', 0)
        
        if not all_hyperedges or iteration < 3:
            return {
                'action': 'remove',
                'agent_id': self.agent_id,
                'edges_to_remove': [],
                'reasoning': "Network initial phase, not removing relationships yet"
            }
        
        prompt = f"""
        You are a relationship remover agent responsible for identifying and removing unreasonable collaborations. Use Chain of Thought analysis.

        **Chain of Thought Analysis Steps:**
        1. Network Anomaly Detection
        2. Relationship Quality Assessment
        3. Redundant Relationship Identification
        4. Removal Impact Analysis
        5. Removal Decision Making

        **Thinking Tree Exploration:**
        ```
        Relationship Removal Analysis
        ├── Anomaly Detection
        │   ├── Over-connection
        │   ├── Feature Mismatch
        │   └── Isolated Groups
        ├── Quality Assessment
        │   ├── Internal Conflict
        │   ├── Low Efficiency
        │   └── Instability Factors
        └── Network Optimization
            ├── Reduce Redundancy
            └── Improve Quality
        ```

        **Current Network Status:**
        Total hyperedges: {len(all_hyperedges)}
        Current iteration: {iteration}

        **Network Hyperedge Overview (recent 10):**
        {self._format_recent_edges(all_hyperedges[-10:])}

        **Chain of Thought Reasoning Process:**

        Step 1 - Network Anomaly Detection:
        Identify anomaly patterns and unreasonable connections in the network.

        Step 2 - Relationship Quality Assessment:
        Assess internal coordination and external impact of each hyperedge.

        Step 3 - Redundant Relationship Identification:
        Find duplicate or overly overlapping collaborations.

        Step 4 - Removal Impact Analysis:
        Predict the impact of removing specific relationships on the overall network.

        Step 5 - Removal Decision:
        Select at most {max(1, len(all_hyperedges) // 10)} hyperedges to remove.

        **Output Format:**
        Output hyperedge indices to remove (starting from 0), space-separated, e.g.: "2 5 8"
        If no relationships need removal, output "NONE"
        """

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a relationship remover agent with keen network analysis ability and cautious removal strategy."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.4,
            )

            output = response.choices[0].message.content.strip()
            
            edges_to_remove = []
            lines = output.split('\n')
            for line in reversed(lines):
                if line.strip() and not line.startswith('Step') and not line.startswith('**'):
                    if "NONE" in line.upper():
                        break
                    try:
                        indices = [int(x) for x in line.strip().split() if x.isdigit()]
                        edges_to_remove = [i for i in indices if 0 <= i < len(all_hyperedges)]
                        break
                    except:
                        continue
            
            result = {
                'action': 'remove',
                'agent_id': self.agent_id,
                'edges_to_remove': edges_to_remove,
                'reasoning': output
            }
            self.decision_history.append(result)
            return result

        except Exception as e:
            print(f"Relationship remover agent call failed: {e}")
            return {
                'action': 'remove',
                'agent_id': self.agent_id,
                'edges_to_remove': [],
                'reasoning': f"API call failed: {e}"
            }
    
    def _format_recent_edges(self, edges: List[List[str]]) -> str:
        if not edges:
            return "No hyperedges"
        return "\n".join([f"Hyperedge{i}: {' '.join(edge)}" for i, edge in enumerate(edges)])


class NetworkOptimizerAgent(BaseAgent):
    """Network optimizer agent - responsible for optimizing network structure from global perspective"""
    
    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        all_hyperedges = context['all_hyperedges']
        personas = context['personas']
        iteration = context.get('iteration', 0)
        
        network_stats = self._calculate_network_stats(all_hyperedges, personas)
        
        prompt = f"""
        You are a network optimizer agent responsible for optimizing the entire hypergraph network structure from a global perspective. Use Chain of Thought analysis.

        **Chain of Thought Optimization Framework:**
        1. Network Topology Analysis
        2. Structural Balance Assessment
        3. Connectivity Check
        4. Diversity Measurement
        5. Optimization Strategy Formulation

        **Thinking Tree Search Space:**
        ```
        Network Optimization
        ├── Structural Optimization
        │   ├── Connectivity Enhancement
        │   ├── Clustering Optimization
        │   └── Degree Distribution Adjustment
        ├── Diversity Balance
        │   ├── Feature Distribution
        │   ├── Group Inclusiveness
        │   └── Avoid Homogenization
        └── Efficiency Improvement
            ├── Reduce Redundancy
            └── Enhance Synergy
        ```

        **Current Network Statistics:**
        Total hyperedges: {network_stats['total_edges']}
        Total nodes: {network_stats['total_nodes']}
        Average hyperedge size: {network_stats['avg_edge_size']:.2f}
        Network density: {network_stats['network_density']:.3f}
        Largest component size: {network_stats['largest_component_size']}

        **Diversity Metrics:**
        Gender distribution: {network_stats['gender_diversity']}
        Race distribution: {network_stats['race_diversity']}
        Religion distribution: {network_stats['religion_diversity']}

        **Chain of Thought Analysis:**

        Step 1 - Network Topology Analysis:
        Assess current network's topological properties and structural features.

        Step 2 - Structural Balance Assessment:
        Check whether the network has over-concentration or dispersion issues.

        Step 3 - Connectivity Check:
        Ensure network connectivity and information propagation efficiency.

        Step 4 - Diversity Measurement:
        Assess the network's diversity and inclusiveness level.

        Step 5 - Optimization Strategy:
        Propose specific network structure optimization recommendations.

        **Output Format:**
        Output optimization suggestion type: one of "INCREASE_CONNECTIONS", "ENHANCE_DIVERSITY", "REDUCE_CLUSTERING", "MAINTAIN_CURRENT"
        """

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a network optimizer agent with deep graph theory knowledge and network analysis capabilities."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=250,
                temperature=0.5,
            )

            output = response.choices[0].message.content.strip()
            
            strategy = "MAINTAIN_CURRENT"
            for line in output.split('\n'):
                for option in ["INCREASE_CONNECTIONS", "ENHANCE_DIVERSITY", "REDUCE_CLUSTERING", "MAINTAIN_CURRENT"]:
                    if option in line:
                        strategy = option
                        break
            
            result = {
                'action': 'optimize',
                'agent_id': self.agent_id,
                'strategy': strategy,
                'network_stats': network_stats,
                'reasoning': output
            }
            self.decision_history.append(result)
            return result

        except Exception as e:
            print(f"Network optimizer agent call failed: {e}")
            return {
                'action': 'optimize',
                'agent_id': self.agent_id,
                'strategy': 'MAINTAIN_CURRENT',
                'network_stats': network_stats,
                'reasoning': f"API call failed: {e}"
            }
    
    def _calculate_network_stats(self, hyperedges: List[List[str]], personas: Dict) -> Dict:
        if not hyperedges:
            return {
                'total_edges': 0, 'total_nodes': 0, 'avg_edge_size': 0,
                'network_density': 0, 'largest_component_size': 0,
                'gender_diversity': {}, 'race_diversity': {}, 'religion_diversity': {}
            }
        
        all_nodes = set()
        for edge in hyperedges:
            all_nodes.update(edge)
        
        gender_count = {}
        race_count = {}
        religion_count = {}
        
        for node in all_nodes:
            if node in personas:
                person = personas[node]
                gender_count[person['gender']] = gender_count.get(person['gender'], 0) + 1
                race_count[person['race/ethnicity']] = race_count.get(person['race/ethnicity'], 0) + 1
                religion_count[person['religion']] = religion_count.get(person['religion'], 0) + 1
        
        total_edges = len(hyperedges)
        total_nodes = len(all_nodes)
        avg_edge_size = sum(len(edge) for edge in hyperedges) / total_edges if total_edges > 0 else 0
        network_density = total_edges / (total_nodes * (total_nodes - 1) / 2) if total_nodes > 1 else 0
        
        return {
            'total_edges': total_edges,
            'total_nodes': total_nodes,
            'avg_edge_size': avg_edge_size,
            'network_density': network_density,
            'largest_component_size': total_nodes,
            'gender_diversity': gender_count,
            'race_diversity': race_count,
            'religion_diversity': religion_count
        }


class ProtectedMASHypergraphGenerator:
    """Protected Multi-Agent System based Dynamic Hypergraph Generator (Configuration-Driven Version)"""
    
    def __init__(self, personas_file: str, config_hypergraph_file: str, output_path: str,
                 groups_per_iteration: int = 5, max_members_per_group: int = 5, 
                 iterations: int = 10, model: str = "gpt-3.5-turbo"):
        """
        Initialize protected configuration-based MAS hypergraph generator
        :param personas_file: Personal data JSON file path
        :param config_hypergraph_file: Configuration hypergraph file path (for extracting hyperedge size distribution)
        :param output_path: Output path (can be file or directory)
        :param groups_per_iteration: Number of hyperedges per iteration
        :param max_members_per_group: Maximum members per hyperedge
        :param iterations: Evolution iteration count
        :param model: LLM model
        """
        self.personas_file = personas_file
        self.config_hypergraph_file = config_hypergraph_file
        self.groups_per_iteration = groups_per_iteration
        self.max_members_per_group = max_members_per_group
        self.num_iterations = iterations
        self.model = model
        
        # Create protected timestamped run directory
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_filename = os.path.splitext(os.path.basename(config_hypergraph_file))[0]
        self.run_dir = f"MAS_Config_Run_{config_filename}_{self.run_timestamp}"
        
        # Handle output path compatibility
        if output_path.endswith('.txt'):
            # If file path, create corresponding directory
            self.output_file = output_path
            base_dir = os.path.dirname(output_path) or '.'
            self.protected_run_dir = os.path.join(base_dir, self.run_dir)
        else:
            # If directory path
            self.protected_run_dir = os.path.join(output_path, self.run_dir)
            self.output_file = os.path.join(self.protected_run_dir, "final_hypergraph.txt")
        
        # Create protected directory structure
        os.makedirs(self.protected_run_dir, exist_ok=True)
        self.snapshots_dir = os.path.join(self.protected_run_dir, "iteration_snapshots")
        self.checkpoints_dir = os.path.join(self.protected_run_dir, "checkpoints")
        self.analysis_dir = os.path.join(self.protected_run_dir, "analysis")
        
        for directory in [self.snapshots_dir, self.checkpoints_dir, self.analysis_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Load data and analyze configuration
        self.personas = self.load_personas()
        self.edge_size_distribution = self.analyze_edge_size_distribution()
        self.edge_size_sequence = self.generate_edge_size_sequence()
        self.total_groups = len(self.edge_size_sequence)
        self.hyperedges = []
        
        # Create agents
        self.agents = {
            'generator': RelationshipGeneratorAgent('generator', model),
            'reviewer': RelationshipReviewerAgent('reviewer', model),
            'remover': RelationshipRemoverAgent('remover', model),
            'optimizer': NetworkOptimizerAgent('optimizer', model)
        }
        
        # Decision history and progress tracking
        self.evolution_history = []
        self.current_edge_index = 0
        self.start_iteration = 0
        
        # Save run configuration
        self.save_run_configuration()
        
        print(f"🛡️ Protection mechanism activated")
        print(f"📁 Run directory: {self.protected_run_dir}")
        print(f"💾 Snapshot directory: {self.snapshots_dir}")
        print(f"🔄 Checkpoint directory: {self.checkpoints_dir}")
    
    def save_run_configuration(self):
        """Save run configuration information"""
        config = {
            'personas_file': self.personas_file,
            'config_hypergraph_file': self.config_hypergraph_file,
            'groups_per_iteration': self.groups_per_iteration,
            'max_members_per_group': self.max_members_per_group,
            'num_iterations': self.num_iterations,
            'model': self.model,
            'run_timestamp': self.run_timestamp,
            'total_target_edges': self.total_groups,
            'edge_size_distribution': self.edge_size_distribution,
            'start_time': datetime.now().isoformat()
        }
        
        config_path = os.path.join(self.protected_run_dir, "run_configuration.json")
        with open(config_path, "w", encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def save_checkpoint(self, iteration: int):
        """Save checkpoint"""
        checkpoint = {
            'iteration': iteration,
            'current_edge_index': self.current_edge_index,
            'hyperedges': self.hyperedges,
            'evolution_history': self.evolution_history,
            'agents_history': {name: agent.decision_history for name, agent in self.agents.items()},
            'remaining_edge_sizes': self.edge_size_sequence[self.current_edge_index:],
            'timestamp': datetime.now().isoformat()
        }
        
        checkpoint_path = os.path.join(self.checkpoints_dir, f"checkpoint_iteration_{iteration:03d}.pkl")
        with open(checkpoint_path, "wb") as f:
            pickle.dump(checkpoint, f)
        
        # Also save JSON version for easy viewing
        checkpoint_json_path = os.path.join(self.checkpoints_dir, f"checkpoint_iteration_{iteration:03d}.json")
        json_checkpoint = checkpoint.copy()
        del json_checkpoint['agents_history']
        with open(checkpoint_json_path, "w", encoding='utf-8') as f:
            json.dump(json_checkpoint, f, indent=2, ensure_ascii=False)
    
    def load_checkpoint(self, checkpoint_path: str) -> bool:
        """Load checkpoint"""
        try:
            with open(checkpoint_path, "rb") as f:
                checkpoint = pickle.load(f)
            
            self.start_iteration = checkpoint['iteration'] + 1
            self.current_edge_index = checkpoint['current_edge_index']
            self.hyperedges = checkpoint['hyperedges']
            self.evolution_history = checkpoint['evolution_history']
            
            # Restore agent decision history
            for agent_name, history in checkpoint['agents_history'].items():
                if agent_name in self.agents:
                    self.agents[agent_name].decision_history = history
            
            # Restore remaining edge size sequence
            if 'remaining_edge_sizes' in checkpoint:
                remaining_sizes = checkpoint['remaining_edge_sizes']
                self.edge_size_sequence = self.edge_size_sequence[:self.current_edge_index] + remaining_sizes
            
            print(f"✅ Successfully loaded checkpoint, will continue from iteration {self.start_iteration}")
            print(f"📊 Current progress: {len(self.hyperedges)} hyperedges, index {self.current_edge_index}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load checkpoint: {e}")
            return False
    
    def resume_from_directory(self, resume_dir: str) -> bool:
        """Resume run from specified directory"""
        try:
            # Validate resume directory exists
            if not os.path.exists(resume_dir):
                print(f"❌ Resume directory does not exist: {resume_dir}")
                return False
            
            # Update protected directory paths
            self.protected_run_dir = resume_dir
            self.snapshots_dir = os.path.join(resume_dir, "iteration_snapshots")
            self.checkpoints_dir = os.path.join(resume_dir, "checkpoints")
            self.analysis_dir = os.path.join(resume_dir, "analysis")
            
            # Validate subdirectories
            for directory in [self.snapshots_dir, self.checkpoints_dir, self.analysis_dir]:
                if not os.path.exists(directory):
                    print(f"❌ Missing required subdirectory: {directory}")
                    return False
            
            # Find latest checkpoint
            latest_checkpoint = self.find_latest_checkpoint()
            if not latest_checkpoint:
                print(f"❌ No checkpoint file found in resume directory")
                return False
            
            # Load checkpoint
            print(f"🔄 Found checkpoint: {latest_checkpoint}")
            return self.load_checkpoint(latest_checkpoint)
            
        except Exception as e:
            print(f"❌ Failed to resume from directory: {e}")
            return False
    
    def find_latest_checkpoint(self) -> str:
        """Find latest checkpoint"""
        if not os.path.exists(self.checkpoints_dir):
            return None
            
        checkpoint_files = [f for f in os.listdir(self.checkpoints_dir) if f.endswith('.pkl')]
        if not checkpoint_files:
            return None
            
        # Sort by iteration number, return latest
        checkpoint_files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
        latest_checkpoint = os.path.join(self.checkpoints_dir, checkpoint_files[-1])
        return latest_checkpoint
    
    def load_personas(self) -> Dict:
        """Load personas.json file"""
        # Smart search for personas file path
        possible_paths = [
            self.personas_file,
            os.path.join("text-files", os.path.basename(self.personas_file)),
            os.path.join("Hypergraph-Generator", os.path.basename(self.personas_file)),
            os.path.join("personas.json"),
            os.path.join("text-files", "personas.json"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✅ Found personas file: {path}")
                with open(path, "r", encoding='utf-8') as f:
                    data = json.load(f)
                return data
        
        # If not found, give clear error message
        print(f"❌ Cannot find personas file, please check the following locations:")
        for path in possible_paths:
            print(f"   - {os.path.abspath(path)}")
        raise FileNotFoundError(f"Personas file not found: {self.personas_file}")
    
    def analyze_edge_size_distribution(self) -> Dict[int, int]:
        """Analyze hyperedge size distribution from configuration file"""
        # Smart search for configuration file path
        possible_paths = [
            self.config_hypergraph_file,
            os.path.join("Hypergraph-Datasets", os.path.basename(self.config_hypergraph_file)),
            os.path.join("..", "Hypergraph-Datasets", os.path.basename(self.config_hypergraph_file)),
            os.path.join("Hypergraph-Generator", "Hypergraph-Datasets", os.path.basename(self.config_hypergraph_file)),
        ]
        
        config_file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                config_file_path = path
                print(f"✅ Found configuration file: {path}")
                break
        
        if config_file_path is None:
            print(f"❌ Cannot find configuration file, please check the following locations:")
            for path in possible_paths:
                print(f"   - {os.path.abspath(path)}")
            raise FileNotFoundError(f"Configuration file not found: {self.config_hypergraph_file}")
        
        with open(config_file_path, 'r') as f:
            lines = f.readlines()
        
        edge_sizes = []
        for line in lines:
            nodes = line.strip().split()
            if nodes:
                edge_sizes.append(len(nodes))
        
        size_distribution = collections.Counter(edge_sizes)
        
        print(f"📊 Hyperedge size distribution analyzed from configuration file {self.config_hypergraph_file}:")
        for size in sorted(size_distribution.keys()):
            print(f"   Size {size}: {size_distribution[size]} hyperedges")
        print(f"   Total hyperedges: {sum(size_distribution.values())}")
        
        return dict(size_distribution)
    
    def generate_edge_size_sequence(self) -> List[int]:
        """Generate random sequence of hyperedge sizes based on distribution"""
        edge_sizes = []
        for size, count in self.edge_size_distribution.items():
            edge_sizes.extend([size] * count)
        
        # Randomly shuffle order
        random.shuffle(edge_sizes)
        
        print(f"🔀 Generated random sequence containing {len(edge_sizes)} hyperedges")
        return edge_sizes
    
    def save_iteration_snapshot(self, iteration: int, iteration_results: Dict):
        """Save iteration snapshot"""
        snapshot = {
            'iteration': iteration,
            'timestamp': datetime.now().isoformat(),
            'hypergraph_state': {
                'num_edges': len(self.hyperedges),
                'edges': self.hyperedges.copy(),
                'current_edge_index': self.current_edge_index,
                'progress_percentage': (self.current_edge_index / len(self.edge_size_sequence)) * 100
            },
            'network_statistics': self.agents['optimizer']._calculate_network_stats(self.hyperedges, self.personas),
            'iteration_results': iteration_results,
            'agents_decisions': {
                name: agent.decision_history[-1] if agent.decision_history else None 
                for name, agent in self.agents.items()
            }
        }
        
        # Save hypergraph state
        hypergraph_file = os.path.join(self.snapshots_dir, f"iteration_{iteration:03d}_hypergraph.txt")
        with open(hypergraph_file, "w", encoding='utf-8') as f:
            for edge in self.hyperedges:
                f.write(" ".join(map(str, edge)) + "\n")
        
        # Save detailed snapshot
        snapshot_file = os.path.join(self.snapshots_dir, f"iteration_{iteration:03d}_snapshot.json")
        with open(snapshot_file, "w", encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
        
        # Save network statistics
        stats_file = os.path.join(self.analysis_dir, f"iteration_{iteration:03d}_stats.json")
        with open(stats_file, "w", encoding='utf-8') as f:
            json.dump(snapshot['network_statistics'], f, indent=2, ensure_ascii=False)
    
    def run_iteration(self, iteration: int) -> Dict[str, Any]:
        """Run single iteration (distinguish building phase and evolution phase)"""
        try:
            print(f"\n🔄 Iteration {iteration + 1}/{self.num_iterations}")
            
            iteration_results = {
                'iteration': iteration,
                'timestamp': datetime.now().isoformat(),
                'actions': [],
                'hyperedges_before': len(self.hyperedges),
                'hyperedges_after': 0,
                'phase': None
            }
            
            # Determine current phase: building vs evolution
            # Building phase: until all target hyperedges are generated
            is_building_phase = self.current_edge_index < len(self.edge_size_sequence)
            
            if is_building_phase:
                # ==================== Building Phase Logic ====================
                iteration_results['phase'] = 'building'
                print(f"🏗️ [Building Phase] Rapid hyperedge generation (progress: {self.current_edge_index}/{len(self.edge_size_sequence)})")
                
                # Building phase: only use generator agent, no review, no removal, no optimization
                all_persons = list(self.personas.keys())
                generated_count = 0
                max_attempts = self.groups_per_iteration * 3
                
                for attempt in range(max_attempts):
                    if self.current_edge_index >= len(self.edge_size_sequence):
                        print("✅ Building phase complete! All target hyperedges generated")
                        break
                    
                    # Get current target hyperedge size
                    target_edge_size = self.edge_size_sequence[self.current_edge_index]
                    
                    # Use preferential attachment to select main individual (building phase)
                    if len(self.hyperedges) > 0:
                        node_degrees = {}
                        for edge in self.hyperedges:
                            for node in edge:
                                node_degrees[node] = node_degrees.get(node, 0) + 1
                        
                        # 85% probability select high-degree nodes, 15% random selection
                        if random.random() < 0.85 and node_degrees:
                            # Weighted selection from connected nodes by degree
                            nodes_with_degrees = list(node_degrees.items())
                            weights = [degree + 1 for _, degree in nodes_with_degrees]
                            main_person = random.choices(
                                [node for node, _ in nodes_with_degrees], 
                                weights=weights
                            )[0]
                            print(f"🎯 Preferential attachment selected {main_person} (degree: {node_degrees[main_person]})")
                        else:
                            main_person = random.choice(all_persons)
                            print(f"🎲 Randomly selected {main_person}")
                    else:
                        main_person = random.choice(all_persons)
                    
                    # Call generator agent
                    generator_context = {
                        'person_id': main_person,
                        'person_data': self.personas[main_person],
                        'existing_hyperedges': self.hyperedges,
                        'personas': self.personas,
                        'max_members': self.max_members_per_group,
                        'target_edge_size': target_edge_size
                    }
                    
                    generator_decision = self.agents['generator'].make_decision(generator_context)
                    
                    # Building phase: lenient quality check (avoid loops, increase diversity)
                    if len(generator_decision['selected_members']) >= 2:
                        # Pass current hyperedge info for quality check
                        self._current_hyperedges = self.hyperedges
                        should_approve = self._lenient_quality_check(
                            generator_decision['selected_members'],
                            self.personas
                        )
                        
                        if should_approve:
                            new_edge = generator_decision['selected_members']
                            self.hyperedges.append(new_edge)
                            print(f"  ✅ Added hyperedge #{len(self.hyperedges)} (size {len(new_edge)}): {' '.join(new_edge)}")
                            generated_count += 1
                            self.current_edge_index += 1
                            
                            iteration_results['actions'].append({
                                'action': 'generate',
                                'edge': new_edge,
                                'size': len(new_edge),
                                'phase': 'building'
                            })
                        else:
                            print(f"  ❌ Quality check failed: {' '.join(generator_decision['selected_members'])}")
                
                # Building phase completion check
                if self.current_edge_index >= len(self.edge_size_sequence):
                    print("\n" + "="*80)
                    print("🎉 Building phase complete! Validating hyperedge size distribution...")
                    print("="*80)
                    self._validate_distribution_match()
                    print("\nNext round will enter evolution phase, starting dynamic optimization...")
            
            else:
                # ==================== Evolution Phase Logic ====================
                iteration_results['phase'] = 'evolution'
                print(f"🔄 [Evolution Phase] Dynamic network optimization (hyperedges: {len(self.hyperedges)})")
                
                # Evolution phase goal: maintain dynamic balance in hyperedge count
                # Operations for removal, generation, and optimization are roughly balanced
                
                # 1. Network optimizer agent analysis
                optimizer_context = {
                    'all_hyperedges': self.hyperedges,
                    'personas': self.personas,
                    'iteration': iteration
                }
                optimizer_decision = self.agents['optimizer'].make_decision(optimizer_context)
                iteration_results['actions'].append(optimizer_decision)
                print(f"  📊 Optimizer suggestion: {optimizer_decision['strategy']}")
                
                # 2. Remover agent - identify hyperedges to remove
                remover_context = {
                    'all_hyperedges': self.hyperedges,
                    'personas': self.personas,
                    'iteration': iteration
                }
                remover_decision = self.agents['remover'].make_decision(remover_context)
                iteration_results['actions'].append(remover_decision)
                
                # Execute removal (at most groups_per_iteration hyperedges)
                edges_to_remove = sorted(remover_decision['edges_to_remove'], reverse=True)
                edges_to_remove = edges_to_remove[:self.groups_per_iteration]
                removed_count = 0
                
                for edge_idx in edges_to_remove:
                    if 0 <= edge_idx < len(self.hyperedges):
                        removed_edge = self.hyperedges.pop(edge_idx)
                        print(f"  🗑️ Removed hyperedge: {' '.join(removed_edge)}")
                        removed_count += 1
                        iteration_results['actions'].append({
                            'action': 'remove',
                            'edge': removed_edge,
                            'phase': 'evolution'
                        })
                
                # 3. Generator agent - add new hyperedges (count comparable to removals)
                # Randomly select some from existing hyperedges as context
                all_persons = list(self.personas.keys())
                generated_count = 0
                target_generate_count = max(removed_count, self.groups_per_iteration // 2)
                max_attempts = target_generate_count * 2
                
                # Generate new hyperedges in evolution phase
                for attempt in range(max_attempts):
                    if generated_count >= target_generate_count:
                        break
                    
                    # Randomly select portion of existing hyperedges as context
                    context_edges = random.sample(self.hyperedges, min(5, len(self.hyperedges)))
                    
                    # Select main individual: prioritize same background features
                    main_person = self._select_person_by_background(all_persons)
                    
                    # Randomly select target size based on existing hyperedge size distribution
                    existing_sizes = [len(e) for e in self.hyperedges]
                    target_edge_size = random.choice(existing_sizes) if existing_sizes else 3
                    
                    generator_context = {
                        'person_id': main_person,
                        'person_data': self.personas[main_person],
                        'existing_hyperedges': context_edges,
                        'personas': self.personas,
                        'max_members': self.max_members_per_group,
                        'target_edge_size': target_edge_size
                    }
                    
                    generator_decision = self.agents['generator'].make_decision(generator_context)
                    
                    # Evolution phase: use lenient review
                    if len(generator_decision['selected_members']) >= 2:
                        should_approve = self._moderate_llm_review(
                            generator_decision['selected_members'],
                            self.personas,
                            self.hyperedges
                        )
                        
                        if should_approve:
                            new_edge = generator_decision['selected_members']
                            self.hyperedges.append(new_edge)
                            print(f"  ✅ Added hyperedge (size {len(new_edge)}): {' '.join(new_edge)}")
                            generated_count += 1
                            
                            iteration_results['actions'].append({
                                'action': 'generate',
                                'edge': new_edge,
                                'size': len(new_edge),
                                'phase': 'evolution'
                            })
                        else:
                            print(f"  ❌ Review rejected: {' '.join(generator_decision['selected_members'])}")
                
                print(f"  📊 Evolution stats: Removed {removed_count}, Added {generated_count}, Net change {generated_count - removed_count}")
            
            iteration_results['hyperedges_after'] = len(self.hyperedges)
            self.evolution_history.append(iteration_results)
            
            # Save iteration snapshot
            self.save_iteration_snapshot(iteration, iteration_results)
            
            # Save checkpoint
            self.save_checkpoint(iteration)
            
            return iteration_results
            
        except Exception as e:
            print(f"⚠️ Exception occurred in iteration {iteration}: {e}")
            # Save emergency checkpoint
            try:
                emergency_checkpoint = {
                    'iteration': iteration,
                    'current_edge_index': self.current_edge_index,
                    'hyperedges': self.hyperedges,
                    'evolution_history': self.evolution_history,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                emergency_path = os.path.join(self.checkpoints_dir, f"emergency_checkpoint_iteration_{iteration:03d}.json")
                with open(emergency_path, "w", encoding='utf-8') as f:
                    json.dump(emergency_checkpoint, f, indent=2, ensure_ascii=False)
                print(f"💾 Emergency checkpoint saved: {emergency_path}")
            except:
                pass
            raise
    
    def _lenient_quality_check(self, hyperedge: List[str], personas: Dict) -> bool:
        if len(hyperedge) < 2:
            return False
            
        # Check if members exist
        valid_members = 0
        for member_id in hyperedge:
            if member_id in personas:
                valid_members += 1
        
        # Basic check: at least 50% of members exist
        if valid_members < len(hyperedge) * 0.5 or valid_members < 2:
            return False
        
        # Check for complete duplication with existing hyperedges (avoid loops)
        edge_set = set(hyperedge)
        for existing_edge in getattr(self, '_current_hyperedges', []):
            if edge_set == set(existing_edge):
                return False 
        
        # Preferential attachment weighted check: calculate node degree distribution in hyperedge
        node_degrees = {}
        for edge in getattr(self, '_current_hyperedges', []):
            for node in edge:
                node_degrees[node] = node_degrees.get(node, 0) + 1
        
        high_degree_count = sum(1 for member in hyperedge if node_degrees.get(member, 0) >= 2)
        medium_degree_count = sum(1 for member in hyperedge if node_degrees.get(member, 0) == 1)
        
        # If contains high-degree nodes, increase pass rate
        if high_degree_count > 0:
            return True
        elif medium_degree_count > 0:
            return random.random() < 0.9
        else:
            return random.random() < 0.7
    
    def _moderate_llm_review(self, hyperedge: List[str], personas: Dict, existing_edges: List) -> bool:
        """Lenient LLM review for evolution phase"""
        try:
            # Simplified prompt
            prompt = f"""
            You are a lenient relationship review agent, with the goal of promoting network growth.
            
            Review relationship: {' '.join(hyperedge)}
            
            Please review based on the following principles:
            1. APPROVE as long as it's not obviously unreasonable
            2. Prioritize network growth
            3. Allow diverse collaborative relationships
            
            Output format: Only output "APPROVE" or "REJECT"
            """
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a review agent that tends to approve reasonable relationships."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.3,
            )
            
            output = response.choices[0].message.content.strip()
            return "APPROVE" in output.upper()
            
        except Exception as e:
            # Default to pass if API fails
            print(f"Review API call failed, defaulting to approve: {e}")
            return True
    
    def _select_person_by_background(self, all_persons: List[str]) -> str:
        """
        Evolution phase: select individual based on background features
        Prioritize selecting individuals with same background as existing hyperedges (simulate human interaction tendencies)
        """
        if not self.hyperedges or random.random() < 0.3:
            return random.choice(all_persons)
        
        # Count distribution of background features in existing hyperedges
        background_counts = {
            'gender': {},
            'race': {},
            'religion': {},
            'political': {}
        }
        
        for edge in self.hyperedges:
            for node_id in edge:
                if node_id in self.personas:
                    person = self.personas[node_id]
                    background_counts['gender'][person['gender']] = background_counts['gender'].get(person['gender'], 0) + 1
                    background_counts['race'][person['race/ethnicity']] = background_counts['race'].get(person['race/ethnicity'], 0) + 1
                    background_counts['religion'][person['religion']] = background_counts['religion'].get(person['religion'], 0) + 1
                    background_counts['political'][person['political affiliation']] = background_counts['political'].get(person['political affiliation'], 0) + 1
        
        # Find most common background features
        most_common_gender = max(background_counts['gender'], key=background_counts['gender'].get) if background_counts['gender'] else None
        most_common_race = max(background_counts['race'], key=background_counts['race'].get) if background_counts['race'] else None
        most_common_religion = max(background_counts['religion'], key=background_counts['religion'].get) if background_counts['religion'] else None
        
        # Prioritize individuals with same background features
        candidates = []
        for person_id in all_persons:
            if person_id in self.personas:
                person = self.personas[person_id]
                score = 0
                if person['gender'] == most_common_gender:
                    score += 1
                if person['race/ethnicity'] == most_common_race:
                    score += 1
                if person['religion'] == most_common_religion:
                    score += 1
                candidates.append((person_id, score))
        
        # Sort by score, prioritize high scores
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Randomly select from top 30%
        top_30_percent = max(1, len(candidates) // 3)
        selected = random.choice(candidates[:top_30_percent])
        
        return selected[0]
    
    def save_final_results(self):
        """Save final results and complete evolution history"""
        # Save final hypergraph to compatible path
        with open(self.output_file, "w", encoding='utf-8') as f:
            for edge in self.hyperedges:
                f.write(" ".join(map(str, edge)) + "\n")
        
        # Save detailed results to protected directory
        final_hypergraph_path = os.path.join(self.protected_run_dir, "final_hypergraph.txt")
        with open(final_hypergraph_path, "w", encoding='utf-8') as f:
            for edge in self.hyperedges:
                f.write(" ".join(map(str, edge)) + "\n")
        
        # Save evolution history
        evolution_history_path = os.path.join(self.protected_run_dir, "evolution_history.json")
        with open(evolution_history_path, "w", encoding='utf-8') as f:
            json.dump(self.evolution_history, f, indent=2, ensure_ascii=False)
        
        # Save agent decision history
        agents_history_path = os.path.join(self.protected_run_dir, "agents_history.json")
        agents_history = {}
        for agent_name, agent in self.agents.items():
            agents_history[agent_name] = agent.decision_history
        
        with open(agents_history_path, "w", encoding='utf-8') as f:
            json.dump(agents_history, f, indent=2, ensure_ascii=False)
        
        # Save final run summary
        summary = {
            'run_completed': True,
            'completion_time': datetime.now().isoformat(),
            'total_iterations': len(self.evolution_history),
            'final_hypergraph_size': len(self.hyperedges),
            'target_size': self.total_groups,
            'completion_percentage': (len(self.hyperedges) / self.total_groups) * 100,
            'final_network_stats': self.agents['optimizer']._calculate_network_stats(self.hyperedges, self.personas)
        }
        
        summary_path = os.path.join(self.protected_run_dir, "run_summary.json")
        with open(summary_path, "w", encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

    def run(self, resume_from_dir: str = None):
        """Run complete protected MAS hypergraph generation process (two-phase)"""
        print("🚀 Starting protected configuration-driven multi-agent system hypergraph generation...")
        print("="*80)
        
        # Check if need to resume from specified directory
        if resume_from_dir:
            print(f"🔄 Resuming from specified directory: {resume_from_dir}")
            if self.resume_from_directory(resume_from_dir):
                print("✅ Successfully resumed from checkpoint")
            else:
                print("❌ Checkpoint resume failed, starting from beginning")
                self.start_iteration = 0
        else:
            print("📝 Starting new run")
            self.start_iteration = 0
        
        print(f"📊 Loaded {len(self.personas)} individuals")
        print(f"📁 Configuration file: {self.config_hypergraph_file}")
        print(f"🎯 Target generation: {self.total_groups} hyperedges")
        print(f"🤖 Initialized {len(self.agents)} agents:")
        for agent_name in self.agents.keys():
            print(f"   - {agent_name}")
        
        print("\n" + "="*80)
        print("🏗️ Phase 1: Building Phase (Rapid generation of base network)")
        print("   - Only use generator agent")
        print("   - Use preferential attachment mechanism")
        print("   - Generate hypergraph with size distribution exactly matching real network")
        print("="*80)
        
        start_time = time.time()
        building_start_time = start_time
        
        try:
            # ==================== Phase 1: Building Phase ====================
            for iteration in range(self.start_iteration, self.num_iterations):
                # Check if building phase complete
                if self.current_edge_index >= len(self.edge_size_sequence):
                    building_end_time = time.time()
                    print(f"\n✅ Building phase complete!")
                    print(f"   Time elapsed: {building_end_time - building_start_time:.2f} seconds")
                    print(f"   Generated hyperedges: {len(self.hyperedges)}")
                    
                    # Display distribution comparison
                    print("\n" + "="*80)
                    print("📊 Hyperedge size distribution validation results")
                    print("="*80)
                    self._validate_distribution_match()
                    
                    # Enter evolution phase
                    print("\n" + "="*80)
                    print("🔄 Phase 2: Evolution Phase (Dynamic network optimization)")
                    print("   - Use all agents (generator, reviewer, remover, optimizer)")
                    print("   - Maintain dynamic balance in hyperedge count")
                    print("   - Human interaction simulation based on background features")
                    print("="*80)
                    break
                    
                # Run building phase iteration
                iteration_result = self.run_iteration(iteration)
                progress = (self.current_edge_index / len(self.edge_size_sequence)) * 100
                print(f"   [{iteration_result['phase']}] Iteration {iteration + 1}: {iteration_result['hyperedges_before']} → {iteration_result['hyperedges_after']} hyperedges (progress: {progress:.1f}%)")
            
            # ==================== Phase 2: Evolution Phase ====================
            evolution_start_iteration = iteration + 1
            for evolution_iteration in range(evolution_start_iteration, self.num_iterations):
                iteration_result = self.run_iteration(evolution_iteration)
                print(f"   [{iteration_result['phase']}] Iteration {evolution_iteration + 1}: {iteration_result['hyperedges_before']} → {iteration_result['hyperedges_after']} hyperedges")
            
            # Save final results
            self.save_final_results()
            
            end_time = time.time()
            print("\n" + "="*80)
            print("✅ Protected configuration-driven MAS hypergraph generation complete!")
            print("="*80)
            print(f"⏱️ Total time: {end_time - start_time:.2f} seconds")
            print(f"📁 Main output: {self.output_file}")
            print(f"📁 Protected directory: {self.protected_run_dir}")
            print(f"📊 Final hypergraph contains {len(self.hyperedges)} hyperedges")
            print("="*80)
            
            # Final validation
            print("\n📊 Final hyperedge size distribution validation:")
            self._validate_distribution_match()
            
        except KeyboardInterrupt:
            print(f"\n⚠️ User interrupted program")
            self._handle_interruption()
        except Exception as e:
            print(f"\n❌ Program exception occurred: {e}")
            import traceback
            traceback.print_exc()
            self._handle_interruption()
    
    def _handle_interruption(self):
        """Handle program interruption"""
        print("🛡️ Protection mechanism activated, saving current state...")
        
        try:
            # Save final state
            if self.hyperedges:
                interrupted_path = os.path.join(self.protected_run_dir, "interrupted_hypergraph.txt")
                with open(interrupted_path, "w", encoding='utf-8') as f:
                    for edge in self.hyperedges:
                        f.write(" ".join(map(str, edge)) + "\n")
                print(f"💾 Current hypergraph saved: {interrupted_path}")
            
            # Save interruption state
            interruption_info = {
                'interruption_time': datetime.now().isoformat(),
                'current_iteration': len(self.evolution_history),
                'current_edge_index': self.current_edge_index,
                'completed_edges': len(self.hyperedges),
                'target_edges': self.total_groups,
                'completion_percentage': (len(self.hyperedges) / self.total_groups) * 100 if self.total_groups > 0 else 0,
                'resume_instructions': f"Use --resume parameter to resume from {self.protected_run_dir}"
            }
            
            interruption_path = os.path.join(self.protected_run_dir, "interruption_info.json")
            with open(interruption_path, "w", encoding='utf-8') as f:
                json.dump(interruption_info, f, indent=2, ensure_ascii=False)
            
            print(f"📋 Interruption info saved: {interruption_path}")
            print(f"🔄 To resume, use: --resume parameter")
            print(f"📁 Data safely saved at: {self.protected_run_dir}")
            
        except Exception as e:
            print(f"❌ Error occurred while saving interruption state: {e}")
    
    def _validate_distribution_match(self):
        """Validate if generated hypergraph matches target distribution"""
        # Calculate actual generated hyperedge size distribution
        actual_sizes = [len(edge) for edge in self.hyperedges]
        actual_distribution = collections.Counter(actual_sizes)
        
        print(f"\n🔍 Hyperedge size distribution validation:")
        print(f"{'Size':<6} {'Target':<8} {'Actual':<8} {'Match':<8}")
        print("-" * 32)
        
        all_sizes = set(self.edge_size_distribution.keys()) | set(actual_distribution.keys())
        perfect_match = True
        
        for size in sorted(all_sizes):
            target_count = self.edge_size_distribution.get(size, 0)
            actual_count = actual_distribution.get(size, 0)
            match_status = "✅" if target_count == actual_count else "❌"
            if target_count != actual_count:
                perfect_match = False
            
            print(f"{size:<6} {target_count:<8} {actual_count:<8} {match_status:<8}")
        
        if perfect_match:
            print("🎯 Perfect match! Generated hypergraph exactly matches target distribution")
        else:
            print("⚠️ Distribution doesn't completely match, may need to adjust parameters or increase iterations")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Protected configuration-driven multi-agent system hypergraph generator")
    parser.add_argument("--personas", type=str, required=True, help="Individual data JSON file path")
    parser.add_argument("--config", type=str, required=True, help="Configuration hypergraph file path (for extracting hyperedge size distribution)")
    parser.add_argument("--output", type=str, required=True, help="Hypergraph output file path or directory")
    parser.add_argument("--groups_per_iter", type=int, default=5, help="Number of hyperedges generated per iteration")
    parser.add_argument("--max_members", type=int, default=5, help="Maximum members per hyperedge")
    parser.add_argument("--iterations", type=int, default=10, help="Dynamic evolution iteration count")
    parser.add_argument("--model", type=str, choices=['gpt-3.5-turbo', 'claude-3-sonnet', 'gpt-4', 'gpt-4.1-nano'],
                        default="gpt-4", help="Select LLM model to use")
    parser.add_argument("--resume", type=str, default=None, help="Resume from checkpoint in specified directory (provide run directory path)")

    args = parser.parse_args()

    generator = ProtectedMASHypergraphGenerator(
        personas_file=args.personas,
        config_hypergraph_file=args.config,
        output_path=args.output,
        groups_per_iteration=args.groups_per_iter,
        max_members_per_group=args.max_members,
        iterations=args.iterations,
        model=args.model
    )

    generator.run(resume_from_dir=args.resume)
 