import os
import sys
from pathlib import Path

# Initialize verification script for project setup.
def check_python_version():
    """Verify Python 3.11+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Python 3.11+ required. You have {version.major}.{version.minor}")
        return False
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

# Initialize Python version and dependency checks.
def check_dependencies():
    """Verify required packages are installed"""
    required = [
        "chromadb",
        "sentence_transformers",
        "langchain",
        "pydantic",
    ]
    
    all_ok = True
    for package in required:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"❌ {package} not installed")
            all_ok = False
    
    if not all_ok:
        print("\nInstall with: pip install -r requirements.txt")
    return all_ok

# Initialize rule document checks.
def check_project_structure():
    """Verify project folders exist"""
    required_dirs = [
        "src",
        "rules",
        "data",
    ]
    
    all_ok = True
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✓ {directory}/")
        else:
            print(f"❌ Missing directory: {directory}/")
            all_ok = False
    
    return all_ok

# Initialize essential core file checks.
def check_core_files():
    """Verify essential files exist"""
    required_files = [
        "main.py",
        "requirements.txt",
        "README.md",
        "QUICKSTART.md",
        "src/__init__.py",
        "src/rag_pipeline.py",
        "src/vector_store/__init__.py",
        "src/embeddings.py",
        "src/document_loader/__init__.py",
    ]
    # Check each required file and report its status.
    all_ok = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"❌ Missing file: {file}")
            all_ok = False
    
    return all_ok

# Initialize rule document checks.
def check_rule_documents():
    """Verify rule documents exist"""
    rules_dir = Path("rules")
    
    if not rules_dir.exists():
        print("❌ rules/ directory does not exist")
        return False
    
    rule_files = list(rules_dir.glob("*.md")) + list(rules_dir.glob("*.txt"))
    
    if rule_files:
        print(f"✓ Found {len(rule_files)} rule documents:")
        for f in rule_files:
            print(f"  - {f.name}")
        return True
    else:
        print("⚠ No rule documents found in rules/")
        print("  Add .md or .txt files to rules/ directory")
        return False

# Initialize import checks.
def check_imports():
    """Verify core modules can be imported"""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from src.rag_pipeline import RAGPipeline
        print("✓ src.rag_pipeline imports successfully")
        
        from src.vector_store import VectorStoreManager
        print("✓ src.vector_store imports successfully")
        
        from src.embeddings import EmbeddingManager
        print("✓ src.embeddings imports successfully")
        
        from src.document_loader import DocumentLoader
        print("✓ src.document_loader imports successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

# Initialize main verification routine.
def main():
    """Run all verification checks"""
    print("=" * 60)
    print("TOW ARBITER - SETUP VERIFICATION")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Project Structure", check_project_structure),
        ("Core Files", check_core_files),
        ("Rule Documents", check_rule_documents),
        ("Module Imports", check_imports),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{'─' * 60}")
        print(f"{name}:")
        print('─' * 60)
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error during check: {e}")
            results.append((name, False))
    
    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = all(result for _, result in results)
    
    for name, result in results:
        status = "✓" if result else "❌"
        print(f"{status} {name}")
    
    print()
    if all_passed:
        print("✓ All checks passed! Ready to run:")
        print("  python main.py")
    else:
        print("❌ Some checks failed. See above for details.")
        print()
        print("Common fixes:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Add rule files to rules/ directory")
        print("3. Verify Python 3.11+ is installed")
    
    return all_passed

# Entry point for the verification script.
if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
