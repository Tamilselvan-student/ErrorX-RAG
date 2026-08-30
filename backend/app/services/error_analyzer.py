"""Lightweight, deterministic error & language analyzer.

Uses simple, reliable pattern matching (regex + keyword tables). It is
intentionally NOT an AST parser or ML classifier — just enough signal to build
a good RAG query and a confidence score.
"""
import re
from dataclasses import dataclass, field
from typing import Dict, List

# --------------------------------------------------------------------------- #
# Pattern tables: language -> [(weight, regex)]
# --------------------------------------------------------------------------- #

LANGUAGE_PATTERNS: Dict[str, List[tuple]] = {
    "java": [
        (1.0, re.compile(r"Exception in thread")),
        (1.0, re.compile(r"java\.lang\.[A-Za-z]+Exception")),
        (1.0, re.compile(r"\.java:\d+")),
        (0.9, re.compile(r"\bat\s+\S+\(.*\.java:\d+\)")),
        (0.8, re.compile(r"\b(public\s+)?(class|interface)\s+\w+")),
        (0.7, re.compile(r"\bimport\s+java\.")),
        (0.7, re.compile(r"\bSystem\.out\b")),
        (0.6, re.compile(r"\bString\[\]\s+args")),
        (0.5, re.compile(r"\bnew\s+(ArrayList|HashMap|LinkedList|StringBuilder)\b")),
    ],
    "python": [
        (1.0, re.compile(r"Traceback \(most recent call last\)")),
        (1.0, re.compile(r'File "[^"]*\.py", line \d+')),
        (1.0, re.compile(r"SyntaxError|IndentationError")),
        (0.9, re.compile(r"\b\.py:\d+")),
        (0.8, re.compile(r"\bdef\s+\w+\(|class\s+\w+:|if __name__")),
        (0.6, re.compile(r"\b(import|from)\s+\w+")),
        (0.5, re.compile(r"\bprint\(\s*|\bself\.")),
    ],
    "javascript": [
        (1.0, re.compile(r"Cannot read propert\w+ of undefined")),
        (1.0, re.compile(r"is not (a function|defined)")),
        (1.0, re.compile(r"\.js:\d+")),
        (0.9, re.compile(r"\b(ReferenceError|TypeError|RangeError|SyntaxError|URIError)\b")),
        (0.7, re.compile(r"\bconst\s+|let\s+|=>|\bconsole\.")),
        (0.6, re.compile(r"\brequire\(|\bimport\s+.*\bfrom\b")),
    ],
    "sql": [
        (1.0, re.compile(r"\bSQLSTATE\b|\bsqlite3\.\w+Error\b|\bpsycopg2\.\w+Error\b")),
        (1.0, re.compile(r"syntax error at or near|You have an error in your SQL syntax")),
        (1.0, re.compile(r"\b(?:FOREIGN KEY|PRIMARY KEY|UNIQUE|NOT NULL|CHECK)\s+constraint")),
        (0.9, re.compile(r"constraint\s+failed|duplicate key|duplicate entry|violates \w+ constraint")),
        (0.9, re.compile(r"\b(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE|JOIN|CREATE TABLE)\b", re.IGNORECASE)),
        (0.8, re.compile(r"\bNULL\b\s*(=|<>)")),
        (0.7, re.compile(r"column .* does not exist|table .* does not exist")),
    ],
    "react": [
        (1.0, re.compile(r"Invalid hook call|Rules of Hooks|hook order")),
        (1.0, re.compile(r"Element type is invalid")),
        (0.9, re.compile(r"\buseState\b|\buseEffect\b|\buseRef\b|\buseMemo\b")),
        (0.8, re.compile(r"\bfrom ['\"]react['\"]|import React")),
        (0.8, re.compile(r"\bclassName\b|\bexport default\b")),
        (0.6, re.compile(r"render\(\)|setState\(")),
    ],
}

# --------------------------------------------------------------------------- #
# Signature table: canonical error-name -> (category, language)
# --------------------------------------------------------------------------- #

