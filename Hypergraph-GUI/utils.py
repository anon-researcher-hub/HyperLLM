"""
Utility functions for HyperLLM GUI
Helper functions for file operations, validation, and formatting
"""

import os
import json
from pathlib import Path
from datetime import datetime


def validate_config_file(file_path):
    """Validate configuration hypergraph file format"""
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        if not lines:
            return False, "File is empty"
        
        # Check if lines contain space-separated node IDs
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            nodes = line.strip().split()
            if len(nodes) < 2:
                return False, f"Line {i+1}: Hyperedge must have at least 2 nodes"
        
        return True, f"Valid configuration file with {len(lines)} hyperedges"
    
    except Exception as e:
        return False, f"Error reading file: {str(e)}"


def validate_personas_file(file_path):
    """Validate personas JSON file format"""
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            personas = json.load(f)
        
        if not isinstance(personas, dict):
            return False, "Personas file must be a JSON object/dictionary"
        
        if not personas:
            return False, "Personas file is empty"
        
        # Check format of first persona
        first_key = list(personas.keys())[0]
        first_persona = personas[first_key]
        
        required_fields = ['gender', 'race/ethnicity', 'age']
        missing_fields = [field for field in required_fields if field not in first_persona]
        
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        return True, f"Valid personas file with {len(personas)} personas"
    
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON format: {str(e)}"
    except Exception as e:
        return False, f"Error reading file: {str(e)}"


def find_latest_run_directory(base_path="."):
    """Find the most recent run directory"""
    try:
        base = Path(base_path)
        run_dirs = [d for d in base.iterdir() if d.is_dir() and d.name.startswith("MAS_Config_Run_")]
        
        if not run_dirs:
            return None
        
        # Sort by modification time
        run_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return str(run_dirs[0])
    
    except Exception as e:
        print(f"Error finding run directories: {e}")
        return None


def find_latest_checkpoint(run_directory):
    """Find the latest checkpoint in a run directory"""
    try:
        checkpoints_dir = Path(run_directory) / "checkpoints"
        
        if not checkpoints_dir.exists():
            return None
        
        checkpoint_files = list(checkpoints_dir.glob("checkpoint_iteration_*.pkl"))
        
        if not checkpoint_files:
            return None
        
        # Sort by iteration number
        checkpoint_files.sort(key=lambda x: int(x.stem.split('_')[-1]), reverse=True)
        return str(checkpoint_files[0])
    
    except Exception as e:
        print(f"Error finding checkpoints: {e}")
        return None


def format_timestamp(timestamp_str=None):
    """Format timestamp for display"""
    if timestamp_str is None:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp_str


