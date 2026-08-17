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