ERROR_SIGNATURES: Dict[str, tuple] = {
    # Java
    "NullPointerException": ("Runtime Error", "Java"),
    "ArrayIndexOutOfBoundsException": ("Runtime Error", "Java"),
    "IndexOutOfBoundsException": ("Runtime Error", "Java"),
    "StringIndexOutOfBoundsException": ("Runtime Error", "Java"),
    "ClassCastException": ("Runtime Error", "Java"),
    "NumberFormatException": ("Runtime Error", "Java"),
    "ArithmeticException": ("Runtime Error", "Java"),
    "IllegalArgumentException": ("Runtime Error", "Java"),
    "IllegalStateException": ("Runtime Error", "Java"),
    "ConcurrentModificationException": ("Runtime Error", "Java"),
    "NegativeArraySizeException": ("Runtime Error", "Java"),
    "StackOverflowError": ("JVM Error", "Java"),
    "OutOfMemoryError": ("JVM Error", "Java"),
    "NoClassDefFoundError": ("Class Loading Error", "Java"),
    "ClassNotFoundException": ("Class Loading Error", "Java"),
    "FileNotFoundException": ("IO Error", "Java"),
    "UnsupportedOperationException": ("Runtime Error", "Java"),
    "NoSuchElementException": ("Runtime Error", "Java"),
    # Python
    "TypeError": ("Runtime Error", "Python"),
    "KeyError": ("Runtime Error", "Python"),
    "IndexError": ("Runtime Error", "Python"),
    "ImportError": ("Module Loading Error", "Python"),
    "ModuleNotFoundError": ("Module Loading Error", "Python"),
    "NameError": ("Runtime Error", "Python"),
    "AttributeError": ("Runtime Error", "Python"),
    "ValueError": ("Runtime Error", "Python"),
    "ZeroDivisionError": ("Runtime Error", "Python"),
    "SyntaxError": ("Syntax Error", "Python"),
    "IndentationError": ("Syntax Error", "Python"),
    "FileNotFoundError": ("IO Error", "Python"),
    "RecursionError": ("Runtime Error", "Python"),
    "StopIteration": ("Runtime Error", "Python"),
    "AssertionError": ("Runtime Error", "Python"),
    # JavaScript
    "TypeError": ("Runtime Error", "JavaScript"),
    "ReferenceError": ("Runtime Error", "JavaScript"),
    "SyntaxError": ("Syntax Error", "JavaScript"),
    "RangeError": ("Runtime Error", "JavaScript"),
    # SQL
    "SQL Syntax Error": ("Syntax Error", "SQL"),
    "SQL Constraint Error": ("Constraint Error", "SQL"),
    "SQL NULL Comparison Error": ("Logic Error", "SQL"),
    "Duplicate Error": ("Constraint Error", "SQL"),
    "Missing Column Error": ("Logic Error", "SQL"),
    "Missing Table Error": ("Logic Error", "SQL"),
    # React
    "Invalid Hook Call": ("React Error", "React"),
    "Invalid Hook Order": ("React Error", "React"),
    "Invalid React Element": ("React Error", "React"),
    "State Update on Unmounted Component": ("React Error", "React"),
}

# Reusable extraction patterns (ordered: most specific first).
ERROR_NAME_PATTERNS: List[tuple] = [
    (re.compile(r"java\.lang\.(\w+Exception)\b"), 1),
    (re.compile(r"(\w+Exception)\b"), 1),
    (re.compile(r"java\.lang\.(\w+Error)\b"), 1),
    (re.compile(r"(\w+Error)\b"), 2),
]
STOPWORDS = {
    "a", "an", "the", "in", "of", "on", "at", "to", "for", "and", "or", "is",
    "was", "are", "were", "be", "been", "has", "have", "had", "it", "its",
    "this", "that", "these", "those", "from", "with", "by", "as", "into",
    "cannot", "can", "not", "null", "undefined", "line", "error", "message",
    "while", "when", "during", "call", "calling", "called", "function",
    "method", "exception", "because", "so", "but", "if", "then", "than",
    "using", "use", "used", "value", "values", "return", "returns", "body",
    "main", "execute", "execution", "thread", "result", "results", "expected",
    "actual", "should", "could", "would", "might", "may", "missing",
    "java", "python", "javascript", "sql", "react", "lang",
}

