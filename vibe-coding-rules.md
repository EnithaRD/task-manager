## Git Delegation Rules

### Never delegate

#### git reset --hard
Worst case: uncommitted work can be permanently destroyed.
Recovery: potentially impossible if the work was never committed or backed up.

#### git push --force
Worst case: shared remote history can be overwritten.
Recovery: may require reflog/backups and coordination with collaborators.

#### Rebasing a branch others have pulled
Worst case: shared history becomes inconsistent for other developers.
Recovery: requires coordination and potentially resetting/reconciling branches.

#### .env, credentials or secrets
Worst case: credentials or secrets can be exposed or committed to the repository.
Recovery: immediately revoke/rotate the exposed secret and remove it from repository history.