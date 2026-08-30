---
error_name: SQL Constraint Error
language: SQL
category: Constraint Error
---

# SQL Constraint Error

## Description

A constraint violation means a `INSERT`/`UPDATE` (or `DELETE` that breaks a
reference) would leave the database in a state its schema forbids. Common forms:

- `FOREIGN KEY constraint failed` (SQLite) / `violates foreign key constraint`.
- `NOT NULL constraint failed: users.email` — a required column got `NULL`.
- `CHECK constraint failed` / `violates check constraint`.
- Unique violations are a sibling (see *Duplicate Error* document).

## Common Causes

- Inserting a row referencing a parent row that does not exist (wrong id, deleted parent).
- Not providing a value for a `NOT NULL` column (the column is absent from the `INSERT` column list, or the code passes `None`).
- Inserting/reading data across tables whose ids are not synchronized (FK mismatch after a data migration).
- A `CHECK` constraint's condition failing for the exact value set being written.
- Deleting a parent row that is still referenced by children (`RESTRICT`/`NO ACTION`).
- Bulk imports with rows out of order (children before parents) and deferred constraints disabled.

## Example

```sql
-- authors must exist before their books:
INSERT INTO books (title, author_id) VALUES ('Fun with SQL', 999);
-- ERROR: FOREIGN KEY constraint failed (no author with id 999)
```

Fixed version — create the parent first:

```sql
INSERT INTO authors (id, name) VALUES (999, 'Ada');
INSERT INTO books (title, author_id) VALUES ('Fun with SQL', 999);
```

`NOT NULL` failure:

```sql
INSERT INTO users (name) VALUES ('Ada');     -- email column is NOT NULL, value missing
-- ERROR: NOT NULL constraint failed: users.email
```

## Why It Happens

Constraints are the database's contract: they guarantee referential integrity and
required data. When a statement violates one, the database *must* abort the whole
statement (and often the transaction) to keep the invariant true — partial writes
would silently corrupt the model. The error message includes the constraint and
usually the column/table involved, which points straight at the bad value.

## Solutions

1. Read which constraint failed — `FOREIGN KEY`, `NOT NULL`, `CHECK` — and the referenced column.
2. For FK failures, verify the parent exists: `SELECT id FROM parents WHERE id = ...` before inserting, or insert parents first in the import order.
3. For `NOT NULL`, check your insert column list and the ORM mapping — the missing column is usually a code bug, not data.
4. For `CHECK`, print the value being written and compare it to the constraint expression.
5. Wrap batch imports in a transaction and enable deferred foreign keys (SQLite `PRAGMA defer_foreign_keys`) so ordering matters less.
6. When deleting parents, remove children first, or set the FK to `ON DELETE CASCADE` deliberately.

## Prevention

- Test migrations and seed data against the real schema in CI.
- Validate domain rules in the app, but rely on the DB constraints as the final guard.
- Use explicit `INSERT` column lists so NULLs are a conscious choice.
- Model parent/child creation in one transaction in the service layer.
- Enforce foreign keys (SQLite default is OFF until you `PRAGMA foreign_keys = ON`).

## Related Errors

- `Duplicate Error` (unique constraint)
- `SQL NO NULL comparison issues`
- `Missing Column Error`
- ORM `IntegrityError` / `DataError` (same family)