CODE_KEYWORD_WEIGHTS: Dict[str, float] = {
    "null": 1.0, "undefined": 1.0, "nan": 1.0, "none": 0.8,
    "object": 0.9, "array": 0.9, "list": 0.9, "string": 0.9, "integer": 0.9,
    "function": 0.9, "variable": 0.8, "property": 0.9, "attribute": 0.9,
    "key": 0.8, "index": 0.9, "out": 0.7, "range": 0.8, "syntax": 1.0,
    "import": 0.9, "module": 0.9, "package": 0.8, "constraint": 1.0,
    "column": 0.9, "table": 0.9, "select": 0.8, "insert": 0.8, "update": 0.8,
    "delete": 0.8, "query": 0.9, "primary": 0.8, "foreign": 0.8,
    "user": 0.8, "name": 0.7, "id": 0.7, "state": 0.7, "hook": 0.9,
    "component": 0.9, "render": 0.9, "setstate": 0.8, "props": 0.8,
    "map": 0.7, "filter": 0.7, "length": 0.8, "size": 0.7, "stack": 0.7,
    "trace": 0.7, "thread": 0.8, "initialize": 0.8, "initialized": 0.8,
}


# --------------------------------------------------------------------------- #
# Data structures
# --------------------------------------------------------------------------- #

@dataclass
class AnalysisResult:
    detected_error: str = ""
    error_type: str = ""
    category: str = ""
    language: str = ""
    language_confidence: str = "High"
    framework: str = ""
    keywords: List[str] = field(default_factory=list)
    stack_frames: List[dict] = field(default_factory=list)
    raw_original: str = ""

    def as_dict(self) -> dict:
        return {
            "detected_error": self.detected_error,
            "error_type": self.error_type,
            "category": self.category,
            "language": self.language,
            "language_confidence": self.language_confidence,
            "framework": self.framework,
            "keywords": self.keywords,
            "stack_frames": self.stack_frames,
        }
# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _score_languages(text: str):
    """Return [(language, score)] sorted by score descending."""
    scores: Dict[str, float] = {}
    for lang, patterns in LANGUAGE_PATTERNS.items():
        total = 0.0
        for weight, rx in patterns:
            total += weight * len(rx.findall(text))
        if total > 0:
            scores[lang] = total
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)


def _find_error_name(text: str):
    """Return a canonical (error_name, category, language) from known signatures."""
    # direct signature scan first (handles Java names inside package prefixes)
    for name, (category, lang) in ERROR_SIGNATURES.items():
        if re.search(rf"\b{re.escape(name)}\b", text):
            return name, category, lang
    for rx, _priority in ERROR_NAME_PATTERNS:
        m = rx.search(text)
        if m:
            name = m.group(1)
            if name in ERROR_SIGNATURES:
                return name, *ERROR_SIGNATURES[name]
            if name.endswith("Exception"):
                lang = "Java" if re.search(r"java\.lang\.|\.java:", text) else "Unknown"
                return name, "Runtime Error", lang
            if name.endswith("Error"):
                lang = "Java" if re.search(r"java\.lang\.|\.java:", text) else ""
                return name, "Error", lang or ""
    return "", "", ""


def _extract_stack_frames(text: str, limit: int = 8):
    frames: list = []
    # Each entry: (regex, group_index_of_file, group_index_of_line)
    patterns = [
        (re.compile(r"(?:\A|\s+)at\s+([\w.$<>]+)\(([^:]+):(\d+)\)"), 2, 3),
        (re.compile(r'File "([^"]+\.(?:py|js|ts|jsx|tsx))", line (\d+)'), 1, 2),
        (re.compile(r"(?:\A|\s+)at\s+([\w.$<>]+)\s+\(([^:]+):(\d+)\)"), 2, 3),
        (re.compile(r"(?:\A|\s+)at\s+([\w.$]+):(\d+)"), 1, 2),  # bare "at File.java:42"
    ]
    for rx, file_grp, line_grp in patterns:
        for m in rx.finditer(text):
            file_name = m.group(file_grp)
            line_num = m.group(line_grp)
            frames.append(
                {
                    "location": f"{file_name}:{line_num}",
                    "file": file_name,
                    "line": line_num,
                }
            )
            if len(frames) >= limit:
                return frames
    return frames


