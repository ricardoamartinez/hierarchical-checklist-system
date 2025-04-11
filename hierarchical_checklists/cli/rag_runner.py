#!/usr/bin/env python3

import os
import sys
import subprocess
import datetime
import json
from pathlib import Path
import re

# Get the root directory of the project
ROOT_DIR = Path(__file__).parent.parent.absolute()
BOOTSTRAP_DIR = ROOT_DIR / "bootstrap"
STEPS_DIR = ROOT_DIR / "steps"
SCRATCHPAD_DIR = ROOT_DIR / "scratchpad"
EXPECTED_DIR = ROOT_DIR / "expected"
LOCK_DIR = ROOT_DIR / "lock"

# Import the checklist utilities
sys.path.append(str(ROOT_DIR / "cli"))
from checklist_utils import (
    get_active_step,
    display_step,
    verify_step,
    mark_step_complete,
    log_thought,
    print_status,
    halt_with_reason,
    try_push,
    all_checkboxes_checked,
    no_pending_questions,
    checklist_incomplete,
    assert_not_locked,
    assert_current_file_is,
    set_current_step,
    create_lock_file,
    remove_lock_file,
    compute_file_hash,
    log_file_hash,
    verify_file_hashes
)

def exec_command(cmd):
    """Execute a shell command and display the output."""
    # Check if the system is locked
    assert_not_locked()

    print(f"Executing: {cmd}")
    try:
        # Log the command execution
        log_file = ROOT_DIR / "cli" / "command_log.txt"
        timestamp = datetime.datetime.now().isoformat()
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {cmd}\n")

        # Execute the command
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        # Log the output
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"STDOUT:\n{result.stdout}\n")
            if result.stderr:
                f.write(f"STDERR:\n{result.stderr}\n")
            f.write(f"Return code: {result.returncode}\n\n")

        # Display the output
        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        print(f"Return code: {result.returncode}")

        # If the command failed, create a lock file
        if result.returncode != 0:
            create_lock_file(f"Command failed: {cmd}")

        return result.returncode == 0
    except Exception as e:
        print(f"Error executing command: {e}")
        create_lock_file(f"Error executing command: {e}")
        return False

def move_to_next_step(current_step):
    """Move to the next step in the checklist."""
    # Ensure this is the current step
    assert_current_file_is(current_step)

    # Check if the system is locked
    assert_not_locked()

    # Verify current step is complete
    if not all_checkboxes_checked(current_step):
        print("🚫 Cannot move to next step. Current step has unchecked items.")
        create_lock_file("Incomplete checklist items")
        return

    if not no_pending_questions(current_step):
        print("🚫 Cannot move to next step. Current step has pending questions.")
        create_lock_file("Pending questions in checklist")
        return

    # Mark current step as complete
    mark_step_complete(current_step)

    # Find the next step
    next_step = get_active_step()
    if next_step:
        print(f"Moving to next step: {next_step}")
        # Set this as the current step
        set_current_step(next_step)
        # Log the file hash
        log_file_hash(next_step)
        # Display the step
        display_step(next_step)
    else:
        print("✅ All steps completed!")
        # Remove the lock file if it exists
        remove_lock_file()

def is_new_codebase():
    """
    Detect if this is a new codebase by checking for .git folder and counting files.
    Returns True if no .git folder, or fewer than 5 files in root (excluding CLI tools).
    """
    # Check if .git folder exists
    git_exists = os.path.exists(".git")

    # Count project files (excluding our CLI tools)
    project_files = [f for f in os.listdir('.') if f not in {'hierarchical_checklists', 'rag_tasks'}]
    few_files = len(project_files) <= 5

    return not git_exists or few_files

