# Hierarchical Checklist System - Usage Example

This document provides a step-by-step example of how to use the hierarchical checklist system for a typical development task.

## Example Scenario: Fixing a Rendering Bug

Let's say we have a bug where 3D voxels aren't rendering correctly in our application.

### Step 1: Initialize the Bootstrap File

Edit `bootstrap/000_BOOTSTRAP_FIX_INIT.md` to describe the issue:

```markdown
# 📍 FIX INITIATOR: Voxel Rendering Bug

## 🔧 Issue Summary
3D voxels are not displaying in the renderer panel. The panel shows up correctly, but no voxels are visible. Console logs show that data is being loaded, but nothing appears on screen.

## 🎯 Objective
Fix the voxel rendering issue by identifying and resolving the root cause. Ensure proper validation through visual confirmation and automated tests.

## 🗂 Required Execution Tree
- [ ] STEP_01__DEFINE_FIX_STRATEGY.md
- [ ] STEP_02__TRACE_SIGNAL_PATH.md
- [ ] STEP_03__ISOLATE_RENDER_CONTEXT.md
- [ ] STEP_04__INJECT_TEMP_LOGS.md
- [ ] STEP_05__CONFIRM_FIX_VIA_VISUAL_OUTPUT.md
- [ ] STEP_06__PRUNE_DEBUG_CODE_AND_PUSH.md

## 🛑 Failsafe Constraints
- [ ] No file mutation unless parent checklist step is complete
- [ ] No push unless `visual_output == expected_output`
- [ ] No commit unless `test_logs` match checklist description
- [ ] On uncertain logic: write pending question to `scratchpad/model_thoughts_todo.md` and halt
```

### Step 2: Run the CLI Tool

```bash
python hierarchical_checklists/cli/rag_runner.py
```

### Step 3: Follow the Steps

The CLI will guide you through each step. For example, when working on STEP_01:

1. Analyze the issue
2. Log thoughts using the `log` command
3. Execute commands using `exec`
4. Verify the step when complete using `verify`
5. Move to the next step using `next`

### Step 4: Example Terminal Session

```
🔄 RAG Task Checklist System
==================================================
📋 Current active step: STEP_01__DEFINE_FIX_STRATEGY.md

==================================================
# STEP 01: DEFINE FIX STRATEGY
**Parent:** `000_BOOTSTRAP_FIX_INIT.md`
**Status:** ☐ In Progress

## ⬇️ Substeps
- [ ] [STEP_01A__Analyze_Issue_Root_Cause.md](./STEP_01A__Analyze_Issue_Root_Cause.md)
- [ ] [STEP_01B__Identify_Potential_Solutions.md](./STEP_01B__Identify_Potential_Solutions.md)
- [ ] [STEP_01C__Select_Best_Approach.md](./STEP_01C__Select_Best_Approach.md)

## 📋 Step Verification Rules
- [ ] All child steps return ✅ before continuing
- [ ] If any child step logs a ❓ in `model_thoughts_todo.md`, halt and prompt user/model retry

## 📎 Notes
- 🧠 *Model Hypothesis:* The issue may be related to initialization sequence.
- 🧠 *Pending:* Need to verify if all dependencies are properly loaded.
==================================================

>> log
Enter thought: Need to check if OpenGL context is being created before voxel rendering
✅ Logged thought: Need to check if OpenGL context is being created before voxel rendering

>> exec python tests/test_renderer.py --verbose
Executing: python tests/test_renderer.py --verbose
STDOUT:
Initializing renderer...
Loading voxel data from file: test_data.vox
ERROR: No OpenGL context found when calling glViewport()

STDERR:

Return code: 1

>> verify
❌ Not all checkboxes are checked.
❌ Step verification failed.
```

### Step 5: Complete All Steps

Continue through all steps until the issue is fixed and all steps are verified. The system will prevent you from pushing incomplete work or skipping steps.

## Safety Features in Action

- If you try to push before completing all steps:
  ```
  >> push
  🚫 Push blocked: checklist incomplete.
  ```

- If you try to skip a step:
  ```
  >> next
  🚫 Cannot move to next step. Current step has unchecked items.
  ```

- If you have pending questions:
  ```
  >> verify
  ❌ There are pending questions in the step file.
  ❌ Step verification failed.
  ```
