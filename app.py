import flask
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import random
import string
import math
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

app.template_folder = os.path.abspath('templates')
app.static_folder = os.path.abspath('static')

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory('static/audio', filename)

def generate_complex_operation():
    easy_operations = [
        ('+', lambda a, b: (f"{a} + {b}", a + b)),
        ('-', lambda a, b: (f"{a} - {b}", a - b)),
        ('*', lambda a, b: (f"{a} * {b}", a * b))
    ]
    hard_operations = [
        ('/', lambda a, b: (f"{a} / {b}", a / b) if b != 0 else (f"{a} / 1", a)),
        ('square', lambda a, b: (f"{a}²", a ** 2)),
        ('cube', lambda a, b: (f"{a}³", a ** 3)),
        ('sqrt', lambda a, b: (f"√{a*a}", a)),
        ('power', lambda a, b: (f"{a}^{b}", a ** b))
    ]
    return easy_operations if random.random() < 0.7 else hard_operations

def generate_problem(difficulty=1):
    operations = generate_complex_operation()
    operation_type, operation_func = random.choice(operations)

    if difficulty == 1:
        if operation_type in ['+', '-']:
            a, b = random.randint(1, 20), random.randint(1, 10)
        elif operation_type == '*':
            a, b = random.randint(2, 9), random.randint(2, 5)
        else:
            a, b = random.randint(1, 5), random.randint(1, 3)
    else:
        if operation_type in ['+', '-']:
            a, b = random.randint(50, 200), random.randint(25, 100)
        elif operation_type == '*':
            a, b = random.randint(10, 30), random.randint(5, 15)
        elif operation_type == '/':
            b = random.randint(2, 12)
            a = b * random.randint(5, 20)
        elif operation_type in ['square', 'cube']:
            a = random.randint(8, 15)
        elif operation_type == 'sqrt':
            a = random.randint(5, 12)
            a = a * a
        else:
            a, b = random.randint(2, 10), random.randint(2, 4)

    expression, result = operation_func(a, b)

    numbers = list(str(a) + (str(b) if operation_type in ['+', '-', '*', '/', 'power'] else ''))
    unique_numbers = list(set(numbers))
    letters = random.sample(string.ascii_uppercase, len(unique_numbers))
    mapping = dict(zip(unique_numbers, letters))

    if operation_type in ['+', '-', '*', '/']:
        parts = expression.split()
        a_letters = ''.join(mapping[d] for d in str(parts[0]))
        b_letters = ''.join(mapping[d] for d in str(parts[2]))
        letter_expression = f"{a_letters} {parts[1]} {b_letters}"
    elif operation_type in ['square', 'cube']:
        a_letters = ''.join(mapping[d] for d in str(a))
        letter_expression = f"{a_letters}{expression[-1]}"
    elif operation_type == 'sqrt':
        a_letters = ''.join(mapping[d] for d in str(a*a))
        letter_expression = f"√{a_letters}"
    else:
        a_letters = ''.join(mapping[d] for d in str(a))
        b_letters = ''.join(mapping[d] for d in str(b))
        letter_expression = f"{a_letters}^{b_letters}"

    hints = [
        "Break down the problem into smaller parts",
        "Look for patterns in the letter combinations",
        "Consider the relationship between the numbers"
    ] if difficulty == 2 else [
        "Start by finding the most common letter in the problem",
        "Try solving the easiest operation first"
    ]

    return {
        'expression': letter_expression,
        'operation_type': operation_type,
        'mapping': {v: k for k, v in mapping.items()},
        'result': round(result),
        'hints': hints
    }

@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/get_problem')
def get_problem():
    difficulty = int(request.args.get('difficulty', 1))
    problem = generate_problem(difficulty)
    return jsonify(problem)

@app.route('/check_answer', methods=['POST'])
def check_answer():
    data = request.json
    user_answer = float(data['answer'])
    correct_answer = float(data['correct_answer'])
    remaining_time = float(data['time_taken'])
    
    base_score = 10 if data['difficulty'] == 2 else 5
    is_correct = abs(user_answer - correct_answer) < 0.01
    
   
    
    if is_correct:
        remaining_time += 5  # Add 5 seconds for correct answer
    else:
        remaining_time -= 10  # Subtract 10 seconds for wrong answer
        
    remaining_time = max(0, min(50, remaining_time))
    
    if remaining_time > 50:
        time_multiplier = 0.0
    elif remaining_time >= 41 and remaining_time <= 50:  # Changed to elif
        time_multiplier = 0.2
    elif remaining_time >= 31 and remaining_time <= 40:
        time_multiplier = 0.4
    elif remaining_time >= 21 and remaining_time <= 30:
        time_multiplier = 0.6
    elif remaining_time >= 11 and remaining_time <= 20:
        time_multiplier = 0.8
    elif remaining_time >= 1 and remaining_time <= 10:
        time_multiplier = 1.0
    else:
        time_multiplier = 0.0
        
    score = int(base_score * time_multiplier)
    

    return jsonify({
        'score': score,
        'is_correct': is_correct,
        'remaining_time': remaining_time
    })

if __name__ == '__main__':  
    app.run(debug=True)