def generate_new_project_bootstrap_md():
    """
    Generate the NEW_PROJECT_INIT.md bootstrap file for new projects.
    """
    bootstrap_file = BOOTSTRAP_DIR / "NEW_PROJECT_INIT.md"
    with open(bootstrap_file, 'w', encoding='utf-8') as f:
        f.write("""# 🏗️ NEW PROJECT INITIALIZATION

## 🎯 Goal
Create a clean, scalable codebase skeleton using Hybrid XaaS design: full-stack monorepo with shared backend/frontend contracts, CI/CD, and service modularity.

## 🗂 Required Execution Tree
- [ ] STEP_01__Choose_Stack_and_Framework.md
- [ ] STEP_02__Scaffold_Directory_Structure.md
- [ ] STEP_03__Initialize_Monorepo_Tooling.md
- [ ] STEP_04__Define_Service_Contracts.md
- [ ] STEP_05__Setup_CI_CD.md
- [ ] STEP_06__Register_Model_Self_Checks.md

## 🚫 Failsafe Constraints
- [ ] No file mutation unless parent checklist step is complete
- [ ] No push until structure is validated
- [ ] No commit unless structure checks pass
- [ ] On uncertain logic: write pending question to `scratchpad/model_thoughts_todo.md` and halt

## 🧠 Internal Prompt: Checklist Writer
> "Write `STEP_01__Choose_Stack_and_Framework.md` with all subgoals and verification paths. This file will link to the next file in hierarchy based on each checklist item. Each subgoal must recursively generate its own `.md` child if complex."
""")
    print(f"Created new project bootstrap file: {bootstrap_file}")

    # Create the first step file
    step_file = STEPS_DIR / "STEP_01__Choose_Stack_and_Framework.md"
    with open(step_file, 'w', encoding='utf-8') as f:
        f.write("""# STEP 01: CHOOSE STACK AND FRAMEWORK
**Parent:** `NEW_PROJECT_INIT.md`
**Status:** ☐ In Progress

## 🧰 Stack Options (Choose one)
- [ ] Full Python (FastAPI + PyScript)
- [ ] JS/TS (Next.js + Express)
- [ ] Polyglot: Rust backend + Svelte frontend

## 📋 Step Verification Rules
- [ ] One stack option is selected
- [ ] Selection is documented in `STACK_SELECTION.md`
- [ ] Required dependencies are listed

## 📎 Notes
- 🧠 *Guidance:* Choose based on team expertise, performance needs, and development speed requirements.
- 🧠 *Pending:* Need to verify if any existing code has framework dependencies.
""")
    print(f"Created first step file: {step_file}")

    # Create the second step file
    step_file = STEPS_DIR / "STEP_02__Scaffold_Directory_Structure.md"
    with open(step_file, 'w', encoding='utf-8') as f:
        f.write("""# STEP 02: SCAFFOLD DIRECTORY STRUCTURE
**Parent:** `NEW_PROJECT_INIT.md`
**Status:** ☐ In Progress

## 📁 Task
Create the canonical Hybrid XaaS skeleton:

```
/src/
  frontend/      # React / Svelte / etc
  backend/       # FastAPI / Express / etc
  shared/        # Types/interfaces/schemas
/tests/          # Unit + integration tests
/scripts/        # Deployment, validation
/infra/          # Docker, Terraform, etc
rag_tasks/       # Autogenerated RAG checklists
```

## 📋 Checklist
- [ ] Create `/src/frontend`, `/src/backend`, `/src/shared`
- [ ] Create `/tests`, `/scripts`, `/infra`
- [ ] Add `README.md` in each folder with initial note
- [ ] Validate structure with `tree` command

## ✅ Validation
- Expected folders must exist with non-empty README
- Run `tree -d` and confirm against spec
""")
    print(f"Created second step file: {step_file}")

