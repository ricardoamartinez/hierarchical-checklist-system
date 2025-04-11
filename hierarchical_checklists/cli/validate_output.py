#!/usr/bin/env python3

import os
import sys
import json
import re
import subprocess
from pathlib import Path

# Get the root directory of the project
ROOT_DIR = Path(__file__).parent.parent.absolute()
BOOTSTRAP_DIR = ROOT_DIR / "bootstrap"
STEPS_DIR = ROOT_DIR / "steps"
SCRATCHPAD_DIR = ROOT_DIR / "scratchpad"
EXPECTED_DIR = ROOT_DIR / "expected"
LOCK_DIR = ROOT_DIR / "lock"

def log_inconsistency(inconsistency, file_path):
    """Log an inconsistency to the inconsistencies_pending.md file."""
    inconsistencies_file = SCRATCHPAD_DIR / "inconsistencies_pending.md"
    
    with open(inconsistencies_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add the inconsistency under Unresolved Inconsistencies
    import datetime
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    new_inconsistency = f"- ⚠️ [{today}] Validation failed\n"
    new_inconsistency += f"  - **File:** {file_path}\n"
    new_inconsistency += f"  - **Details:** {inconsistency}\n"
    
    # Insert after the Unresolved Inconsistencies header
    content = re.sub(
        r'## Unresolved Inconsistencies\n',
        f'## Unresolved Inconsistencies\n{new_inconsistency}',
        content
    )
    
    with open(inconsistencies_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"⚠️ Logged inconsistency for {file_path}")

def create_lock_file(reason):
    """Create a lock file with the given reason."""
    lock_file = LOCK_DIR / ".model_push_lock"
    import datetime
    with open(lock_file, 'w', encoding='utf-8') as f:
        f.write(f"Locked: {reason}\n")
        f.write(f"Timestamp: {datetime.datetime.now().isoformat()}\n")
    
    print(f"🔒 System locked: {reason}")

def validate_expected_outputs():
    """Validate all expected outputs."""
    # Get all expected output files
    expected_output_files = list(EXPECTED_DIR.glob("EXPECTED_OUTPUT_*.json"))
    if not expected_output_files:
        print("No expected output files found.")
        return True
    
    all_valid = True
    
    for expected_output_file in expected_output_files:
        print(f"Validating: {expected_output_file}")
        
        try:
            with open(expected_output_file, 'r', encoding='utf-8') as f:
                expected_output = json.load(f)
            
            # Extract the step number
            match = re.match(r'EXPECTED_OUTPUT_(\d+)\.json', expected_output_file.name)
            if not match:
                print(f"❌ Invalid expected output file name: {expected_output_file.name}")
                all_valid = False
                continue
            
            step_num = match.group(1)
            step_files = list(STEPS_DIR.glob(f"STEP_{step_num}__*.md"))
            if not step_files:
                print(f"❌ No step file found for step {step_num}")
                all_valid = False
                continue
            
            step_file = step_files[0]
            
            # Check for required validation commands
            if "validation_commands" in expected_output:
                for cmd in expected_output["validation_commands"]:
                    print(f"Running validation command: {cmd}")
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        print("❌ Validation command failed:")
                        print(result.stdout)
                        print(result.stderr)
                        
                        # Log the inconsistency
                        inconsistency = f"Validation command failed: {cmd}\n"
                        inconsistency += f"Output:\n{result.stdout}\n{result.stderr}"
                        log_inconsistency(inconsistency, step_file)
                        
                        all_valid = False
            
            # Check for expected logs
            if "expected_logs" in expected_output:
                log_file = ROOT_DIR / "cli" / "command_log.txt"
                if not log_file.exists():
                    print(f"❌ Log file not found: {log_file}")
                    all_valid = False
                    continue
                
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                
                for expected_log in expected_output["expected_logs"]:
                    if expected_log not in log_content:
                        print(f"❌ Expected log not found: {expected_log}")
                        
                        # Log the inconsistency
                        inconsistency = f"Expected log not found: {expected_log}"
                        log_inconsistency(inconsistency, step_file)
                        
                        all_valid = False
            
            # Check for expected return code
            if "expected_return_code" in expected_output:
                # TODO: Implement return code checking
                pass
            
            # Check for expected frame count
            if "expected_frame_count" in expected_output:
                # TODO: Implement frame count checking
                pass
            
        except Exception as e:
            print(f"❌ Error validating expected output: {e}")
            all_valid = False
    
    return all_valid

def main():
    """Main function to validate outputs."""
    print("🔍 Validating outputs...")
    
    # Validate expected outputs
    if not validate_expected_outputs():
        print("❌ Validation failed.")
        create_lock_file("Output validation failed")
        return 1
    
    print("✅ All validations passed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
