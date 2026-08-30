---
error_name: SQL Type Mismatch Error
language: SQL
category: Logic Error
---

# SQL Type Mismatch Error

## Description

A SQL type mismatch happens when a value does not fit the column or operator type:
`invalid input syntax for type integer: "abc"` (PostgreSQL),
`DATA_TYPE_MISMATCH` / `Incorrect integer value: 'abc' for column 'age'` (MySQL),
`datatype mismatch` (SQLite). It can also appear as an *implicit* mismatch —
comparing a string column with a number, or inserting a dictionary where a blob
was expected.

## Common Causes

- Passing a string where the column expects a number/date: `"2024"` into an `INTEGER` column, or `"2024-13-40"` into a `DATE` column.
- Application-side `None`/`null`/empty string being sent for a `NOT NULL` numeric column.
- Comparing typed values incorrectly, e.g. `WHERE price = 'free'` on a `DECIMAL` column.
- Locale-formatted numbers (`"1.234,56"`) inserted directly instead of converted.
- ORM mapping the wrong Python/JS type to the column (a `str` for an `int` field).
- Mixing `INTEGER`/`REAL` expectations in arithmetic or `BETWEEN` on a text column.

## Example

```python
# BAD: passing a string where the schema expects an integer
cursor.execute(
    "INSERT INTO users (name, age) VALUES (%s, %s)",
    ("Ada", "not-a-number"),          # ERROR: invalid input syntax for type integer
)
```

Fixed:

```python
age = int(parsed_age) if parsed_age.isdigit() else None
if age is not None:
    cursor.execute(
        "INSERT INTO users (name, age) VALUES (%s, %s)",
        ("Ada", age),
    )
```

```sql
-- BAD
SELECT * FROM orders WHERE total = 'one hundred';
```

```sql
-- GOOD
SELECT * FROM orders WHERE total = 100;
```

## Why It Happens

SQL columns are strongly typed: the storage engine interprets bytes according to
the declared type. When a driver sends a value the type system cannot parse (a
non-numeric string into a numeric column, an invalid calendar date), the database
cannot store or compare meaningfully and fails with a type mismatch. The message
includes the type it expected and the rejected text.

## Solutions

1. Read the message: it names the expected type and the offending literal (e.g. `invalid input syntax for type integer: "abc"`).
2. Find the code path that produced the bad value — usually a conversion happening too late or never (`int(x)`, `datetime.fromisoformat`).
3. Convert values at the API/ORM boundary where the type contract is well defined.
4. Send `NULL` values as `None`/`NULL`, not as `""`/`"0"` — empty strings are valid text but invalid numbers.
5. Avoid ORM auto-type guesses; declare explicit column types in the model.
6. Add validation tests that run each insert with its extreme and malformed variations.

## Prevention

- Define precise DDL types (`INTEGER`, `NUMERIC(10,2)`, `DATE`) matching each domain value.
- Validate and coerce input in the service layer before it reaches queries.
- Keep a small set of typed helper functions for persistence (insert_user, update_price) so type drift is centralized.
- Database tests with realistic (dirty) payloads catch conversions CI with synthetic data misses.

## Related Errors

- `SQL Missing Column Error`
- `SQL Constraint Error`
- `NumberFormatException` (Java)
- `ValueError` (Python)