def initialize_project_structure():
    """
    Initialize the project structure for a new codebase.
    """
    print("🆕 New project detected. Bootstrapping clean Hybrid XaaS checklist...")

    # Create necessary directories if they don't exist
    for directory in [BOOTSTRAP_DIR, STEPS_DIR, SCRATCHPAD_DIR, EXPECTED_DIR, LOCK_DIR]:
        if not directory.exists():
            os.makedirs(directory)
            print(f"Created directory: {directory}")

    # Generate the new project bootstrap file
    if not (BOOTSTRAP_DIR / "NEW_PROJECT_INIT.md").exists():
        generate_new_project_bootstrap_md()
        # Create a lock file to prevent pushing until project is initialized
        lock_file = LOCK_DIR / ".model_push_lock"
        with open(lock_file, 'w', encoding='utf-8') as f:
            f.write("Locked: project not initialized\n")
            f.write(f"Timestamp: {datetime.datetime.now().isoformat()}\n")

    # Set the current step to the bootstrap file
    current_step_lock = LOCK_DIR / ".current_step.lock"
    with open(current_step_lock, 'w', encoding='utf-8') as f:
        f.write(str((BOOTSTRAP_DIR / "NEW_PROJECT_INIT.md").absolute()))

    # Create scratchpad files
    thoughts_file = SCRATCHPAD_DIR / "model_thoughts_todo.md"
    if not thoughts_file.exists():
        with open(thoughts_file, 'w', encoding='utf-8') as f:
            f.write("""# Model Thoughts and TODOs

## Pending Questions
- ❓ [YYYY-MM-DD] [Question about implementation or issue]

## Hypotheses
- 🧠 [YYYY-MM-DD] [Hypothesis about root cause]

## Action Items
- [ ] [YYYY-MM-DD] [Action to take]

## Resolved Items
- [x] [YYYY-MM-DD] [Resolved question or action]
""")
        print(f"Created thoughts file: {thoughts_file}")

    inconsistencies_file = SCRATCHPAD_DIR / "inconsistencies_pending.md"
    if not inconsistencies_file.exists():
        with open(inconsistencies_file, 'w', encoding='utf-8') as f:
            f.write("""# Inconsistencies and Pending Issues

## Unresolved Inconsistencies
- ⚠️ [YYYY-MM-DD] [Description of inconsistency]
  - **File:** [Path to file]
  - **Expected:** [Expected behavior]
  - **Actual:** [Actual behavior]

## Resolved Inconsistencies
- ✅ [YYYY-MM-DD] [Description of resolved inconsistency]
  - **File:** [Path to file]
  - **Resolution:** [How it was resolved]
""")
        print(f"Created inconsistencies file: {inconsistencies_file}")

    # Create hash log file if it doesn't exist
    hash_log = ROOT_DIR / ".checklist_hash_log"
    if not hash_log.exists():
        with open(hash_log, 'w', encoding='utf-8') as f:
            f.write("# Checklist File Hashes\n")
        print(f"Created hash log file: {hash_log}")

    # Create command log file if it doesn't exist
    command_log = ROOT_DIR / "cli" / "command_log.txt"
    if not command_log.exists():
        with open(command_log, 'w', encoding='utf-8') as f:
            f.write("# Command Execution Log\n")
        print(f"Created command log file: {command_log}")

    # Create git hooks
    hooks_dir = ROOT_DIR / ".git" / "hooks"
    if hooks_dir.exists():
        # Pre-commit hook
        pre_commit_hook = hooks_dir / "pre-commit"
        with open(pre_commit_hook, 'w', encoding='utf-8') as f:
            f.write("""#!/bin/bash
if [ -f lock/.model_push_lock ]; then
    echo "🚫 Commit blocked: Checklist state incomplete."
    exit 1
fi

python cli/validate_output.py || {
    echo "🚫 Output validation failed."
    exit 1
}
""")
        os.chmod(pre_commit_hook, 0o755)
        print(f"Created pre-commit hook: {pre_commit_hook}")

        # Pre-push hook
        pre_push_hook = hooks_dir / "pre-push"
        with open(pre_push_hook, 'w', encoding='utf-8') as f:
            f.write("""#!/bin/bash
if [ -f lock/.model_push_lock ]; then
    echo "🚫 Push blocked: Checklist state incomplete."
    exit 1
fi

python cli/validate_output.py || {
    echo "🚫 Output validation failed."
    exit 1
}
""")
        os.chmod(pre_push_hook, 0o755)
        print(f"Created pre-push hook: {pre_push_hook}")

