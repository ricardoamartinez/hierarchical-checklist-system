#!/usr/bin/env python3

import os
import re
import sys
import subprocess
import datetime
import hashlib
import json
from pathlib import Path

# Get the root directory of the project
ROOT_DIR = Path(__file__).parent.parent.absolute()
BOOTSTRAP_DIR = ROOT_DIR / "bootstrap"
STEPS_DIR = ROOT_DIR / "steps"
SCRATCHPAD_DIR = ROOT_DIR / "scratchpad"
EXPECTED_DIR = ROOT_DIR / "expected"
LOCK_DIR = ROOT_DIR / "lock"

def assert_not_locked():
    """
    Check if the system is locked and exit if it is.
    """
    lock_file = LOCK_DIR / ".model_push_lock"
    if lock_file.exists():
        with open(lock_file, 'r', encoding='utf-8') as f:
            reason = f.read().strip()
        print(f"❌ Operation blocked: {reason}")
        sys.exit(1)

def assert_current_file_is(path):
    """
    Check if the given path is the current active step.
    """
    current_step_lock = LOCK_DIR / ".current_step.lock"
    if not current_step_lock.exists():
        print("❌ No current step defined.")
        sys.exit(1)

    with open(current_step_lock, 'r', encoding='utf-8') as f:
        current = f.read().strip()

    if os.path.abspath(path) != os.path.abspath(current):
        print(f"❌ Access denied: {path} is not the current active checklist.")
        print(f"Current active step is: {current}")
        sys.exit(1)

def set_current_step(step_file):
    """
    Set the current active step.
    """
    current_step_lock = LOCK_DIR / ".current_step.lock"
    with open(current_step_lock, 'w', encoding='utf-8') as f:
        f.write(str(step_file.absolute()))

def create_lock_file(reason):
    """
    Create a lock file with the given reason.
    """
    lock_file = LOCK_DIR / ".model_push_lock"
    with open(lock_file, 'w', encoding='utf-8') as f:
        f.write(f"Locked: {reason}\n")
        f.write(f"Timestamp: {datetime.datetime.now().isoformat()}\n")

    print(f"🔒 System locked: {reason}")

def remove_lock_file():
    """
    Remove the lock file if it exists.
    """
    lock_file = LOCK_DIR / ".model_push_lock"
    if lock_file.exists():
        os.remove(lock_file)
        print("🔓 System unlocked.")

def compute_file_hash(file_path):
    """
    Compute the SHA256 hash of a file.
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def log_file_hash(file_path):
    """
    Log the hash of a file to the hash log.
    """
    hash_log = ROOT_DIR / ".checklist_hash_log"
    file_hash = compute_file_hash(file_path)
    timestamp = datetime.datetime.now().isoformat()
    log_entry = f"{timestamp} {file_path} {file_hash}\n"

    with open(hash_log, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def verify_file_hashes():
    """
    Verify all file hashes in the hash log.
    """
    hash_log = ROOT_DIR / ".checklist_hash_log"
    if not hash_log.exists():
        return True

    with open(hash_log, 'r', encoding='utf-8') as f:
        log_entries = f.readlines()

    for entry in log_entries:
        parts = entry.strip().split()
        if len(parts) >= 3:
            file_path = parts[1]
            recorded_hash = parts[2]

            if os.path.exists(file_path):
                current_hash = compute_file_hash(file_path)
                if current_hash != recorded_hash:
                    print(f"❌ File hash mismatch: {file_path}")
                    print(f"Recorded: {recorded_hash}")
                    print(f"Current: {current_hash}")
                    return False

    return True

def get_active_step():
    """
    Parse the bootstrap file and return the first incomplete step.
    If all steps are complete, return None.
    """
    # Verify file hashes to detect tampering
    if not verify_file_hashes():
        create_lock_file("File tampering detected")
        sys.exit(1)

    # Determine which bootstrap file to use
    new_project_bootstrap = BOOTSTRAP_DIR / "NEW_PROJECT_INIT.md"
    fix_bootstrap = BOOTSTRAP_DIR / "000_BOOTSTRAP_FIX_INIT.md"

    if new_project_bootstrap.exists():
        bootstrap_file = new_project_bootstrap
    elif fix_bootstrap.exists():
        bootstrap_file = fix_bootstrap
    else:
        print(f"❌ No bootstrap file found.")
        return None

    with open(bootstrap_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the Required Execution Tree section
    tree_section = re.search(r'## 🗂 Required Execution Tree(.*?)##', content, re.DOTALL)
    if not tree_section:
        print("❌ Required Execution Tree section not found in bootstrap file.")
        return None

    # Extract the steps
    steps = re.findall(r'- \[([ x])\] (STEP_\d+__.*?\.md)', tree_section.group(1))

    # Find the first incomplete step
    for checked, step in steps:
        if checked == ' ':  # Unchecked
            step_file = STEPS_DIR / step
            if not step_file.exists():
                # Create the step file if it doesn't exist
                create_step_file(step)

            # Set this as the current step
            set_current_step(step_file)

            # Log the file hash
            log_file_hash(step_file)

            return step_file

    return None

def create_step_file(step_name):
    """Create a new step file with the given name."""
    step_file = STEPS_DIR / step_name

    # Extract the step number and description
    match = re.match(r'STEP_(\d+)__(.*?)\.md', step_name)
    if not match:
        print(f"❌ Invalid step name format: {step_name}")
        return

    step_num = match.group(1)
    step_desc = match.group(2).replace('_', ' ')

    # Determine which bootstrap file to use as parent
    new_project_bootstrap = BOOTSTRAP_DIR / "NEW_PROJECT_INIT.md"
    fix_bootstrap = BOOTSTRAP_DIR / "000_BOOTSTRAP_FIX_INIT.md"

    if new_project_bootstrap.exists():
        parent = "NEW_PROJECT_INIT.md"
    else:
        parent = "000_BOOTSTRAP_FIX_INIT.md"

    # Create content based on step number
    if step_num == "01" and parent == "NEW_PROJECT_INIT.md":
        # This is the first step for a new project
        content = f"""# STEP {step_num}: {step_desc}
