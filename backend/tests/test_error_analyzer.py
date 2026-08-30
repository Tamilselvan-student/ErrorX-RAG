"""Tests for the error analyzer (language, error type, category, stack frames)."""
import pytest
from pydantic import ValidationError

from app.models import AnalyzeRequest
from app.services.error_analyzer import analyze


def test_detects_java_null_pointer_exception():
    text = (
        'Exception in thread "main" java.lang.NullPointerException: '
        'Cannot invoke "User.getName()" because "user" is null\n'
        "\tat UserService.java:42\n"
    )
    result = analyze(text)
    assert result.detected_error == "NullPointerException"
    assert result.language == "Java"
    assert result.category == "Runtime Error"
    assert result.language_confidence in ("High", "Medium")
    assert any("UserService.java:42" in f["location"] for f in result.stack_frames)


def test_detects_python_key_error():
    text = (
        "Traceback (most recent call last):\n"
        '  File "C:\\\\app\\\\users.py", line 12, in <module>\n'
        "    profile = user_profile['settings']\n"
        "KeyError: 'settings'\n"
    )
    result = analyze(text)
    assert result.detected_error == "KeyError"
    assert result.language == "Python"
    assert result.category == "Runtime Error"
    assert result.keywords


def test_detects_javascript_type_error():
    text = (
        "TypeError: Cannot read properties of undefined (reading 'toUpperCase')\n"
        "    at normalizeName (utils.js:15)\n"
    )
    result = analyze(text)
    assert result.detected_error == "TypeError"
    assert result.language == "JavaScript"


def test_detects_sql_null_comparison():
    text = "SELECT * FROM users WHERE id = NULL;"
    result = analyze(text, language_hint="sql")
    assert result.language == "SQL"
    assert "NULL" in result.detected_error.upper()


def test_language_hint_overrides_detection():
    result = analyze("generic runtime failure happened at line 12", language_hint="python")
    assert result.language == "Python"
    assert result.language_confidence == "High"


def test_unknown_language_is_not_invented():
    result = analyze("lorem ipsum dolor sit amet consectetur")
    assert result.language in ("", "Unknown")


def test_custom_java_exception_detected():
    text = "com.acme.MyCustomException: boom\n\tat App.java:9"
    result = analyze(text)
    assert result.detected_error == "MyCustomException"
    assert result.language == "Java"


def test_stack_frames_extracted():
    text = (
        "\tat com.example.OrderService.getUser(OrderService.java:18)\n"
        "\tat com.example.Main.main(Main.java:7)\n"
    )
    result = analyze(text)
    assert len(result.stack_frames) >= 2
    assert result.stack_frames[0]["line"] == "18"


def test_pydantic_rejects_unsupported_language():
    with pytest.raises(ValidationError):
        AnalyzeRequest(input="x", language="cobol")


def test_pydantic_rejects_empty_input():
    with pytest.raises(ValidationError):
        AnalyzeRequest(input="   ", language="auto")