def initialize_system():
    """Initialize the hierarchical checklist system."""
    # Create necessary directories if they don't exist
    for directory in [BOOTSTRAP_DIR, STEPS_DIR, SCRATCHPAD_DIR, EXPECTED_DIR, LOCK_DIR]:
        if not directory.exists():
            os.makedirs(directory)
            print(f"Created directory: {directory}")

    # Check if this is a new codebase
    if is_new_codebase():
        initialize_project_structure()
        return

    # Create initial files if they don't exist
    # Bootstrap file
    bootstrap_file = BOOTSTRAP_DIR / "000_BOOTSTRAP_FIX_INIT.md"
    if not bootstrap_file.exists():
        with open(bootstrap_file, 'w', encoding='utf-8') as f:
            f.write("""# 📍 FIX INITIATOR: [Issue Title]

## 🔧 Issue Summary
[Detailed description of the issue to be fixed]

## 🎨 Objective
Autonomously generate and execute a fail-safe fix pipeline for this issue, using hierarchical checklists. Ensure **no deviation**, **no hallucinated validation**, **no premature exit**.

## 🗂 Required Execution Tree
- [ ] STEP_01__DEFINE_FIX_STRATEGY.md
- [ ] STEP_02__TRACE_SIGNAL_PATH.md
- [ ] STEP_03__ISOLATE_ISSUE.md
- [ ] STEP_04__IMPLEMENT_FIX.md
- [ ] STEP_05__VALIDATE_FIX.md
- [ ] STEP_06__CLEANUP_AND_PUSH.md

## 🚫 Failsafe Constraints
- [ ] No file mutation unless parent checklist step is complete
- [ ] No push unless validation confirms fix
- [ ] No commit unless tests pass
- [ ] On uncertain logic: write pending question to `scratchpad/model_thoughts_todo.md` and halt

## 🧠 Internal Prompt: Checklist Writer
> "Write `STEP_01__DEFINE_FIX_STRATEGY.md` with all subgoals and verification paths. This file will link to the next file in hierarchy based on each checklist item. Each subgoal must recursively generate its own `.md` child if complex."
""")
        print(f"Created bootstrap file: {bootstrap_file}")

    # Scratchpad files
    thoughts_file = SCRATCHPAD_DIR / "model_thoughts_todo.md"
    if not thoughts_file.exists():
        with open(thoughts_file, 'w', encoding='utf-8') as f:
            f.write("""# Model Thoughts and TODOs

## Pending Questions
- ❓ [YYYY-MM-DD] [Question about implementation or issue]

## Hypotheses
- 🧠 [YYYY-MM-DD] [Hypothesis about root cause]

## Action Items
- [ ] [YYYY-MM-DD] [Action to take]

## Resolved Items
- [x] [YYYY-MM-DD] [Resolved question or action]
""")
        print(f"Created thoughts file: {thoughts_file}")

    inconsistencies_file = SCRATCHPAD_DIR / "inconsistencies_pending.md"
    if not inconsistencies_file.exists():
        with open(inconsistencies_file, 'w', encoding='utf-8') as f:
            f.write("""# Inconsistencies and Pending Issues

## Unresolved Inconsistencies
- ⚠️ [YYYY-MM-DD] [Description of inconsistency]
  - **File:** [Path to file]
  - **Expected:** [Expected behavior]
  - **Actual:** [Actual behavior]

## Resolved Inconsistencies
- ✅ [YYYY-MM-DD] [Description of resolved inconsistency]
  - **File:** [Path to file]
  - **Resolution:** [How it was resolved]
""")
        print(f"Created inconsistencies file: {inconsistencies_file}")

    # Create hash log file if it doesn't exist
    hash_log = ROOT_DIR / ".checklist_hash_log"
    if not hash_log.exists():
        with open(hash_log, 'w', encoding='utf-8') as f:
            f.write("# Checklist File Hashes\n")
        print(f"Created hash log file: {hash_log}")

    # Create command log file if it doesn't exist
    command_log = ROOT_DIR / "cli" / "command_log.txt"
    if not command_log.exists():
        with open(command_log, 'w', encoding='utf-8') as f:
            f.write("# Command Execution Log\n")
        print(f"Created command log file: {command_log}")

    # Create git hooks
    hooks_dir = ROOT_DIR / ".git" / "hooks"
    if hooks_dir.exists():
        # Pre-commit hook
        pre_commit_hook = hooks_dir / "pre-commit"
        with open(pre_commit_hook, 'w', encoding='utf-8') as f:
            f.write("""#!/bin/bash
if [ -f lock/.model_push_lock ]; then
    echo "🚫 Commit blocked: Checklist state incomplete."
    exit 1
fi

python cli/validate_output.py || {
    echo "🚫 Output validation failed."
    exit 1
}
""")
        os.chmod(pre_commit_hook, 0o755)
        print(f"Created pre-commit hook: {pre_commit_hook}")

        # Pre-push hook
        pre_push_hook = hooks_dir / "pre-push"
        with open(pre_push_hook, 'w', encoding='utf-8') as f:
            f.write("""#!/bin/bash
if [ -f lock/.model_push_lock ]; then
    echo "🚫 Push blocked: Checklist state incomplete."
    exit 1
fi

python cli/validate_output.py || {
    echo "🚫 Output validation failed."
    exit 1
}
""")
        os.chmod(pre_push_hook, 0o755)
        print(f"Created pre-push hook: {pre_push_hook}")

