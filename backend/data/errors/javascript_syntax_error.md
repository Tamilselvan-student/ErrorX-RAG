---
error_name: SyntaxError
language: JavaScript
category: Syntax Error
---

# SyntaxError

## Description

`SyntaxError` is raised when the JavaScript parser cannot make sense of the source
code, so the script fails to *load/compile* before any line runs. Common renderings
in the browser: `Unexpected token '}'`, `Invalid or unexpected token`,
`Unexpected end of input`. It usually surfaces as a blank page with the error in
DevTools, because the whole bundle/script is rejected.

## Common Causes

- Missing or extra braces/parentheses/brackets — the parser loses its balance.
- Strings broken across lines without a valid continuation, or concatenation forgotten: a stray `'` swallows subsequent code as one string.
- Using the wrong quote type for the content, or smart quotes from a word processor.
- A stray comma, trailing `,` in a place the grammar disallows (e.g. an arrow parameter list).
- Newer syntax (optional chaining `?.`, class fields, `import`) used in an environment/bundler that does not transpile it.
- `return` with a newline before the expression (`return \n value`).

## Example

```js
// BAD
if (isValid {
  showMessage("ok");
}
// Unexpected token '{' — the ')' is missing
```

Fixed version:

```js
if (isValid) {
  showMessage("ok");
}
```

Another classic — broken string:

```js
// BAD
const msg = 'It's starting';    // the apostrophe closes the string early
```

```js
// GOOD
const msg = "It's starting";
```

## Why It Happens

The JS engine tokenizes then parses the file into an AST before executing. When a
token is illegal in the current grammar state (an unbalanced `{`, an unclosed
string running to the end of the file), the parser cannot build a valid program, so
nothing runs — not even the parts that look fine on their own.

## Solutions

1. Open DevTools and read the reported line/column; the `^`/position points at the token where parsing got stuck.
2. Check for unbalanced brackets and mismatched quotes nearest to that position — count them backward.
3. Use your IDE's bracket-matching / language server to visually spot imbalance.
4. If "unexpected end of input" appears, you are missing a closing `}`, `)`, `]`, or `"` above.
5. For newer syntax, confirm the transpilation target in your bundler config covers the syntax.
6. Run the file through a linter/prettier, which reformats and highlights the malformed spot.

## Prevention

- Format on save with Prettier; it makes imbalance obvious instantly.
- Let ESLint run in CI — parsing errors fail linting immediately.
- Keep braces on the same line as the block opener (the dominant convention).
- Commit small syntactic changes frequently so the breaking change is easy to isolate.

## Related Errors

- `ReferenceError`
- `TypeError`
- `Babel parser` errors (toolchain flavour of the same problem)
- `SyntaxError` (Python)