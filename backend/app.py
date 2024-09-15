from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Welcome to the interactive resume website"})


@app.route('/api/header', methods=['GET'])
def header():
    return jsonify([{
        "email": "info@teraearlywine.com",
        "linkedin": "https://www.linkedin.com/in/teraearlywine/",
        "github": "https://github.com/teraearlywine"
    }])


@app.route('/api/experience', methods=['GET'])
def experience():
    return jsonify([
        {"company": "Mercari", "role": "Business Intelligence Analyst", "years": "2018-2021"},
        {"company": "This is Alice", "role": "Data Analytics Engineer", "years": "2021-2022"},
        {"company": "Mercari", "role": "Data Engineer", "years": "2022-2024"}
    ])


@app.route('/api/education', methods=['GET'])
def education():
    return jsonify([{
        "school": "University of Portland",
        "degree": "B.B.A Operations & Technology Management",
        "years": "2014-2018"
    }])


@app.route('/api/skills', methods=['GET'])
def skills():
    return jsonify(["Python", "React", "Flask", "Data Engineering", "SQL"])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)