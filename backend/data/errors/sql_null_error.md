---
error_name: SQL NULL Comparison Error
language: SQL
category: Logic Error
---

# SQL NULL Comparison Error

## Description

This is not so much an exception as a *silent logic bug*: comparisons with `NULL`
never match. `NULL = NULL` is not true, `NULL = 1` is not false — both are
`UNKNOWN`, which behaves like false in `WHERE` clauses. The classic symptom:
`SELECT * FROM users WHERE deleted_at = NULL;` returns **zero rows** even when many
users have `deleted_at` set. The user sees the "error" as missing rows.

## Common Causes

- Writing `= NULL`, `<> NULL`, or `!= NULL` instead of `IS NULL` / `IS NOT NULL`.
- Treating a nullable column as a normal value in comparisons, `BETWEEN`, or joins.
- Using a nullable column in `WHERE ... = 'value'` and forgetting it can also be `NULL`.
- Aggregating with `COUNT(col)` expecting it to count NULLs (it does not).
- ORM/framework code that translates "NULL input" into `= NULL` because of a naive mapper.

## Example

```sql
-- BAD: never matches
SELECT * FROM users WHERE deleted_at = NULL;
```

Does the opposite of what the writer expects — it returns rows where
`deleted_at` is *not* null in some engines by accident, or none at all.

```sql
-- GOOD
SELECT * FROM users WHERE deleted_at IS NULL;
SELECT * FROM users WHERE deleted_at IS NOT NULL;
```

`BETWEEN` and NULL:

```sql
SELECT * FROM orders WHERE discount BETWEEN 0 AND 10;
-- a NULL discount is excluded, though the business rule may or may not want that
```

## Why It Happens

SQL implements three-valued logic (`TRUE`, `FALSE`, `UNKNOWN`) because a `NULL`
means "unknown / missing", not a concrete value. Comparing two unknowns cannot
produce a definite answer, so every NULL comparison evaluates to `UNKNOWN`.
`WHERE` keeps rows only where the predicate is `TRUE`, so UNKNOWN rows vanish.
`IS NULL`/`IS NOT NULL` are the dedicated predicates that test *for* nullness.

## Solutions

1. Replace `= NULL`, `<> NULL`, `= 'NULL'` with `IS NULL` / `IS NOT NULL` everywhere.
2. Audit joins and `BETWEEN` for NULL-introducing columns: decide *intent* (is NULL "not applicable"?) and express it (`col IS NOT NULL AND col BETWEEN ...`).
3. In application code, search for `= null`/`= None` patterns translated by your ORM into `= NULL`.
4. If a column may be NULL and you need `NOT IN`, remember NULL semantics break `NOT IN` — use `NOT EXISTS` instead.
5. Add tests that include NULL rows and assert exactly which set is returned.
6. Define column nullability in the schema to make intent explicit (`NOT NULL` where the app always requires a value).

## Prevention

- Make nullable columns rare and deliberate; use `NOT NULL DEFAULT ...` for columns that always have a value.
- Always write filter intent as `IS NULL`/`IS NOT NULL` — never equality.
- Namespaced query reviewers: grep for `= NULL` before merging.
- Prefer ORM constructs (`isnull=False`) that generate `IS NULL`.

## Related Errors

- `SQL Syntax Error`
- ORM query results being unexpectedly empty (the symptom)
- `Duplicate Error` when NULL keys collide in unique constraints
- Counting bugs (`COUNT(col)` with NULLs)