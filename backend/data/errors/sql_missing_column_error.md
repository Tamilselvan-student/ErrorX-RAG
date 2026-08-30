---
error_name: Missing Column Error
language: SQL
category: Logic Error
---

# Missing Column Error

## Description

This error means your SQL statement references a column that does not exist in the
table (or in your query's scope). Providers phrase it differently:
`column "foo" does not exist` (PostgreSQL), `Unknown column 'foo' in 'field list'`
(MySQL), `no such column: foo` (SQLite). Fixing is usually a one-word typo fix —
but the root cause is often a schema drift between code and the live database.

## Common Causes

- A typo in the column name (`user_name` vs `username`, `orderId` vs `order_id`).
- Writing a query against a table whose schema differs from what you think (the model was migrated/renamed since the code was written).
- Referring to a column that only exists in a `SELECT` alias inside a `WHERE`/`GROUP BY` (you cannot reuse aliases in the same level, except in `ORDER BY`).
- Referencing a column in `JOIN`-on without qualifying it when both tables have same-named columns.
- Copying a query between providers where column naming conventions differ (`created_at` vs `createdAt`, case sensitivity).

## Example

```sql
-- BAD
SELECT id, user_name, email FROM users;   -- column is actually 'username'
-- ERROR: column "user_name" does not exist
```

Fixed:

```sql
SELECT id, username, email FROM users;
```

Alias misuse:

```sql
-- BAD: 'name' alias cannot be used in WHERE at the same SELECT level
SELECT first_name || ' ' || last_name AS name
FROM users
WHERE name = 'Ada Lovelace';
```

```sql
-- GOOD: repeat the expression, or wrap in a subquery
SELECT * FROM (
    SELECT first_name || ' ' || last_name AS name
    FROM users
) t
WHERE t.name = 'Ada Lovelace';
```

## Why It Happens

The database planner resolves every column reference against the actual schema of
the tables in scope. If no table in the query (directly or via join) defines that
name, planning fails with a "does not exist" error — before a single row is read.
The mismatch between the SQL you wrote and the DDL that actually ran is the 
classic cause.

## Solutions

1. Print the failing column name from the message and `\d table` / `DESCRIBE table`/`PRAGMA table_info(table)` to list the real columns.
2. Fix typos; be mindful of snake_case vs camelCase and exact casing for quoted identifiers.
3. For alias reuse, wrap the query in a subquery or `WITH`, or repeat the expression in `WHERE`.
4. Qualify joined columns: `SELECT u.name FROM users u JOIN orders o ON o.user_id = u.id`.
5. When the column really should exist but does not — run the pending migration/deployment against the environment.
6. Add a schema snapshot test that compares the queries you ship against the production (or test) schema.

## Prevention

- Use a single naming convention (snake_case for all DB columns) and enforce it in the ORM.
- Generate queries from ORM mappings instead of handwriting SQL strings.
- Run migrations in a controlled order and verify them in CI against an ephemeral database.
- Review schema-vs-code drift in every deployment checklist.

## Related Errors

- `Missing Table Error` (same family, one level up)
- `SQL Syntax Error`
- `SQL Constraint Error`
- ORM `ProgrammingError` / `OperationalError` wrappers