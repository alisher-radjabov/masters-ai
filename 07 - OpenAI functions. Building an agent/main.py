from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'  # SQLite database
db = SQLAlchemy(app)

# Define a simple model for our database
class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    answer = db.Column(db.String(500), nullable=False)

# Initialize the database
@app.before_request
def create_tables():
    db.create_all()

# Endpoint to add data to the database
@app.route('/add_data', methods=['POST'])
def add_data():
    data = request.get_json()
    new_data = Data(question=data['question'], answer=data['answer'])
    db.session.add(new_data)
    db.session.commit()
    return jsonify({"message": "Data added successfully!"}), 200

# Agent function to query the database
def agent_answer(question):
    result = Data.query.filter(Data.question.like(f'%{question}%')).first()
    if result:
        return result.answer
    return "Sorry, I don't know the answer to that question."

# Endpoint to get answer from the agent
@app.route('/ask', methods=['GET'])
def ask():
    question = request.args.get('question')
    if question:
        answer = agent_answer(question)
        return jsonify({"question": question, "answer": answer})
    return jsonify({"error": "Please provide a question."}), 400

if __name__ == '__main__':
    app.run(debug=True)