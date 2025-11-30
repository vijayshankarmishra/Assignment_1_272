from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import os
from dataclasses import dataclass
from typing import List, Tuple

app = Flask(__name__)
CORS(app)

# Word bank
WORD_BANK = [
    "python", "developer", "keyboard", "notebook", "algorithm", "function", "variable",
    "compose", "docker", "github", "machine", "learning", "network", "browser",
    "package", "library", "module", "integer", "string", "boolean", "operator",
    "system", "process", "thread", "memory", "storage", "buffer", "socket", "server",
    "client", "request", "response", "timeout", "session", "cookie", "token",
    "kubernetes", "microservice", "container", "deployment", "service", "ingress",
    "replica", "cluster", "namespace", "configmap", "secret", "volume", "pod",
]

@dataclass
class Question:
    answer: str
    masked: str
    options: List[str]
    correctIndex: int


def mask_word(word: str) -> str:
    """Mask random characters in a word with underscores."""
    if len(word) <= 2:
        return "_" * len(word)
    
    # Randomly hide between 1 and max(len-1) characters
    num_to_hide = random.randint(1, max(1, len(word) - 1))
    indices = list(range(len(word)))
    random.shuffle(indices)
    hide = set(indices[:num_to_hide])
    
    return "".join("_" if i in hide else ch for i, ch in enumerate(word))


def generate_options(answer: str, bank: List[str], k: int = 4) -> Tuple[List[str], int]:
    """Generate multiple choice options including the correct answer."""
    # Try to get words of same length first
    same_len = [w for w in bank if w != answer and len(w) == len(answer)]
    pool = same_len if len(same_len) >= k - 1 else [w for w in bank if w != answer]
    
    # Select distractors
    if len(pool) >= k - 1:
        distractors = random.sample(pool, k - 1)
    else:
        distractors = random.choices(pool, k=k - 1)
    
    # Combine and shuffle
    options = distractors + [answer]
    random.shuffle(options)
    
    return options, options.index(answer)


def make_question(bank: List[str]) -> Question:
    """Create a complete quiz question."""
    answer = random.choice(bank)
    masked = mask_word(answer)
    options, idx = generate_options(answer, bank, 4)
    
    return Question(
        answer=answer,
        masked=masked,
        options=options,
        correctIndex=idx
    )


# ============================================
# API Routes
# ============================================

@app.route('/quiz/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'quiz-service',
        'wordBankSize': len(WORD_BANK),
    }), 200


@app.route('/quiz/generate', methods=['GET'])
def generate_question():
    """Generate a new quiz question."""
    try:
        question = make_question(WORD_BANK)
        
        return jsonify({
            'answer': question.answer,
            'masked': question.masked,
            'options': question.options,
            'correctIndex': question.correctIndex,
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error generating question: {str(e)}")
        return jsonify({
            'error': 'Failed to generate question',
            'message': str(e)
        }), 500


@app.route('/quiz/validate', methods=['POST'])
def validate_answer():
    """Validate a user's answer."""
    try:
        data = request.get_json()
        answer = data.get('answer')
        selected_option = data.get('selectedOption')
        
        if not answer or not selected_option:
            return jsonify({
                'error': 'Missing required fields',
                'required': ['answer', 'selectedOption']
            }), 400
        
        is_correct = answer.lower() == selected_option.lower()
        
        return jsonify({
            'correct': is_correct,
            'answer': answer,
            'selectedOption': selected_option,
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error validating answer: {str(e)}")
        return jsonify({
            'error': 'Failed to validate answer',
            'message': str(e)
        }), 500


@app.route('/quiz/words', methods=['GET'])
def get_words():
    """Get word bank information."""
    return jsonify({
        'totalWords': len(WORD_BANK),
        'categories': {
            'programming': ['python', 'developer', 'algorithm', 'function', 'variable'],
            'technology': ['docker', 'kubernetes', 'github', 'microservice', 'container'],
            'computing': ['memory', 'storage', 'processor', 'thread', 'system'],
        },
        'averageLength': sum(len(w) for w in WORD_BANK) / len(WORD_BANK),
        'shortest': min(WORD_BANK, key=len),
        'longest': max(WORD_BANK, key=len),
    }), 200


@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information."""
    return jsonify({
        'service': 'Quiz Service',
        'version': '1.0.0',
        'description': 'Microservice for generating word quiz questions',
        'endpoints': {
            'health': 'GET /quiz/health',
            'generate': 'GET /quiz/generate',
            'validate': 'POST /quiz/validate',
            'words': 'GET /quiz/words',
        }
    }), 200


# ============================================
# Error Handlers
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested endpoint does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500


# ============================================
# Main
# ============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"🎯 Quiz Service starting on port {port}")
    print(f"📚 Word bank size: {len(WORD_BANK)} words")
    print(f"🔧 Debug mode: {debug}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
