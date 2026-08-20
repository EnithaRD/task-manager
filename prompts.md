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


## Exercise 7.4 — Reflection

### What was missing from my original Slice 2 prompt?

My original prompt did not include an explicit binding constraint specifying which files Claude was allowed to modify.

I only asked Claude to keep the implementation consistent with the existing codebase. Although Claude modified only `backend/main.py` and `tests/test_main.py` in this case, the prompt did not explicitly prevent changes to other files.

In Slice 1, I had explicitly stated the allowed files. I should have carried that constraint into Slice 2 as well.

### Lesson

When scope matters, do not rely on the agent to infer it. Explicitly name the files that may be changed and state that files outside that list must not be modified.


## Project 2 — Task Manager REST API

### Important prompts used

1. "Start Project 2: Task Manager REST API. First inspect the existing repository. Do not code yet. Create a PROJECT_SPEC.md defining [endpoints, data model, validation, status codes, storage, tests, out-of-scope]. Recommend an appropriate technology stack and explain why. Do not create implementation files yet. Show me the proposed specification first."
2. "Create PROJECT_SPEC.md from the approved specification. Do not implement the API yet."
3. "Create a feature branch for Project 2 from the current main branch. Do not implement or commit anything yet."
4. "Read PROJECT_SPEC.md and implement the approved Task Manager REST API. [requirements list]. Implement the minimum clean solution. Do not add unrelated features. Run the complete test suite after implementation. Do not commit yet."
5. "Review the implementation against every requirement in PROJECT_SPEC.md. Do not modify anything. Identify missing requirements, unnecessary changes, validation problems, test gaps, and API issues."
6. "Read PROJECT_SPEC.md and finish the Task Manager REST API implementation. [...] Run the complete test suite. Do not commit yet. Then review the implementation against PROJECT_SPEC.md and report any missing requirements or issues. If tests pass, continue with [README.md and prompts.md updates]. Do not commit yet. Show me the diff summary."

### What was asked for

A spec-first workflow: inspect the repo before writing anything, get the spec approved before touching code, branch before implementing, implement the minimum needed to satisfy the spec, self-review against the spec with no code changes allowed during review, then fix only what the review found, re-verify with the full test suite, and only then touch documentation — with an explicit no-commit boundary held throughout.

### What was generated

- `PROJECT_SPEC.md` — endpoints, data model, validation rules, status codes, persistence choice, minimum test list, out-of-scope items, and a justified tech stack recommendation (reusing FastAPI/Pydantic/pytest already in the repo, adding SQLite + SQLAlchemy for persistence).
- Branch `task-manager-rest-api` off `main`.
- `backend/database.py`, `backend/models.py` (new), and a rewritten `backend/main.py`: in-memory `dict` replaced with SQLite-backed persistence, routes moved from `/api/tasks` to `/tasks`, added `title`/`due_date` validation.
- Updated `frontend/app.js` and `tests/test_main.py` to match the new `/tasks` paths and DB-backed fixture.
- A structured self-review (no file changes) that caught real gaps: `created_at` was stored but never returned by the API; no max-length validation on `title`/`description`/`notes`; a genuine bug where `PUT` with `"title": null` crashed with a 500 instead of returning 422; non-positive task IDs weren't rejected.
- A second implementation pass that fixed exactly those findings (added `created_at` to the response model and wired it into `sort_by=created`; added `Field(max_length=...)`; fixed the `title` validator to reject `None` cleanly; added `Path(gt=0)` on ID path params) plus 7 new tests targeting those specific fixes — 57 tests passing.

### Important decisions

- **Reuse over rewrite**: the existing in-memory API's shape (fields, filters, sort, status codes) was kept as-is and only the storage layer was swapped, rather than redesigning the API for Project 2.
- **Route prefix change was flagged, not silently assumed**: `PROJECT_SPEC.md` explicitly called out the `/api/tasks` → `/tasks` change as something needing reconciliation; the implementation made a reasonable choice (full replace, update frontend + tests to match) but this was surfaced in the review rather than buried.
- **Review before fixing, fixing only what the review found**: the review pass was run with modifications explicitly disallowed, so it produced an honest list of gaps instead of a review that quietly fixed things along the way. The fix pass then targeted only those findings — no scope creep.
- **Tests as the acceptance gate**: "if tests pass, continue" was used as a hard checkpoint before moving on to documentation, not just as an FYI step.

### What I would improve in future prompts

- The spec review step ("review against every requirement") should have explicitly asked for a **severity ranking** (blocking vs. cosmetic) up front — the review returned a flat list, and separating "must fix before this counts as done" from "nice to have" would have made the next prompt's scope even tighter.
- I should specify **whether new fields introduced for the review's sake (like `created_at`) need their own dedicated test**, rather than relying on the model to infer that gap — it was inferred correctly here, but that's not guaranteed for less obvious fields.
- For the `/api/tasks` → `/tasks` ambiguity that the spec itself flagged, I should have resolved it explicitly in the prompt (e.g., "keep both paths" or "fully replace") instead of leaving it as an open decision for the implementation step to make on its own.