def _extract_keywords(text: str, error_name: str, max_keywords: int = 12):
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]{1,}", text)
    scored: Dict[str, float] = {}
    order: list = []

    def add(token: str, weight: float) -> None:
        lower = token.lower()
        if lower in STOPWORDS or len(lower) < 2:
            return
        base = CODE_KEYWORD_WEIGHTS.get(lower, 0.6)
        if lower not in scored:
            scored[lower] = 0.0
            order.append(lower)
        scored[lower] += base * weight

    for token in tokens:
        if re.match(r"^[A-Z][A-Za-z0-9_]*$", token):
            add(token, 1.5)  # PascalCase → class/type-ish
        elif re.match(r"^[a-z][A-Za-z0-9_]*$", token):
            add(token, 1.0)

    for token in error_name.replace("_", " ").split():
        add(token, 2.0)

    ranked = sorted(order, key=lambda t: scored[t], reverse=True)
    return ranked[:max_keywords]


def _detect_framework(text: str, language: str) -> str:
    if language.lower() == "react":
        return "React"
    return ""


# --------------------------------------------------------------------------- #
# Main entrypoint
# --------------------------------------------------------------------------- #


def analyze(text: str, language_hint: str = "auto") -> AnalysisResult:
    """Analyze a user input and produce a structured AnalysisResult."""
    original = text
    text = (text or "").strip()
    result = AnalysisResult(raw_original=original)

    if not text:
        return result

    lang_scores = _score_languages(text)
    error_name, category, sig_lang = _find_error_name(text)

    # --- Language resolution -------------------------------------------------
    forced = (language_hint or "auto").strip().lower()
    if forced and forced != "auto":
        if forced == "javascript":
            result.language = "JavaScript"
        elif forced == "sql":
            result.language = "SQL"
        elif forced == "react":
            result.language = "React"
        else:
            result.language = forced.capitalize()
        result.language_confidence = "High"
    elif lang_scores:
        best_lang, best_score = lang_scores[0]
        result.language = best_lang
        result.language_confidence = (
            "High" if best_score >= 1.5 else "Medium" if best_score >= 0.5 else "Low"
        )
        if sig_lang and best_score < 0.5:
            result.language = sig_lang
            result.language_confidence = "Medium"
    elif sig_lang:
        result.language = sig_lang
        result.language_confidence = "Medium"

    new_lang = {
        "java": "Java", "python": "Python", "js": "JavaScript",
        "javascript": "JavaScript", "jsx": "React", "tsx": "React",
        "sql": "SQL", "react": "React",
    }.get(result.language.lower(), result.language)
    if new_lang == "React" or re.search(r"\b(useState|useEffect|import React)\b", text):
        result.framework = "React"
    result.language = new_lang

    # --- Error identity ------------------------------------------------------
    if error_name:
        result.detected_error = error_name
        result.error_type = error_name
        result.category = category or "Unknown"
    else:
        m = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*Exception)\b", text)
        if m:
            result.detected_error = m.group(1)
            result.error_type = "Exception"
            result.category = "Runtime Error"
        text_lower = text.lower()
        if not result.detected_error:
            if "syntax error" in text_lower and result.language:
                result.detected_error = "Syntax Error"
                result.error_type = "Syntax Error"
                result.category = "Syntax Error"
            elif "constraint" in text_lower and result.language.lower() == "sql":
                result.detected_error = "SQL Constraint Error"
                result.error_type = "Constraint"
                result.category = "Constraint Error"
            elif "duplicate key" in text_lower and result.language.lower() == "sql":
                result.detected_error = "Duplicate Error"
                result.error_type = "Constraint"
                result.category = "Constraint Error"
            elif result.language.lower() == "sql" and re.search(r"=\s*NULL|IS NULL", text, re.IGNORECASE):
                result.detected_error = "SQL NULL Comparison Error"
                result.error_type = "NULL handling"
                result.category = "Logic Error"

    # --- Stack trace, keywords, framework ------------------------------------
    result.stack_frames = _extract_stack_frames(text)
    result.keywords = _extract_keywords(text, result.detected_error)
    result.framework = _detect_framework(text, result.language)

    return result