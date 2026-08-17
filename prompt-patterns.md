# Prompt Patterns

## 1. Investigate Only

**Template**

```text
Inspect [FEATURE] and the existing implementation.
Show the relevant files, current behavior, affected functions, and proposed approach.
Do not make any changes yet.
```

**Example**

```text
Inspect the existing Task Manager before adding task priority.
Show the relevant files, affected models/endpoints, frontend files, and tests.
Show your proposed approach.
Do not make any changes yet.
```

## 2. Plan First

**Template**

```text
In plan mode, investigate [FEATURE].
Review the existing implementation and propose the files, approach, tests, and verification steps.
Do not make any changes yet.
```

**Example**

```text
In plan mode, investigate adding task search, filtering, and sorting.
Review the existing backend, frontend, and tests.
Propose the implementation plan and files to modify.
Do not make any changes yet.
```

## 3. Scoped Change

**Template**

```text
Add [FEATURE].
```

**Requirements**

- [REQUIREMENTS]

**Constraints**

- Reuse the existing structure.
- No new dependencies.
- No unrelated changes.
- Do not change existing functionality.

```text
Do not change anything else.
```

**Example**

```text
Add task priority.
```

**Requirements**

- Priority must be low, medium, or high, with medium as the default.
- Users should select priority when creating a task.

**Constraints**

- Reuse the existing structure.
- Do not add dependencies or unrelated features.

```text
Do not change anything else.
```

## 4. Follow This Pattern

**Template**

```text
Implement [FEATURE] using the existing pattern in [FILE].
Reuse the same structure and conventions.
Do not introduce a different pattern or refactor unrelated code.
```

**Example**

```text
Implement Task Notes using the existing Pydantic and test patterns in
backend/main.py and tests/test_main.py.
Reuse the existing in-memory storage and CRUD patterns.
Do not introduce a new database or repository layer.
```

## 5. Reproduce Then Fix

**Template**

```text
Reproduce [BUG] first.
Create or run a test that demonstrates the failure.
Do not fix it yet.
After confirming the failure, implement the smallest fix and run all tests.
```

**Example**

```text
Reproduce the reported task behavior with a failing test first.
Confirm the failure before making the fix.
Then implement the smallest fix and verify all tests pass.
```

## 6. Constrained Refactor

**Template**

```text
Refactor [FEATURE] without changing existing behavior.
Keep existing tests passing.
Do not add dependencies.
Do not modify unrelated files or functionality.
Show the diff and run the tests afterward.
```

**Example**

```text
Refactor the Task Manager while preserving existing behavior.
Modify only the specified files.
Do not add dependencies or change priority, notes, search, filtering, or sorting.
Run all existing tests afterward.
```

## 7. Explain This Diff

**Template**

```text
Explain this diff against the approved plan.
Identify what changed, why it changed, and anything outside the approved scope.
Do not make any changes.
```

**Example**

```text
Compare the completed Task Notes diff against the approved plan.
Identify any files or changes that were not planned.
Do not make any changes.
```


