---
description: Stage (if needed) and commit locally with a Conventional Commit message. Never pushes.
argument-hint: "[skip <file> [<file>...]]"
---

Create a local git commit. Do **not** push.

Invoking this command is itself the authorization to commit — proceed through the procedure below without pausing to confirm the message, the staged set, or the commit itself. Only stop to ask if you hit a genuine blocker (e.g. a potential secret in the diff, or an ambiguous `skip` argument).

## Arguments

`$ARGUMENTS` may be:
- empty — default behavior
- `skip <path> [<path>...]` — stage everything except the listed paths, then commit

## Procedure

1. Run `git status --porcelain` and `git diff --cached --stat` in parallel to see what's staged vs. unstaged.

2. Decide what to commit:
   - **If `$ARGUMENTS` starts with `skip`:** ignore current staging state. Run `git add -A`, then `git reset HEAD -- <each skipped path>` to unstage the excluded files. Commit the result.
   - **Else if anything is already staged:** commit only the staged changes. Do not touch unstaged or untracked files.
   - **Else (nothing staged):** run `git add -A` to stage everything (tracked modifications + untracked files + deletions), then commit.

3. Inspect the staged diff with `git diff --cached` and recent commits with `git log --oneline -10` to match the repo's tone.

4. Draft the commit message in this shape:

   ```
   <type>(<scope>): <what changed>
   ```

   - `<type>`: Conventional Commits — `feat`, `fix`, `chore`, `refactor`, `docs`, `test`, `style`, `perf`, `build`, `ci`.
   - `<scope>`: the area touched — typically `web`, `api`, `db`, `infra`, `openspec`, or a more specific module name inferred from the paths. Omit the parens entirely if the change is truly repo-wide.
   - `<what changed>`: imperative, lowercase, no trailing period. Keep the subject line under ~72 chars.

   If the diff covers several distinct changes or non-obvious logic, add a blank line and a short bullet list below the subject:

   ```
   feat(web): add edit modal

   - wire modal open/close state into the recipe detail store
   - prefill form from the existing recipe payload
   - close modal and refetch on successful save
   ```

   Keep bullets to the *why* or the *non-obvious what*; skip bullets that just restate the subject.

5. Commit with a HEREDOC so multi-line messages format correctly:

   ```bash
   git commit -m "$(cat <<'EOF'
   <message here>
   EOF
   )"
   ```

   **Do not** add a `Co-Authored-By` trailer — this is the user's personal project.

6. If a pre-commit hook (Husky/lint-staged) fails, fix the underlying issue, re-stage the fixes, and create a **new** commit. Never use `--no-verify` and never `--amend` after a hook failure.

7. Run `git status` after the commit and report the new commit's subject line back to the user.

## Must not

- Push to any remote (no `git push`, no `--set-upstream`, nothing).
- Amend existing commits unless the user explicitly asks.
- Stage files that were explicitly skipped via `skip <path>`.
- Add `Co-Authored-By` or other trailers unless requested.
- Commit obvious secret files (`.env`, credentials, keys) even if they appear in the working tree — stop and warn the user instead.
