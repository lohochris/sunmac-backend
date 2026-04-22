import os
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_math_solver(question):
    """
    Uses Groq's Llama 3.3 70B model to solve math problems.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # ✅ Working model
            messages=[
                {"role": "system", "content": "You're a math teacher. Solve math problems step by step."},
                {"role": "user", "content": question}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Groq Error: {str(e)}"

# ========== YOUR EXISTING HELPER FUNCTIONS ==========
def sanitize_filename(text):
    """Sanitizes a string to be safe for use as a filename."""
    return re.sub(r'[^\w\s-]', '', text).strip().replace(' ', '_')[:50]

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
    """Convert LaTeX math to readable plain text with Unicode symbols."""
    if not text:
        return ""
    
    # Replace Greek letters
    for latex, symbol in GREEK.items():
        text = text.replace(latex, symbol)

    # Replace LaTeX math symbols
    replacements = {
        r'\leq': '≤', r'\geq': '≥', r'\le': '≤', r'\ge': '≥',
        r'\neq': '≠', r'\times': '×', r'\div': '÷', r'\pm': '±',
        r'\sqrt': '√', r'\infty': '∞', r'\approx': '≈'
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

# ========== TEST ==========
if __name__ == "__main__":
    # Test with a math problem
    test_question = "What is the derivative of x^2 + 3x + 5?"
    print(f"Question: {test_question}\n")
    print("="*60)
    
    result = ask_math_solver(test_question)
    print("Answer:")
    print(result)
    
    # Optional: Convert LaTeX to readable format
    print("\n" + "="*60)
    print("Readable version:")
    print(latex_to_readable(result))