def format_file_size(size_bytes):
    """Format file size for display"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def get_file_info(file_path):
    """Get file information"""
    try:
        path = Path(file_path)
        
        if not path.exists():
            return None
        
        stat = path.stat()
        
        return {
            'name': path.name,
            'size': format_file_size(stat.st_size),
            'modified': format_timestamp(datetime.fromtimestamp(stat.st_mtime).isoformat()),
            'path': str(path.absolute())
        }
    
    except Exception as e:
        print(f"Error getting file info: {e}")
        return None


def parse_run_configuration(run_directory):
    """Parse run configuration from directory"""
    try:
        config_file = Path(run_directory) / "run_configuration.json"
        
        if not config_file.exists():
            return None
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return config
    
    except Exception as e:
        print(f"Error parsing run configuration: {e}")
        return None


def get_run_progress(run_directory):
    """Get progress information from run directory"""
    try:
        # Check for interruption info
        interruption_file = Path(run_directory) / "interruption_info.json"
        if interruption_file.exists():
            with open(interruption_file, 'r', encoding='utf-8') as f:
                info = json.load(f)
            return {
                'status': 'interrupted',
                'completion_percentage': info.get('completion_percentage', 0),
                'completed_edges': info.get('completed_edges', 0),
                'target_edges': info.get('target_edges', 0)
            }
        
        # Check for completion
        summary_file = Path(run_directory) / "run_summary.json"
        if summary_file.exists():
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary = json.load(f)
            return {
                'status': 'completed' if summary.get('run_completed') else 'in_progress',
                'completion_percentage': summary.get('completion_percentage', 0),
                'final_hypergraph_size': summary.get('final_hypergraph_size', 0),
                'target_size': summary.get('target_size', 0)
            }
        
        return {
            'status': 'unknown',
            'completion_percentage': 0
        }
    
    except Exception as e:
        print(f"Error getting run progress: {e}")
        return None


def export_hyperedges_to_formats(hypergraph_file, output_formats=['json', 'csv']):
    """Export hyperedges to different formats"""
    try:
        # Load hyperedges
        hyperedges = []
        with open(hypergraph_file, 'r') as f:
            for line in f:
                nodes = line.strip().split()
                if nodes:
                    hyperedges.append(nodes)
        
        base_name = Path(hypergraph_file).stem
        output_dir = Path(hypergraph_file).parent
        
        results = []
        
        # Export to JSON
        if 'json' in output_formats:
            json_file = output_dir / f"{base_name}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'hyperedges': hyperedges,
                    'num_hyperedges': len(hyperedges),
                    'exported_at': format_timestamp()
                }, f, indent=2)
            results.append(str(json_file))
        
        # Export to CSV
        if 'csv' in output_formats:
            csv_file = output_dir / f"{base_name}.csv"
            with open(csv_file, 'w', encoding='utf-8') as f:
                f.write("hyperedge_id,nodes,size\n")
                for i, edge in enumerate(hyperedges):
                    f.write(f"{i},\"{' '.join(edge)}\",{len(edge)}\n")
            results.append(str(csv_file))
        
        return results
    
    except Exception as e:
        print(f"Error exporting hyperedges: {e}")
        return []


def create_evaluation_report(hypergraph_file, output_file="evaluation_report.txt"):
    """Create comprehensive evaluation report"""
    try:
        from visualization import HypergraphStats
        
        stats = HypergraphStats(hypergraph_file)
        
        report = []
        report.append("=" * 60)
        report.append("HYPERGRAPH EVALUATION REPORT")
        report.append("=" * 60)
        report.append(f"\nGenerated: {format_timestamp()}")
        report.append(f"Source File: {hypergraph_file}\n")
        
        report.append(stats.format_stats_text())
        
        report.append("\n" + "=" * 60)
        report.append("END OF REPORT")
        report.append("=" * 60)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        return output_file
    
    except Exception as e:
        print(f"Error creating evaluation report: {e}")
        return None


def validate_agent_parameters(params):
    """Validate agent parameters"""
    errors = []
    
    for agent_name, agent_params in params.items():
        # Check temperature
        try:
            temp = float(agent_params.get('temperature', 0.7))
            if not (0.0 <= temp <= 2.0):
                errors.append(f"{agent_name}: Temperature must be between 0.0 and 2.0")
        except ValueError:
            errors.append(f"{agent_name}: Invalid temperature value")
        
        # Check max_tokens
        try:
            tokens = int(agent_params.get('max_tokens', 100))
            if tokens < 1:
                errors.append(f"{agent_name}: Max tokens must be positive")
        except ValueError:
            errors.append(f"{agent_name}: Invalid max_tokens value")
    
    return len(errors) == 0, errors


if __name__ == "__main__":
    # Test utilities
    print("Testing HyperLLM GUI Utilities...")
    
    # Test find latest run
    latest = find_latest_run_directory()
    if latest:
        print(f"Latest run directory: {latest}")
        
        config = parse_run_configuration(latest)
        if config:
            print(f"Run configuration: {json.dumps(config, indent=2)}")
        
        progress = get_run_progress(latest)
        if progress:
            print(f"Run progress: {json.dumps(progress, indent=2)}")

