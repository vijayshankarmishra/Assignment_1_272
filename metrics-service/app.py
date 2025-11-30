from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime
from collections import defaultdict
from threading import Lock

app = Flask(__name__)
CORS(app)

# In-memory storage (in production, use a database)
metrics_store = {
    'answers': [],
    'sessions': {},
}
store_lock = Lock()


# ============================================
# Helper Functions
# ============================================

def calculate_stats():
    """Calculate aggregate statistics from stored metrics."""
    with store_lock:
        answers = metrics_store['answers']
        sessions = metrics_store['sessions']
        
        if not answers:
            return {
                'totalQuestions': 0,
                'correctAnswers': 0,
                'accuracy': '0.0',
                'totalSessions': 0,
                'averageScore': '0.0',
            }
        
        total_questions = len(answers)
        correct_answers = sum(1 for a in answers if a.get('correct', False))
        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Calculate session stats
        session_scores = defaultdict(int)
        for answer in answers:
            session_id = answer.get('sessionId', 'unknown')
            if answer.get('correct', False):
                session_scores[session_id] += 1
        
        total_sessions = len(session_scores)
        average_score = sum(session_scores.values()) / total_sessions if total_sessions > 0 else 0
        
        return {
            'totalQuestions': total_questions,
            'correctAnswers': correct_answers,
            'accuracy': f'{accuracy:.1f}',
            'totalSessions': total_sessions,
            'averageScore': f'{average_score:.1f}',
            'lastUpdated': datetime.utcnow().isoformat(),
        }


# ============================================
# API Routes
# ============================================

@app.route('/metrics/health', methods=['GET'])
def health():
    """Health check endpoint."""
    with store_lock:
        stored_count = len(metrics_store['answers'])
    
    return jsonify({
        'status': 'healthy',
        'service': 'metrics-service',
        'storedMetrics': stored_count,
    }), 200


@app.route('/metrics/record', methods=['POST'])
def record_metric():
    """Record a quiz attempt metric."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['sessionId', 'correct']
        missing_fields = [f for f in required_fields if f not in data]
        
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing': missing_fields
            }), 400
        
        # Add timestamp if not present
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow().isoformat()
        
        # Store metric
        with store_lock:
            metrics_store['answers'].append(data)
            
            # Update session info
            session_id = data['sessionId']
            if session_id not in metrics_store['sessions']:
                metrics_store['sessions'][session_id] = {
                    'startTime': data['timestamp'],
                    'questions': 0,
                    'correct': 0,
                }
            
            metrics_store['sessions'][session_id]['questions'] += 1
            if data['correct']:
                metrics_store['sessions'][session_id]['correct'] += 1
        
        app.logger.info(f"Recorded metric for session {session_id}")
        
        return jsonify({
            'success': True,
            'message': 'Metric recorded successfully',
            'sessionId': session_id,
        }), 201
        
    except Exception as e:
        app.logger.error(f"Error recording metric: {str(e)}")
        return jsonify({
            'error': 'Failed to record metric',
            'message': str(e)
        }), 500


@app.route('/metrics/stats', methods=['GET'])
def get_stats():
    """Get aggregate statistics."""
    try:
        stats = calculate_stats()
        return jsonify(stats), 200
        
    except Exception as e:
        app.logger.error(f"Error calculating stats: {str(e)}")
        return jsonify({
            'error': 'Failed to calculate statistics',
            'message': str(e)
        }), 500


@app.route('/metrics/session/<session_id>', methods=['GET'])
def get_session_stats(session_id):
    """Get statistics for a specific session."""
    try:
        with store_lock:
            if session_id not in metrics_store['sessions']:
                return jsonify({
                    'error': 'Session not found',
                    'sessionId': session_id
                }), 404
            
            session_data = metrics_store['sessions'][session_id]
            session_answers = [
                a for a in metrics_store['answers'] 
                if a.get('sessionId') == session_id
            ]
        
        return jsonify({
            'sessionId': session_id,
            'questions': session_data['questions'],
            'correct': session_data['correct'],
            'accuracy': f"{(session_data['correct'] / session_data['questions'] * 100):.1f}" if session_data['questions'] > 0 else '0.0',
            'startTime': session_data['startTime'],
            'answers': session_answers,
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error fetching session stats: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch session statistics',
            'message': str(e)
        }), 500


@app.route('/metrics/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get top scoring sessions."""
    try:
        with store_lock:
            sessions = metrics_store['sessions']
        
        # Calculate scores and sort
        leaderboard = []
        for session_id, data in sessions.items():
            score = data['correct']
            total = data['questions']
            accuracy = (score / total * 100) if total > 0 else 0
            
            leaderboard.append({
                'sessionId': session_id[:12] + '...',  # Truncate for privacy
                'score': f"{score}/{total}",
                'accuracy': f"{accuracy:.1f}%",
                'timestamp': data['startTime'],
            })
        
        # Sort by score (correct answers) descending
        leaderboard.sort(key=lambda x: int(x['score'].split('/')[0]), reverse=True)
        
        return jsonify({
            'leaderboard': leaderboard[:10],  # Top 10
            'totalSessions': len(leaderboard),
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error generating leaderboard: {str(e)}")
        return jsonify({
            'error': 'Failed to generate leaderboard',
            'message': str(e)
        }), 500


@app.route('/metrics/reset', methods=['POST'])
def reset_metrics():
    """Reset all metrics (for testing purposes)."""
    try:
        with store_lock:
            metrics_store['answers'].clear()
            metrics_store['sessions'].clear()
        
        app.logger.warning("All metrics have been reset")
        
        return jsonify({
            'success': True,
            'message': 'All metrics have been reset'
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error resetting metrics: {str(e)}")
        return jsonify({
            'error': 'Failed to reset metrics',
            'message': str(e)
        }), 500


@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information."""
    return jsonify({
        'service': 'Metrics Service',
        'version': '1.0.0',
        'description': 'Microservice for tracking quiz performance metrics',
        'endpoints': {
            'health': 'GET /metrics/health',
            'record': 'POST /metrics/record',
            'stats': 'GET /metrics/stats',
            'session': 'GET /metrics/session/<session_id>',
            'leaderboard': 'GET /metrics/leaderboard',
            'reset': 'POST /metrics/reset',
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
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"📊 Metrics Service starting on port {port}")
    print(f"🔧 Debug mode: {debug}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
