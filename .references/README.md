# .references/

Cloned reference repos for study. The contents are gitignored; only this README is committed.

The canonical rehydration index is [`REFERENCES.md`](../REFERENCES.md) at the repo root:
`mise run rehydrate` (`tools/rehydrate.py`) clones every `git clone … .references/<dir>` line in it.
Add new public clones there, not here.

## Local clones not in REFERENCES.md

Some owner-local clones of non-public repos may sit here. They are not listed: this repo is
public, and they are not rehydratable from it.
