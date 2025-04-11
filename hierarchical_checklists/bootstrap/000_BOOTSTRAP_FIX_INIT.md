# 📍 FIX INITIATOR: [Issue Title]

## 🔧 Issue Summary
[Detailed description of the issue to be fixed]

## 🎯 Objective
Autonomously generate and execute a fail-safe fix pipeline for this issue, using hierarchical checklists. Ensure **no deviation**, **no hallucinated validation**, **no premature exit**.

## 🗂 Required Execution Tree
- [ ] STEP_01__DEFINE_FIX_STRATEGY.md
- [ ] STEP_02__TRACE_SIGNAL_PATH.md
- [ ] STEP_03__ISOLATE_ISSUE.md
- [ ] STEP_04__IMPLEMENT_FIX.md
- [ ] STEP_05__VALIDATE_FIX.md
- [ ] STEP_06__CLEANUP_AND_PUSH.md

## 🛑 Failsafe Constraints
- [ ] No file mutation unless parent checklist step is complete
- [ ] No push unless validation confirms fix
- [ ] No commit unless tests pass
- [ ] On uncertain logic: write pending question to `scratchpad/model_thoughts_todo.md` and halt

## 🧠 Internal Prompt: Checklist Writer
> "Write `STEP_01__DEFINE_FIX_STRATEGY.md` with all subgoals and verification paths. This file will link to the next file in hierarchy based on each checklist item. Each subgoal must recursively generate its own `.md` child if complex."
