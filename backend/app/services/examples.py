"""Built-in example errors for the UI's "Try Example" button.

These examples go through the *actual* RAG pipeline — nothing is hardcoded.
"""
from typing import Dict, List

EXAMPLES: List[Dict[str, str]] = [
    {
        "title": "Java — NullPointerException",
        "language": "java",
        "input": (
            'Exception in thread "main" java.lang.NullPointerException: '
            'Cannot invoke "User.getName()" because "user" is null\n'
            "\tat UserService.java:42\n"
            "\tat com.example.OrderService.getUser(OrderService.java:18)\n"
        ),
    },
    {
        "title": "Python — KeyError",
        "language": "python",
        "input": (
            "Traceback (most recent call last):\n"
            '  File "C:\\\\app\\\\users.py", line 12, in <module>\n'
            "    profile = user_profile['settings']['theme']\n"
            "             ~~~~~~~~~~~^^^^^^^^^^^^\n"
            "KeyError: 'settings'\n"
        ),
    },
    {
        "title": "JavaScript — TypeError",
        "language": "javascript",
        "input": (
            "TypeError: Cannot read properties of undefined (reading 'toUpperCase')\n"
            "    at normalizeName (utils.js:15)\n"
            "    at renderUsers (app.js:42)\n"
        ),
    },
    {
        "title": "SQL — syntax error",
        "language": "sql",
        "input": (
            'sqlite3.OperationalError: near "WHERE": syntax error\n'
            "SELECT * FROM users WHERE id = 1 AND;\n"
        ),
    },
    {
        "title": "React — Invalid Hook Call",
        "language": "react",
        "input": (
            "Error: Invalid hook call. Hooks can only be called inside of the body "
            "of a function component.\n"
            "\tuseState called from a regular function\n"
            "    at App (App.jsx:21)\n"
        ),
    },
]


def get_examples() -> List[Dict[str, str]]:
    """Return a shallow copy of the built-in examples."""
    return [dict(e) for e in EXAMPLES]