---
error_name: SQL Syntax Error
language: SQL
category: Syntax Error
---

# SQL Syntax Error

## Description

A SQL syntax error means the database's parser rejected your statement because it
does not follow the grammar. Providers phrase it differently:
`ERROR: syntax error at or near "WHERE"` (PostgreSQL),
`You have an error in your SQL syntax near '...'` (MySQL),
`near "xxx": syntax error` (SQLite). The database points at the token where parsing
stopped — often a few tokens *after* the real mistake.

## Common Causes

- Keyword order mistakes: `SELECT ... FROM users WHERE id = 1 AND;` — a dangling `AND`/`OR` with no right operand.
- Missing/extra commas in the `SELECT` list or `VALUES` clause (`INSERT INTO t (a,b) VALUES (1 2)`).
- Unbalanced quotes or parentheses in the WHERE clause.
- Using quotes instead of backticks for identifiers (`"users"` vs `` `users` `` in MySQL) or vice versa in PostgreSQL.
- Reserved keywords used as identifiers without escaping (`table`, `order`, `group`, `user`).
- Missing semicolons breaking a multi-statement batch, or a stray trailing `;` in the middle of a statement built by concatenation.
- Concatenating a query with an unfiltered user string that injects a stray token.

## Example

```sql
-- BAD
SELECT * FROM users WHERE id = 1 AND;
```

What the parser sees after `AND` is the end — but `AND` needs a right-hand operand.

```sql
-- GOOD
SELECT * FROM users WHERE id = 1 AND active = 1;
```

Another common one:

```sql
-- BAD (missing comma)
INSERT INTO products (name, price) VALUES ('Laptop' 1200);
```

```sql
-- GOOD
INSERT INTO products (name, price) VALUES ('Laptop', 1200);
```

## Why It Happens

SQL is a context-free-ish grammar, and database parsers are strict: every
statement must reduce to a valid rule. The parser scans token by token; at the
first token that cannot fit the current rule it stops and reports near that token.
Because the actual error is usually one token earlier (the missing operand/comma),
the "near" location is a strong hint, not the exact spot.

## Solutions

1. Read the "near" token, then look **immediately before** it for a missing operand, comma, or parenthesis.
2. Reconstruct the statement with placeholders and check each clause's grammar (`SELECT` list → `FROM` → `WHERE` → `ORDER BY` ...).
3. If the query is built in code, log the *final* SQL string (the string you execute, not the template) — concatenation bugs live there.
4. Avoid string concatenation; use parameterized queries that keep the SQL text static.
5. Quote reserved words properly: `"table"` (Postgres) or `` `table` `` (MySQL), or rename the column.
6. Validate parenthesized expressions by counting open/close parens mentally or with an editor's highlighter.

## Prevention

- Never build SQL by string interpolation; use parameters (psycopg2 `%s`, `sqlite3.?`, ORM query builders).
- Keep queries readable and formatted; run the formatter/linter in CI.
- Add integration tests that execute each query against a real (test) DB.
- Use an ORM or query builder that validates at construction time.

## Related Errors

- `SQL Constraint Error`
- `Missing Column Error`
- `StringIndexOutOfBounds` analog: truncation of the SQL text
- `SyntaxError` (programming-language analogue)