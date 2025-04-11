# Hierarchical Checklist System

A bulletproof, tamper-resistant, terminal-based system for managing development tasks, debugging, and feature implementation with strict validation and safety mechanisms. The system can automatically detect if it's being used with a new codebase and guide the model through setting up a proper Hybrid XaaS structure.

## Directory Structure

```
hierarchical_checklists/
│
├── bootstrap/
│   └── 000_BOOTSTRAP_FIX_INIT.md     # Starts every process
│
├── steps/
│   └── STEP_<ID>__*.md               # All recursive task steps
│
├── scratchpad/
│   ├── model_thoughts_todo.md        # Model's thoughts and questions
│   └── inconsistencies_pending.md    # Tracking inconsistencies
│
├── expected/
│   └── EXPECTED_OUTPUT_<ID>.json     # Expected outputs for validation
│
├── lock/
│   ├── .model_push_lock              # Exists = commit/push blocked
│   └── .current_step.lock            # Contains path to current step
│
└── cli/
    ├── rag_runner.py                 # Main CLI script
    ├── checklist_utils.py            # Checklist parsing/validation
    ├── validate_output.py            # Output validation script
    └── command_log.txt               # Log of executed commands
```

## Security Features

### 🔐 Lock Architecture (Filesystem-Enforced)

- **`.model_push_lock`**: Exists = model is **not** allowed to `git commit`, `git push`, or mutate higher-level checklists.
  - Auto-generated if:
    - Any `*.md` has `[ ]` unchecked items.
    - Any file contains `❓` or `PENDING:` lines.
    - Any `EXPECTED_OUTPUT_<ID>.json` has not been verified.

- **`.current_step.lock`**: Contains absolute path to the current `.md` checklist file being worked on.
  - Model can only write to this file, not others.
  - Any attempt to `exec` or `verify` steps outside this path will be blocked.

### 🧱 Terminal Guard Rails (Execution Filter)

- All allowed actions must pass through `rag_runner.py` and enforce strict validation.
- Commands are logged to `command_log.txt` for auditing.
- Failed commands automatically create lock files.

### 🧪 Blinded Validation Strategy

- **`EXPECTED_OUTPUT_<ID>.json`**: Contains expected outputs, logs, and validation commands.
- **`validate_output.py`**: Validates outputs against expected values.
- If validation fails → writes to `scratchpad/inconsistencies_pending.md` → locks the process.

### ⛓️ Tamper-Evident File Hashing

- SHA256 hash of each checklist file is stored in `.checklist_hash_log`.
- Before running any command, all previous hashes are verified to detect tampering.

## How to Use

1. Run the CLI tool and specify your codebase directory:

```bash
python hierarchical_checklists/cli/rag_runner.py
```

2. The system will detect if it's a new codebase or an existing one:
   - **New Codebase**: It will initialize a project structure checklist to guide you through setting up a Hybrid XaaS architecture
   - **Existing Codebase**: It will initialize a fix/feature checklist to guide you through implementing changes

3. Use the following commands:

- `next` - Move to the next step (only if current step is complete)
- `log` - Add model thoughts to model_thoughts_todo.md
- `verify` - Confirm and mark step as done (only if all checks pass)
- `status` - Print progress tree
- `halt` - Abort and record reasoning
- `exec <cmd>` - Run shell command (e.g., test runner)
- `push` - Push changes if all conditions met
- `help` - Show available commands
- `exit` - Exit the program

## Workflow Examples

### New Project Workflow

1. The system detects a new codebase and initializes the NEW_PROJECT_INIT.md checklist
2. Follow the steps to choose a stack and create the directory structure
3. The system will guide you through setting up a proper Hybrid XaaS architecture
4. Verify each step when complete (system will enforce all checks)
5. Push changes only when the structure is validated

### Existing Project Workflow

1. The system detects an existing codebase and initializes the 000_BOOTSTRAP_FIX_INIT.md checklist
2. Edit the bootstrap file to define your task
3. Follow the steps in order, with each step enforcing its own validation
4. Log thoughts and questions as they arise
5. Verify each step when complete (system will enforce all checks)
6. Push changes only when all steps are verified and all validations pass

## Protection Against Common Risks

| Risk | Defense |
|------|---------|
| Fake fix | Output validation via blinded expected JSON |
| Writing outside current file | `.current_step.lock` scope enforcement |
| Premature commit/push | `.model_push_lock` + git hooks |
| Skipping steps | Step parser must verify all children ✅ |
| Tampering with checklists | SHA256 logging and verification |
