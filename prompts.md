# Day 6 — Prompting Patterns & Plan Mode

## Exercise 6.1 — One Feature, Three Prompts

The biggest improvement came from adding clear context, requirements, constraints, and acceptance criteria in B. This helped Claude understand the existing code and avoid unnecessary changes. C became more precise by referencing existing files and adding explicit “must not” rules, but it was not significantly better than B. The examples added only a small improvement.

## Exercise 6.2 — Plan Mode

Feature: Task Search, Filtering & Sorting

Claude's plan was reviewed against all five questions. It solved the requested problem, fit the existing codebase, avoided unnecessary dependencies and refactoring, included testing and verification, and was small enough to review in one sitting.

One issue was identified: creation-order sorting should not introduce a `created_at` field or a new storage mechanism. Claude was asked to preserve the existing insertion order instead.

The revised plan was approved and implemented. The finished diff was then compared against the approved plan to check for unplanned changes.

## Exercise 6.3 — Reject a Plan Properly

Feature: Task Notes

Plan rounds: 2

The first plan used a more complicated expand/collapse UI with several helper functions. I rejected it because it was more UI structure than necessary. I asked Claude to use the simplest existing frontend pattern instead.

The second plan used a simple always-visible textarea and Save Notes button, while reusing the existing backend and storage patterns. I approved it.

The implementation stayed within the planned application files:
`backend/main.py`, `frontend/app.js`, `frontend/style.css`, and `tests/test_main.py`.

29 tests passed. Two `__pycache__` files appeared during execution; these were generated test artifacts and were not part of the approved plan.


## Exercise 6.4 — Constraints That Bind

Feature: Add due date support to tasks.

I first used decorative constraints such as “write clean code,” “follow best practices,” and “keep it simple.” These were difficult to verify objectively from the diff.

I then used binding constraints that specified exactly which files could be changed, prohibited new dependencies and files, required existing patterns to be followed, and prevented unrelated changes.

The binding constraints were respected. `frontend/style.css` was not modified, and all 34 tests passed with 1 warning.

The main learning was that constraints should be specific and verifiable against the diff. A strong constraint creates a clear boundary, such as “modify only these files” or “do not change anything else.”



## Exercise 6.5 — Know When to Split

Oversized request: Turn the Task Manager into a complete team task-management application.

I split the request into four independently reviewable and mergeable steps:

1. User authentication
   Commit: `Add user authentication`

2. Task assignment
   Commit: `Add task assignment`

3. Team task dashboard
   Commit: `Add team task dashboard`

4. Task notifications
   Commit: `Add task notifications`

Each step has a clear scope and can be reviewed and merged independently. The "AND" test was used to avoid combining multiple responsibilities into one step.

I did not implement the full oversized request because the purpose of this exercise was to practice recognizing when a request should be split before implementation.