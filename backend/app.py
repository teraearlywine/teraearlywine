```python
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from any domain

@app.route('/')
def index():
    return jsonify({"message": "Welcome to the interactive resume website"})

@app.route('/api/header')
def header():
    """Return header information with contact links."""
    return jsonify({
        "email": "info@teraearlywine.com",
        "linkedin": "https://www.linkedin.com/in/teraearlywine/",
        "github": "https://github.com/teraearlywine"
    })

@app.route('/api/experience')
def experience():
    """Return a list of work experiences."""
    return jsonify([
        {"company": "Mercari", "role": "Business Intelligence Analyst", "years": "2018-2021"},
        {"company": "This is Alice", "role": "Data Analytics Engineer", "years": "2021-2022"},
        {"company": "Mercari", "role": "Data Engineer", "years": "2022-2024"}
    ])

@app.route('/api/education')
def education():
    """Return educational background."""
    return jsonify([{
        "school": "University of Portland",
        "degree": "B.B.A Operations & Technology Management",
        "years": "2014-2018"
    }])

@app.route('/api/skills')
def skills():
    """Return a list of skills."""
    return jsonify(["Python", "React", "Flask", "Data Engineering", "SQL"])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```