from flask import Blueprint, request, jsonify
from utils.auth import token_required
from utils.ai_chat import generate_sql, validate_query, execute_safe_query, format_answer

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')


@chat_bp.route('', methods=['POST'])
@token_required
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400

    question = data['message']

    try:
        # Step 1: Generate SQL from natural language
        sql = generate_sql(question)

        # Step 2: Validate the query is safe
        if not validate_query(sql):
            return jsonify({
                'answer': 'I could only generate a query that modifies data, which is not allowed. Please rephrase your question.',
                'sql': sql,
            }), 400

        # Step 3: Execute the query
        columns, rows = execute_safe_query(sql)

        # Step 4: Format the answer
        answer = format_answer(question, columns, rows)

        return jsonify({
            'answer': answer,
            'sql': sql,
            'row_count': len(rows),
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({
            'answer': f'Sorry, I had trouble processing that question. Error: {str(e)}',
            'sql': None,
        }), 500
