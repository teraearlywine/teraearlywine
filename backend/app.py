from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will allow cross-origin requests from any domain

@app.route('/')
def index():
    return jsonify({"message": "Welcome to the interactive resume website"})

@app.route('/api/experience')
def experience():
    # Sample data (replace this with data from a DB or any other source)
    return jsonify([
        {"company": "Company A", "role": "Data Engineer", "years": "2018-2021"},
        {"company": "Company B", "role": "Full Stack Engineer", "years": "2021-2023"}
    ])

@app.route('/api/education')
def education():
    return jsonify([{
        "school": "University of Portland",
        "degree": "B.B.A Operations & Technology Management",
        "years": "2014-2018"
    }])

@app.route('/api/skills')
def skills():
    return jsonify(["Python", "React", "Flask", "Data Engineering", "SQL"])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)