**Parent:** `{parent}`
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
"""
    elif step_num == "02" and parent == "NEW_PROJECT_INIT.md":
        # This is the second step for a new project
        content = f"""# STEP {step_num}: {step_desc}
**Parent:** `{parent}`
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
"""
    else:
        # Default template for other steps
        content = f"""# STEP {step_num}: {step_desc}
**Parent:** `{parent}`
**Status:** ☐ In Progress

## ⬇️ Substeps
- [ ] Analyze the issue
- [ ] Identify potential solutions
- [ ] Select the best approach

## 📋 Step Verification Rules
- [ ] All substeps are complete
- [ ] No pending questions in scratchpad

## 📎 Notes
- 🧠 *Initial thoughts:* This step needs to be completed before moving to the next one.
"""

    with open(step_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ Created step file: {step_file}")

def display_step(step_file):
    """Display the content of a step file."""
    if not step_file.exists():
        print(f"❌ Step file not found: {step_file}")
        return

    with open(step_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print("\n" + "=" * 50)
    print(content)
    print("=" * 50)

def all_checkboxes_checked(step_file):
    """Check if all checkboxes in a step file are checked."""
    if not step_file.exists():
        return False

    with open(step_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all checkboxes
    checkboxes = re.findall(r'- \[([ x])\]', content)

    # Check if all are checked
    return all(c == 'x' for c in checkboxes)

def no_pending_questions(step_file):
    """Check if there are no pending questions in the step file."""
    if not step_file.exists():
        return False

    with open(step_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for pending questions (❓)
    return '❓' not in content

def validate_expected_output(step_file):
    """Validate the expected output for a step."""
    # Extract the step number
    match = re.match(r'STEP_(\d+)__.*?\.md', step_file.name)
    if not match:
        print(f"❌ Invalid step name format: {step_file.name}")
        return False

    step_num = match.group(1)
    expected_output_file = EXPECTED_DIR / f"EXPECTED_OUTPUT_{step_num}.json"

    if not expected_output_file.exists():
        print(f"⚠️ No expected output file found: {expected_output_file}")
        return True  # Not all steps require validation

    try:
        with open(expected_output_file, 'r', encoding='utf-8') as f:
            expected_output = json.load(f)

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

                    return False

        # Check for expected logs
        if "expected_logs" in expected_output:
            # TODO: Implement log checking
            pass

        return True
    except Exception as e:
        print(f"❌ Error validating expected output: {e}")
        return False

def log_inconsistency(inconsistency, file_path):
    """Log an inconsistency to the inconsistencies_pending.md file."""
    inconsistencies_file = SCRATCHPAD_DIR / "inconsistencies_pending.md"

    with open(inconsistencies_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add the inconsistency under Unresolved Inconsistencies
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

def verify_step(step_file):
    """Verify a step and mark it as complete if all checks pass."""
    # Ensure this is the current step
    assert_current_file_is(step_file)

    if not step_file.exists():
        print(f"❌ Step file not found: {step_file}")
        return False

    # Check if all checkboxes are checked
    if not all_checkboxes_checked(step_file):
        print("❌ Not all checkboxes are checked.")
        create_lock_file("Incomplete checklist items")
        return False

    # Check if there are no pending questions
    if not no_pending_questions(step_file):
        print("❌ There are pending questions in the step file.")
        create_lock_file("Pending questions in checklist")
        return False

    # Check for child steps
    child_steps = get_child_steps(step_file)
    for child_step in child_steps:
        child_path = STEPS_DIR / child_step
        if not child_path.exists():
            print(f"❌ Child step not found: {child_step}")
            create_lock_file(f"Missing child step: {child_step}")
            return False

        if not is_step_complete(child_path):
            print(f"❌ Child step not complete: {child_step}")
            create_lock_file(f"Incomplete child step: {child_step}")
            return False

    # Validate expected output
    if not validate_expected_output(step_file):
        print("❌ Expected output validation failed.")
        create_lock_file("Expected output validation failed")
        return False

    # Check for unexpected git diffs
    result = subprocess.run(["git", "diff", "--exit-code"], capture_output=True)
    if result.returncode != 0:
        print("⚠️ Uncommitted changes detected in git working tree.")
        # This is just a warning, not a blocker

    # Mark the step as complete
    mark_step_complete(step_file)

    # Remove the lock file if it exists
    remove_lock_file()

    return True

def get_child_steps(step_file):
    """Get all child steps referenced in a step file."""
    if not step_file.exists():
        return []

    with open(step_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all references to child steps
    # Format: [STEP_01A__*.md](./STEP_01A__*.md)
    child_steps = re.findall(r'\[(STEP_\d+[A-Z]__.*?\.md)\]\(\./\1\)', content)
    return child_steps

def is_step_complete(step_file):
    """Check if a step is marked as complete."""
    if not step_file.exists():
        return False

    with open(step_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if the status is marked as complete
    return "**Status:** ✅ Complete" in content

def mark_step_complete(step_file):
    """Mark a step as complete in the bootstrap file."""
    if not step_file.exists():
        print(f"❌ Step file not found: {step_file}")
        return

    # Update the step file status
    with open(step_file, 'r', encoding='utf-8') as f:
        content = f.read()

    content = re.sub(r'\*\*Status:\*\* ☐ In Progress', '**Status:** ✅ Complete', content)

    with open(step_file, 'w', encoding='utf-8') as f:
        f.write(content)

    # Update the bootstrap file
    bootstrap_file = BOOTSTRAP_DIR / "000_BOOTSTRAP_FIX_INIT.md"
    if not bootstrap_file.exists():
        print(f"❌ Bootstrap file not found: {bootstrap_file}")
        return

    with open(bootstrap_file, 'r', encoding='utf-8') as f:
        content = f.read()

    step_name = step_file.name
    content = re.sub(
        f'- \\[ \\] {step_name}',
        f'- [x] {step_name}',
        content
    )

    with open(bootstrap_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ Marked step as complete: {step_file.name}")

def log_thought(thought):
    """Log a thought to the model_thoughts_todo.md file."""
    thoughts_file = SCRATCHPAD_DIR / "model_thoughts_todo.md"

    with open(thoughts_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add the thought under Pending Questions
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    new_thought = f"- ❓ [{today}] {thought}\n"

    # Insert after the Pending Questions header
    content = re.sub(
        r'## Pending Questions\n',
        f'## Pending Questions\n{new_thought}',
        content
    )

    with open(thoughts_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ Logged thought: {thought}")

def print_status():
    """Print the status of all steps."""
    bootstrap_file = BOOTSTRAP_DIR / "000_BOOTSTRAP_FIX_INIT.md"
    if not bootstrap_file.exists():
        print(f"❌ Bootstrap file not found: {bootstrap_file}")
        return

    with open(bootstrap_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the Required Execution Tree section
    tree_section = re.search(r'## 🗂 Required Execution Tree(.*?)##', content, re.DOTALL)
    if not tree_section:
        print("❌ Required Execution Tree section not found in bootstrap file.")
        return

    # Extract the steps
    steps = re.findall(r'- \[([ x])\] (STEP_\d+__.*?\.md)', tree_section.group(1))

    print("\n📋 Step Status:")
    for checked, step in steps:
        status = "✅ Complete" if checked == 'x' else "☐ Incomplete"
        print(f"  {status} - {step}")

    # Check for pending thoughts
    thoughts_file = SCRATCHPAD_DIR / "model_thoughts_todo.md"
    with open(thoughts_file, 'r', encoding='utf-8') as f:
        thoughts_content = f.read()

    pending_questions = re.findall(r'- ❓ \[\d{4}-\d{2}-\d{2}\] (.*)', thoughts_content)
    if pending_questions:
        print("\n❓ Pending Questions:")
        for question in pending_questions:
            print(f"  - {question}")

def halt_with_reason(reason):
    """Halt execution with a reason."""
    lock_file = LOCK_DIR / ".model_push_lock"

    with open(lock_file, 'w', encoding='utf-8') as f:
        f.write(f"Halted: {reason}\n")
        f.write(f"Timestamp: {datetime.datetime.now().isoformat()}\n")

    print(f"🛑 Halted: {reason}")
    print("A lock file has been created to prevent pushing.")

def try_push():
    """Try to push changes if all conditions are met."""
    # Check if the system is locked
    lock_file = LOCK_DIR / ".model_push_lock"
    if lock_file.exists():
        with open(lock_file, 'r', encoding='utf-8') as f:
            reason = f.read().strip()
        print(f"🚫 Push blocked: {reason}")
        return

    # Check if any checklist is incomplete
    if checklist_incomplete():
        print("🚫 Push blocked: checklist incomplete.")
        create_lock_file("Checklist incomplete")
        return

    # Check for pending questions in scratchpad
    thoughts_file = SCRATCHPAD_DIR / "model_thoughts_todo.md"
    with open(thoughts_file, 'r', encoding='utf-8') as f:
        thoughts_content = f.read()

    pending_questions = re.findall(r'- ❓ \[\d{4}-\d{2}-\d{2}\] (.*)', thoughts_content)
    if pending_questions:
        print("🚫 Push blocked: pending questions in scratchpad.")
        for question in pending_questions:
            print(f"  - {question}")
        create_lock_file("Pending questions in scratchpad")
        return

    # Check for unresolved inconsistencies
    inconsistencies_file = SCRATCHPAD_DIR / "inconsistencies_pending.md"
    with open(inconsistencies_file, 'r', encoding='utf-8') as f:
        inconsistencies_content = f.read()

    unresolved_inconsistencies = re.findall(r'- ⚠️ \[\d{4}-\d{2}-\d{2}\] (.*)', inconsistencies_content)
    if unresolved_inconsistencies:
        print("🚫 Push blocked: unresolved inconsistencies.")
        for inconsistency in unresolved_inconsistencies:
            print(f"  - {inconsistency}")
        create_lock_file("Unresolved inconsistencies")
        return

    # Run validation script if it exists
    validate_script = ROOT_DIR / "cli" / "validate_output.py"
    if validate_script.exists():
        result = subprocess.run([sys.executable, str(validate_script)], capture_output=True, text=True)
        if result.returncode != 0:
            print("🚫 Push blocked: output validation failed.")
            print(result.stdout)
            print(result.stderr)
            create_lock_file("Output validation failed")
            return

    # Execute git push
    try:
        # First commit any changes
        result = subprocess.run(["git", "status"], capture_output=True, text=True)
        if "Changes not staged for commit" in result.stdout or "Untracked files" in result.stdout:
            print("Committing changes...")
            subprocess.run(["git", "add", "."], capture_output=True)
            subprocess.run(["git", "commit", "-m", "Completed checklist steps"], capture_output=True)

        # Then push
        print("Pushing changes...")
        result = subprocess.run(["git", "push"], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        print("✅ Changes pushed successfully!")
    except Exception as e:
        print(f"Error pushing changes: {e}")
        create_lock_file(f"Error pushing changes: {e}")

def checklist_incomplete():
    """Check if any checklist is incomplete."""
    bootstrap_file = BOOTSTRAP_DIR / "000_BOOTSTRAP_FIX_INIT.md"
    if not bootstrap_file.exists():
        return True

    with open(bootstrap_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find unchecked items
    unchecked = re.findall(r'- \[ \]', content)
    return len(unchecked) > 0
