import os
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_math_solver(question):
    """
    Uses Groq's Llama 3.3 70B model to solve math problems with proper mathematical notation.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": """You are a professional math teacher. Solve problems using proper mathematical notation.

CRITICAL FORMATTING RULES:
1. Use proper mathematical symbols:
   - Use ∫ for integrals
   - Use proper fractions like \frac{1}{3}
   - Use ^ for exponents
   - Use √ for square roots
   - Use π, θ, α for Greek letters
   - Use ∞ for infinity
   - Use ≤, ≥, ≠, ±, ×, ÷

2. Format steps with numbers (1., 2., 3.)

3. Each mathematical expression should be on its own line

4. Use LaTeX notation for complex expressions

5. Final answer should be clearly marked

Example format:
1. Identify the integral: ∫ e^(3x) dx
2. Recall the formula: ∫ e^(ax) dx = (1/a) e^(ax) + C
3. Here a = 3
4. Apply the formula: (1/3) e^(3x) + C

Final Answer: (1/3)e^(3x) + C

Remember: Use mathematical notation, not plain English descriptions."""},
                {"role": "user", "content": f"Solve: {question}"}
            ],
            temperature=0.2,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Groq Error: {str(e)}"

def generate_teaching_guide(topic):
    """
    Uses Groq to generate teaching guides with proper mathematical notation.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": """You are an expert math teacher. Create teaching guides using proper mathematical notation.

Use mathematical symbols: ∫, ∑, √, ∞, π, θ, α, β, γ, δ, ≤, ≥, ≠, ±, ×, ÷, ≈

Include:
- Key formulas using proper notation
- Worked examples with step-by-step solutions
- Practice problems with mathematical expressions

Keep formatting clean and mathematical."""},
                {"role": "user", "content": f"Create a teaching guide for: {topic}"}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Groq Error: {str(e)}"

# ========== MATHEMATICAL SYMBOLS AND CONVERSIONS ==========

def sanitize_filename(text):
    """Sanitizes a string to be safe for use as a filename."""
    return re.sub(r'[^\w\s-]', '', text).strip().replace(' ', '_')[:50]

# Unicode mathematical symbols
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
    r'\\alpha': 'α', r'\\beta': 'β', r'\\gamma': 'γ', r'\\delta': 'δ',
    r'\\epsilon': 'ε', r'\\theta': 'θ', r'\\lambda': 'λ', r'\\mu': 'μ',
    r'\\pi': 'π', r'\\rho': 'ρ', r'\\sigma': 'σ', r'\\tau': 'τ',
    r'\\phi': 'φ', r'\\omega': 'ω', r'\\infty': '∞'
}

def to_superscript(expr):
    return ''.join(SUPERSCRIPTS.get(c, c) for c in expr)

def to_subscript(expr):
    return ''.join(SUBSCRIPTS.get(c, c) for c in expr)

def latex_to_readable(text):
    """Convert LaTeX to clean mathematical notation with Unicode symbols."""
    if not text:
        return ""
    
    # Replace Greek letters
    for latex, symbol in GREEK.items():
        text = text.replace(latex, symbol)

    # Replace LaTeX math symbols
    replacements = {
        r'\\leq': '≤', r'\\geq': '≥', r'\\le': '≤', r'\\ge': '≥',
        r'\\neq': '≠', r'\\times': '×', r'\\div': '÷', r'\\pm': '±',
        r'\\sqrt': '√', r'\\infty': '∞', r'\\approx': '≈',
        r'\\int': '∫', r'\\partial': '∂', r'\\sum': '∑',
        r'\\prod': '∏', r'\\theta': 'θ', r'\\lambda': 'λ'
    }
    for key, val in replacements.items():
        text = text.replace(key, val)

    # Handle integrals
    text = re.sub(r'\\int_{([^}]+)}^{([^}]+)}', r'∫[\\1 to \\2]', text)
    text = re.sub(r'\\int', '∫', text)
    
    # Handle fractions
    text = re.sub(r'\\frac\s*{([^}]+)}{([^}]+)}', r'\\1/\\2', text)
    
    # Handle roots
    text = re.sub(r'\\sqrt{([^}]+)}', r'√\\1', text)
    
    # Handle exponents
    text = re.sub(r'(\w)\^(\d+)', lambda m: m.group(1) + to_superscript(m.group(2)), text)
    text = re.sub(r'(\w)\^{([^}]+)}', lambda m: m.group(1) + '^' + m.group(2), text)
    
    # Handle subscripts
    text = re.sub(r'(\w)_(\d+)', lambda m: m.group(1) + to_subscript(m.group(2)), text)
    
    # Remove remaining backslashes
    text = text.replace('\\', '')
    
    # Remove curly braces
    text = text.replace('{', '').replace('}', '')
    
    return text.strip()

# ========== TEST ==========
if __name__ == "__main__":
    test_question = "Integrate e^(3x) dx"
    print(f"Question: {test_question}\n")
    print("="*60)
    result = ask_math_solver(test_question)
    print("Solution:")
    print(result)
    print("\n" + "="*60)
    print("Readable version:")
    print(latex_to_readable(result))