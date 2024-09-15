Here's your Python code revised for better readability, efficiency, and compliance with PEP8 standards:

```python
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable cross-origin requests from any domain


@app.route('/')
def index():
    """Root endpoint returning a welcome message."""
    return jsonify({"message": "Welcome to the interactive resume website"})


@app.route('/api/header')
def header():
    """Endpoint returning header data."""
    # Sample data (replace this with data from a DB or any other source)
    return jsonify({
        "email": "info@teraearlywine.com",
        "linkedin": "https://www.linkedin.com/in/teraearlywine/",
        "github": "https://github.com/teraearlywine"
    })


@app.route('/api/experience')
def experience():
    """Endpoint returning work experience data."""
    # Sample data (replace this with data from a DB or any other source)
    return jsonify([
        {"company": "Mercari", "role": "Business Intelligence Analyst", "years": "2018-2021"},
        {"company": "This is Alice", "role": "Data Analytics Engineer", "years": "2021-2022"},
        {"company": "Mercari", "role": "Data Engineer", "years": "2022-2024"}
    ])


@app.route('/api/education')
def education():
    """Endpoint returning education data."""
    return jsonify({
        "school": "University of Portland",
        "degree": "B.B.A Operations & Technology Management",
        "years": "2014-2018"
    })


@app.route('/api/skills')
def skills():
    """Endpoint returning skills data."""
    return jsonify(["Python", "React", "Flask", "Data Engineering", "SQL"])


def main():
    """Main function to run the app."""
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
```
In this revision, I've added docstrings to the functions for better readability and understanding of what each function does. I also packed the running of the application into a separate function called `main()`. This makes the code more modular and makes it easier to manage the application's initialization logic.