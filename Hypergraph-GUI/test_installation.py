"""
Installation and dependency test script
Run this to verify GUI installation and dependencies
"""

import sys
import os
from pathlib import Path


def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need 3.7+")
        return False


def check_tkinter():
    """Check if tkinter is available"""
    print("\nChecking tkinter...")
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.destroy()
        print("✅ tkinter - OK")
        return True
    except ImportError:
        print("❌ tkinter - NOT FOUND")
        print("   Install: sudo apt-get install python3-tk (Ubuntu/Debian)")
        print("           or: brew install python-tk (macOS)")
        return False


def check_required_files():
    """Check if required files exist"""
    print("\nChecking required files...")
    required_files = [
        "main.py",
        "languages.json",
        "visualization.py",
        "utils.py",
        "advanced_features.py",
        "styles.json",
        "requirements.txt",
        "README.md"
    ]
    
    all_exist = True
    for file in required_files:
        file_path = Path(__file__).parent / file
        if file_path.exists():
            print(f"✅ {file} - Found")
        else:
            print(f"❌ {file} - NOT FOUND")
            all_exist = False
    
    return all_exist


def check_parent_modules():
    """Check if parent HyperLLM modules are accessible"""
    print("\nChecking parent modules...")
    
    parent_dir = Path(__file__).parent.parent
    modules_to_check = [
        ("Hypergraph-Generator", "LLM_MAS_Hypergraph_Configuration.py"),
        ("Hypergraph-Evaluation", "hypergraph_evaluation_main.py"),
        ("Hypergraph-Entity", "entity_generator.py")
    ]
    
    all_exist = True
    for module_dir, script in modules_to_check:
        script_path = parent_dir / module_dir / script
        if script_path.exists():
            print(f"✅ {module_dir}/{script} - Found")
        else:
            print(f"⚠️  {module_dir}/{script} - NOT FOUND")
            all_exist = False
    
    return all_exist


def check_optional_dependencies():
    """Check optional dependencies"""
    print("\nChecking optional dependencies...")
    
    optional = {
        'matplotlib': 'For advanced visualization',
        'numpy': 'For numerical operations'
    }
    
    for package, purpose in optional.items():
        try:
            __import__(package)
            print(f"✅ {package} - Installed ({purpose})")
        except ImportError:
            print(f"ℹ️  {package} - Not installed ({purpose})")


def check_api_configuration():
    """Check API key configuration"""
    print("\nChecking API configuration...")
    
    parent_dir = Path(__file__).parent.parent
    api_key_file = parent_dir / "Hypergraph-Generator" / "api-key.txt"
    
    if api_key_file.exists():
        print("✅ api-key.txt - Found")
        
        # Check if OPENAI_BASE_URL is set
        base_url = os.environ.get("OPENAI_BASE_URL")
        if base_url:
            print(f"✅ OPENAI_BASE_URL - Set ({base_url})")
        else:
            print("⚠️  OPENAI_BASE_URL - Not set")
            print("   Set with: export OPENAI_BASE_URL='your-api-url'")
            return False
        return True
    else:
        print("❌ api-key.txt - NOT FOUND")
        print(f"   Create file at: {api_key_file}")
        return False


def test_json_loading():
    """Test loading JSON configuration files"""
    print("\nTesting JSON file loading...")
    
    json_files = ["languages.json", "styles.json"]
    all_ok = True
    
    for json_file in json_files:
        try:
            import json
            file_path = Path(__file__).parent / json_file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ {json_file} - Valid JSON ({len(data)} keys)")
        except Exception as e:
            print(f"❌ {json_file} - Error: {e}")
            all_ok = False
    
    return all_ok


def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("HyperLLM GUI Installation Test")
    print("="*60)
    
    results = []
    
    results.append(("Python Version", check_python_version()))
    results.append(("tkinter", check_tkinter()))
    results.append(("Required Files", check_required_files()))
    results.append(("Parent Modules", check_parent_modules()))
    results.append(("JSON Files", test_json_loading()))
    
    check_optional_dependencies()
    results.append(("API Configuration", check_api_configuration()))
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:25} {status}")
        if not result:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 All tests passed! You're ready to use the GUI.")
        print("\nTo start the GUI, run:")
        print("  python main.py")
        print("\nOr use the launcher:")
        print("  Windows: launch_gui.bat")
        print("  Linux/Mac: bash launch_gui.sh")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\nRefer to README.md for installation instructions.")
    
    print()


if __name__ == "__main__":
    run_all_tests()

