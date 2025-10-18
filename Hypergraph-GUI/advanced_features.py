"""
Advanced features for HyperLLM GUI
Including progress tracking, statistics display, and enhanced visualization
"""

import os
import json
import threading
import queue
from datetime import datetime
from pathlib import Path


class ProgressTracker:
    """Track generation progress and provide updates"""
    
    def __init__(self):
        self.current_phase = "idle"
        self.total_hyperedges = 0
        self.target_hyperedges = 0
        self.current_iteration = 0
        self.total_iterations = 0
        self.hyperedges_history = []
        self.phase_changes = []
        
    def update_phase(self, phase):
        """Update current phase"""
        self.current_phase = phase
        self.phase_changes.append({
            'phase': phase,
            'timestamp': datetime.now().isoformat(),
            'hyperedges_count': self.total_hyperedges
        })
    
    def add_hyperedge(self, hyperedge):
        """Add a new hyperedge to tracking"""
        self.total_hyperedges += 1
        self.hyperedges_history.append({
            'index': self.total_hyperedges,
            'nodes': hyperedge,
            'size': len(hyperedge),
            'iteration': self.current_iteration,
            'phase': self.current_phase,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_progress_percentage(self):
        """Calculate progress percentage"""
        if self.target_hyperedges == 0:
            return 0
        return min(100, (self.total_hyperedges / self.target_hyperedges) * 100)
    
    def get_statistics(self):
        """Get current statistics"""
        if not self.hyperedges_history:
            return {
                'total_hyperedges': 0,
                'avg_size': 0,
                'building_phase_count': 0,
                'evolution_phase_count': 0
            }
        
        building_count = sum(1 for h in self.hyperedges_history if h['phase'] == 'building')
        evolution_count = sum(1 for h in self.hyperedges_history if h['phase'] == 'evolution')
        
        sizes = [h['size'] for h in self.hyperedges_history]
        avg_size = sum(sizes) / len(sizes) if sizes else 0
        
        return {
            'total_hyperedges': self.total_hyperedges,
            'avg_size': avg_size,
            'building_phase_count': building_count,
            'evolution_phase_count': evolution_count,
            'current_iteration': self.current_iteration,
            'progress_percentage': self.get_progress_percentage()
        }
    
    def export_to_json(self, output_file):
        """Export tracking data to JSON"""
        data = {
            'metadata': {
                'exported_at': datetime.now().isoformat(),
                'total_hyperedges': self.total_hyperedges,
                'target_hyperedges': self.target_hyperedges,
                'total_iterations': self.total_iterations
            },
            'statistics': self.get_statistics(),
            'phase_changes': self.phase_changes,
            'hyperedges_history': self.hyperedges_history
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


class LogParser:
    """Parse and analyze generation logs"""
    
    @staticmethod
    def parse_phase(line):
        """Extract phase information from log line"""
        if "Building Phase" in line or "建设阶段" in line or "구축 단계" in line:
            return "building"
        elif "Evolution Phase" in line or "演化阶段" in line or "진화 단계" in line:
            return "evolution"
        return None
    
    @staticmethod
    def parse_hyperedge(line):
        """Extract hyperedge information from log line"""
        # Look for patterns like "Added hyperedge #N (size M): nodes"
        if "Added hyperedge" in line or "添加超边" in line:
            # Extract node IDs
            import re
            # Try to find pattern after colon
            if ':' in line:
                nodes_part = line.split(':', 1)[1].strip()
                nodes = nodes_part.split()
                return nodes
        return None
    
    @staticmethod
    def parse_progress(line):
        """Extract progress percentage from log line"""
        import re
        match = re.search(r'(\d+\.?\d*)%', line)
        if match:
            return float(match.group(1))
        return None
    
    @staticmethod
    def parse_iteration(line):
        """Extract iteration number from log line"""
        import re
        match = re.search(r'Iteration (\d+)[/:]', line)
        if match:
            return int(match.group(1))
        return None


class RealtimeMonitor:
    """Monitor generation process in real-time"""
    
    def __init__(self, callback=None):
        self.callback = callback
        self.is_monitoring = False
        self.monitor_thread = None
        self.message_queue = queue.Queue()
        
    def start_monitoring(self):
        """Start monitoring thread"""
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring thread"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
    
    def add_message(self, message):
        """Add message to queue"""
        self.message_queue.put(message)
    
    def _monitor_loop(self):
        """Monitor loop that processes messages"""
        while self.is_monitoring:
            try:
                message = self.message_queue.get(timeout=0.1)
                
                if self.callback:
                    self.callback(message)
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Monitor error: {e}")


class ConfigurationManager:
    """Manage GUI configuration and presets"""
    
    def __init__(self, config_file="gui_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        default_config = {
            'recent_files': {
                'config_files': [],
                'personas_files': [],
                'output_directories': []
            },
            'default_parameters': {
                'iterations': 10,
                'groups_per_iteration': 5,
                'max_members': 5,
                'model': 'gpt-4'
            },
            'ui_preferences': {
                'language': 'en',
                'theme': 'default'
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with default config
                    default_config.update(loaded_config)
        except Exception as e:
            print(f"Error loading config: {e}")
        
        return default_config
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def add_recent_file(self, file_type, file_path):
        """Add file to recent files list"""
        if file_type not in self.config['recent_files']:
            self.config['recent_files'][file_type] = []
        
        recent = self.config['recent_files'][file_type]
        
        # Remove if already exists
        if file_path in recent:
            recent.remove(file_path)
        
        # Add to front
        recent.insert(0, file_path)
        
        # Keep only last 10
        self.config['recent_files'][file_type] = recent[:10]
        
        self.save_config()
    
    def get_recent_files(self, file_type):
        """Get recent files of specified type"""
        return self.config['recent_files'].get(file_type, [])
    
    def update_default_parameters(self, params):
        """Update default parameters"""
        self.config['default_parameters'].update(params)
        self.save_config()
    
    def get_default_parameters(self):
        """Get default parameters"""
        return self.config['default_parameters'].copy()


class ValidationHelper:
    """Helper class for input validation"""
    
    @staticmethod
    def validate_positive_integer(value, min_val=1, max_val=None):
        """Validate positive integer input"""
        try:
            val = int(value)
            if val < min_val:
                return False, f"Value must be at least {min_val}"
            if max_val and val > max_val:
                return False, f"Value must not exceed {max_val}"
            return True, ""
        except ValueError:
            return False, "Must be a valid integer"
    
    @staticmethod
    def validate_float(value, min_val=None, max_val=None):
        """Validate float input"""
        try:
            val = float(value)
            if min_val is not None and val < min_val:
                return False, f"Value must be at least {min_val}"
            if max_val is not None and val > max_val:
                return False, f"Value must not exceed {max_val}"
            return True, ""
        except ValueError:
            return False, "Must be a valid number"
    
    @staticmethod
    def validate_file_exists(file_path):
        """Validate file exists"""
        if not file_path:
            return False, "File path is required"
        if not os.path.exists(file_path):
            return False, "File does not exist"
        return True, ""
    
    @staticmethod
    def validate_all_parameters(params):
        """Validate all parameters"""
        errors = []
        
        # Validate iterations
        valid, msg = ValidationHelper.validate_positive_integer(
            params.get('iterations', 10), min_val=1, max_val=100
        )
        if not valid:
            errors.append(f"Iterations: {msg}")
        
        # Validate groups per iteration
        valid, msg = ValidationHelper.validate_positive_integer(
            params.get('groups_per_iteration', 5), min_val=1, max_val=50
        )
        if not valid:
            errors.append(f"Groups per iteration: {msg}")
        
        # Validate max members
        valid, msg = ValidationHelper.validate_positive_integer(
            params.get('max_members', 5), min_val=2, max_val=20
        )
        if not valid:
            errors.append(f"Max members: {msg}")
        
        return len(errors) == 0, errors


if __name__ == "__main__":
    # Test advanced features
    print("Testing advanced features...")
    
    # Test progress tracker
    tracker = ProgressTracker()
    tracker.target_hyperedges = 100
    tracker.update_phase("building")
    
    for i in range(10):
        tracker.add_hyperedge([str(j) for j in range(i % 5 + 2)])
    
    stats = tracker.get_statistics()
    print(f"Statistics: {json.dumps(stats, indent=2)}")
    
    # Test configuration manager
    config_mgr = ConfigurationManager()
    config_mgr.add_recent_file('config_files', 'test_config.txt')
    print(f"Recent files: {config_mgr.get_recent_files('config_files')}")
    
    # Test validation
    valid, errors = ValidationHelper.validate_all_parameters({
        'iterations': '10',
        'groups_per_iteration': '5',
        'max_members': '3'
    })
    print(f"Validation result: {valid}, Errors: {errors}")

