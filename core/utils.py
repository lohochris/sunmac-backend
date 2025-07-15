import openai, os
from dotenv import load_dotenv
load_dotenv()

def ask_openai_math_solver(question):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You're a math teacher. Solve math problems step by step."},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message['content'].strip()

import re

def sanitize_filename(text):
    """
    Sanitizes a string to be safe for use as a filename.
    Removes or replaces characters that are invalid in filenames.
    """
    return re.sub(r'[^\w\s-]', '', text).strip().replace(' ', '_')[:50]


def latex_to_readable(text):
    """Convert simple LaTeX math to readable plain text."""
    if not text:
        return ""

    # Replace common LaTeX symbols
    replacements = {
        r"\geq": "≥",
        r"\leq": "≤",
        r"\neq": "≠",
        r"\times": "×",
        r"\div": "÷",
        r"\cdot": "·",
        r"\sqrt": "√",
        r"\infty": "∞",
        r"\approx": "≈",
        r"\pm": "±",
        r"\frac": "/",
        r"\left": "",
        r"\right": "",
        r"\\": "",
        r"\(": "",
        r"\)": "",
        r"\[": "",
        r"\]": "",
        r"{": "",
        r"}": "",
        r"\,": " ",
    }

    for latex, plain in replacements.items():
        text = text.replace(latex, plain)

    # Remove math dollar signs
    text = re.sub(r'\$(.*?)\$', r'\1', text)

    return text.strip()


SUPERSCRIPTS = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
    '+': '⁺', '-': '⁻', '=': '=', '(': '⁽', ')': '⁾'
}

SUBSCRIPTS = {
    '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
    '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
    '+': '₊', '-': '₋', '=': '=', '(': '₍', ')': '₎'
}

GREEK = {
    r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ', r'\delta': 'δ',
    r'\epsilon': 'ε', r'\theta': 'θ', r'\lambda': 'λ', r'\mu': 'μ',
    r'\pi': 'π', r'\rho': 'ρ', r'\sigma': 'σ', r'\tau': 'τ',
    r'\phi': 'φ', r'\omega': 'ω'
}

def to_superscript(expr):
    return ''.join(SUPERSCRIPTS.get(c, c) for c in expr)

def to_subscript(expr):
    return ''.join(SUBSCRIPTS.get(c, c) for c in expr)

def latex_to_readable(text):
    # Replace Greek letters
    for latex, symbol in GREEK.items():
        text = text.replace(latex, symbol)

    # Replace LaTeX math symbols
    replacements = {
        r'\leq': '≤', r'\geq': '≥', r'\le': '≤', r'\ge': '≥',
        r'\neq': '≠', r'\times': '×', r'\div': '÷', r'\pm': '±',
        r'\sqrt': '√'
    }
    for key, val in replacements.items():
        text = text.replace(key, val)

    # Replace \frac{a}{b} → a/b
    text = re.sub(r'\\frac\s*{(.+?)}{(.+?)}', r'\1/\2', text)

    # Replace \sqrt{value} → √value
    text = re.sub(r'√{(.+?)}', r'√\1', text)

    # Remove LaTeX curly braces and dollar signs
    text = text.replace('{', '').replace('}', '').replace('$', '')

    # Grouped superscript (e.g. (x+1)^2)
    text = re.sub(r'(\(.+?\))\^(\d+)', lambda m: m.group(1) + to_superscript(m.group(2)), text)

    # Grouped subscript (e.g. (n+1)_2)
    text = re.sub(r'(\(.+?\))_(\d+)', lambda m: m.group(1) + to_subscript(m.group(2)), text)

    # x^2 → x²
    text = re.sub(r'(\w)\^(\d+)', lambda m: m.group(1) + to_superscript(m.group(2)), text)

    # x_1 → x₁
    text = re.sub(r'(\w)_(\d+)', lambda m: m.group(1) + to_subscript(m.group(2)), text)

    return text.strip()