def main():
    """Main function to run the RAG Task Checklist System."""
    print("🔄 RAG Task Checklist System")
    print("=" * 50)

    # Ask for the codebase directory
    codebase_dir = input("Enter the path to your codebase directory (or press Enter to use current directory): ").strip()
    if codebase_dir:
        try:
            os.chdir(codebase_dir)
            print(f"Changed to directory: {codebase_dir}")
        except Exception as e:
            print(f"Error changing to directory: {e}")
            sys.exit(1)

    # Initialize the system - this will detect if it's a new codebase
    initialize_system()

    # Verify file hashes to detect tampering
    if not verify_file_hashes():
        create_lock_file("File tampering detected")
        sys.exit(1)

    # Determine which bootstrap file to use
    if is_new_codebase():
        bootstrap_file = BOOTSTRAP_DIR / "NEW_PROJECT_INIT.md"
    else:
        bootstrap_file = BOOTSTRAP_DIR / "000_BOOTSTRAP_FIX_INIT.md"

    # Check if bootstrap file exists
    if not bootstrap_file.exists():
        print(f"❌ Bootstrap file not found: {bootstrap_file}")
        sys.exit(1)

    # Get the active step
    current_step = get_active_step()
    if not current_step:
        print("✅ All steps completed or no steps defined.")
        sys.exit(0)

    print(f"📋 Current active step: {current_step}")
    display_step(current_step)

    # Main command loop
    while True:
        cmd = input("\n>> ").strip()

        if cmd == "next":
            move_to_next_step(current_step)
            current_step = get_active_step()
        elif cmd == "log":
            thought = input("Enter thought: ")
            log_thought(thought)
        elif cmd == "verify":
            if verify_step(current_step):
                print("✅ Step verified successfully!")
            else:
                print("❌ Step verification failed.")
        elif cmd == "status":
            print_status()
        elif cmd == "halt":
            reason = input("Enter reason for halting: ")
            halt_with_reason(reason)
        elif cmd.startswith("exec "):
            exec_command(cmd[5:])
        elif cmd == "push":
            try_push()
        elif cmd == "help":
            print("""
Available commands:
  next    - Move to the next step
  log     - Log a thought or question
  verify  - Verify the current step
  status  - Show the status of all steps
  halt    - Halt execution with a reason
  exec    - Execute a shell command
  push    - Push changes if all conditions are met
  help    - Show this help message
  exit    - Exit the program
            """)
        elif cmd == "exit":
            print("Exiting RAG Task Checklist System.")
            break
        else:
            print("Invalid command. Type 'help' for available commands.")

if __name__ == "__main__":
    main()
