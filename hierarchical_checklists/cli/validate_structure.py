#!/usr/bin/env python3

import os
import sys
from pathlib import Path

def validate_directory_structure():
    """
    Validate the directory structure for a new project.
    Returns True if the structure is valid, False otherwise.
    """
    # Required directories
    required_dirs = [
        "src/frontend",
        "src/backend",
        "src/shared",
        "tests",
        "scripts",
        "infra"
    ]
    
    # Check if all required directories exist
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print("❌ Missing directories:")
        for dir_path in missing_dirs:
            print(f"  - {dir_path}")
        return False
    
    # Check if all directories have a README.md file
    missing_readmes = []
    for dir_path in required_dirs:
        readme_path = os.path.join(dir_path, "README.md")
        if not os.path.exists(readme_path):
            missing_readmes.append(readme_path)
        else:
            # Check if README is empty
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    missing_readmes.append(f"{readme_path} (empty)")
    
    if missing_readmes:
        print("❌ Missing or empty README.md files:")
        for readme_path in missing_readmes:
            print(f"  - {readme_path}")
        return False
    
    print("✅ Directory structure is valid!")
    return True

def main():
    """Main function to validate the directory structure."""
    print("🔍 Validating directory structure...")
    
    if validate_directory_structure():
        print("✅ All checks passed.")
        return 0
    else:
        print("❌ Validation failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
