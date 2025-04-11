# Hierarchical Checklist System

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A bulletproof, tamper-resistant, terminal-based system for managing development tasks, debugging, and feature implementation with strict validation and safety mechanisms. The system can automatically detect if it's being used with a new codebase and guide the model through setting up a proper Hybrid XaaS (Anything-as-a-Service) structure.

## 🌟 Features

- **Auto-Detection**: Automatically detects if it's being used with a new or existing codebase
- **Guided Setup**: Provides step-by-step guidance for setting up a proper Hybrid XaaS architecture
- **Tamper-Resistant**: Detects and prevents unauthorized modifications to checklist files
- **Strict Validation**: Enforces validation at each step to ensure quality and consistency
- **Hierarchical Structure**: Organizes tasks in a hierarchical structure for better management
- **Terminal-Based**: Runs entirely in the terminal for easy integration with development workflows
- **Safety Mechanisms**: Prevents pushing incomplete work or skipping steps

## 📋 Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Directory Structure](#directory-structure)
- [Security Features](#security-features)
- [Workflow Examples](#workflow-examples)
- [Commands](#commands)
- [Protection Against Common Risks](#protection-against-common-risks)
- [Contributing](#contributing)
- [License](#license)

## 🔧 Installation

1. Clone the repository:

```bash
git clone https://github.com/ricardoamartinez/hierarchical-checklist-system.git
cd hierarchical-checklist-system
```

2. Ensure you have Python 3.6+ installed:

```bash
python --version
```

3. No additional dependencies are required as the system uses only standard Python libraries.

## 🚀 Usage

1. Run the CLI tool and specify your codebase directory:

```bash
python hierarchical_checklists/cli/rag_runner.py
```

2. The system will detect if it's a new codebase or an existing one:
   - **New Codebase**: It will initialize a project structure checklist to guide you through setting up a Hybrid XaaS architecture
   - **Existing Codebase**: It will initialize a fix/feature checklist to guide you through implementing changes

3. Follow the steps provided by the system, using the available commands to navigate, log thoughts, verify steps, and execute commands.

## 📁 Directory Structure

```
hierarchical_checklists/
│
├── bootstrap/
│   ├── 000_BOOTSTRAP_FIX_INIT.md     # Template for existing codebases
│   └── NEW_PROJECT_INIT.md           # Template for new codebases
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
    ├── validate_structure.py         # Directory structure validation
    └── command_log.txt               # Log of executed commands
```

## 🔒 Security Features

### Lock Architecture (Filesystem-Enforced)

- **`.model_push_lock`**: Exists = model is **not** allowed to `git commit`, `git push`, or mutate higher-level checklists.
  - Auto-generated if:
    - Any `*.md` has `[ ]` unchecked items.
    - Any file contains `❓` or `PENDING:` lines.
    - Any `EXPECTED_OUTPUT_<ID>.json` has not been verified.

- **`.current_step.lock`**: Contains absolute path to the current `.md` checklist file being worked on.
  - Model can only write to this file, not others.
  - Any attempt to `exec` or `verify` steps outside this path will be blocked.

### Terminal Guard Rails (Execution Filter)

- All allowed actions must pass through `rag_runner.py` and enforce strict validation.
- Commands are logged to `command_log.txt` for auditing.
- Failed commands automatically create lock files.

### Blinded Validation Strategy

- **`EXPECTED_OUTPUT_<ID>.json`**: Contains expected outputs, logs, and validation commands.
- **`validate_output.py`**: Validates outputs against expected values.
- If validation fails → writes to `scratchpad/inconsistencies_pending.md` → locks the process.

### Tamper-Evident File Hashing

- SHA256 hash of each checklist file is stored in `.checklist_hash_log`.
- Before running any command, all previous hashes are verified to detect tampering.

## 🔄 Workflow Examples

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

## 💻 Commands

The system provides the following commands:

- `next` - Move to the next step (only if current step is complete)
- `log` - Add model thoughts to model_thoughts_todo.md
- `verify` - Confirm and mark step as done (only if all checks pass)
- `status` - Print progress tree
- `halt` - Abort and record reasoning
- `exec <cmd>` - Run shell command (e.g., test runner)
- `push` - Push changes if all conditions met
- `help` - Show available commands
- `exit` - Exit the program

## 🛡️ Protection Against Common Risks

| Risk | Defense |
|------|---------|
| Fake fix | Output validation via blinded expected JSON |
| Writing outside current file | `.current_step.lock` scope enforcement |
| Premature commit/push | `.model_push_lock` + git hooks |
| Skipping steps | Step parser must verify all children ✅ |
| Tampering with checklists | SHA256 logging and verification |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- Inspired by best practices in software development
- Designed to enforce rigorous validation and safety mechanisms
- Created to guide models through complex development tasks

---

Made with ❤️ by [Ricardo A. Martinez](https://github.com/ricardoamartinez)
