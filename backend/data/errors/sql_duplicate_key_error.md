---
error_name: Duplicate Error
language: SQL
category: Constraint Error
---

# Duplicate Error

## Description

A duplicate error is thrown when an insert or update would create a row that
violates a **unique** constraint (a `UNIQUE` index, a `PRIMARY KEY`, or a partial
unique index). Real messages: `UNIQUE constraint failed: users.email` (SQLite),
`duplicate key value violates unique constraint "users_email_key"` (PostgreSQL),
`Duplicate entry 'ada@example.com' for key 'users.email'` (MySQL). The message
names the constraint and the offending value.

## Common Causes

- Retrying a request that already succeeded (double-click on "Submit", replay of a webhook) — the same unique key is inserted twice.
- Two rows in a bulk import/CSV share the same key (same email, same slug, same order number) while the table already has one.
- Case/whitespace differences that the column's collation treats as equal.
- A `UNIQUE` index on a column you assumed could repeat (e.g. naming a product slug unique when drafts collide).
- Concurrent flows both generating the same id because the id was guessed client-side.

## Example

```sql
-- users.email has a UNIQUE index
INSERT INTO users (email, name) VALUES ('ada@example.com', 'Ada');
INSERT INTO users (email, name) VALUES ('ada@example.com', 'Adal');   -- ERROR:
-- UNIQUE constraint failed: users.email
```

Idempotent fix — insert only if absent:

```sql
INSERT INTO users (email, name)
SELECT 'ada@example.com', 'Ada'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'ada@example.com');
```

Or upsert (provider-specific):

```sql
INSERT INTO users (email, name) VALUES ('ada@example.com', 'Ada')
ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name;   -- PostgreSQL
```

## Why It Happens

Unique constraints are backed by a unique index: before inserting a row, the
database probes the index for the key. Finding an existing entry means the
uniqueness invariant would be broken, so the statement aborts with an error naming
the constraint and value. The frequent real-world cause is *repeatability* — an
operation executed twice when it was only meant to run once.

## Solutions

1. Read the constraint name and value — it tells you the column and the duplicate key.
2. Decide the intended semantics: is the insert *idempotent* (safe to retry), *domain-unique* (must never collide), or *accidentally colliding* (a bug)?
3. For idempotent flows, use `ON CONFLICT`/`INSERT OR IGNORE`/`ON DUPLICATE KEY UPDATE`, or check-then-insert inside a transaction.
4. Clean bulk imports before loading: deduplicate rows in memory and identify pre-existing values.
5. Normalize the key (trim, lower the email, canonicalize the slug) at the write boundary.
6. Investigate *how* two values arrived when it should be impossible — a duplicate key is often a symptom of a retry or concurrency bug elsewhere.

## Prevention

- Design unique constraints to match reality (partial unique indexes for "soft-deleted" rows: `UNIQUE (email) WHERE deleted_at IS NULL`).
- Make request handlers idempotent (idempotency keys for payments/orders).
- Prevent double-submit in the UI and dedupe at the ingestion layer.
- Add tests that insert the same key twice and assert the chosen strategy behaves.

## Related Errors

- `SQL Constraint Error`
- `SQL NOT NULL` failures
- `Missing Column Error`
- ORM `IntegrityError`