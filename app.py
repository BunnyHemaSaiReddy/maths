from flask import Flask, render_template, request, redirect, url_for, send_file, session
from datetime import datetime
from generate_pdf import create_certificate
import json
import os

app = Flask(__name__)
# Base directory
app.secret_key = 'your_secret_key_herefghjklgfhjklvhjbnk'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load modules and questions
with open(os.path.join(BASE_DIR, "static", "modules.json")) as f:
    modules = json.load(f)

with open(os.path.join(BASE_DIR, "static", "questions.json")) as f:
    questions = json.load(f)

def load_modules(language="english"):
    if language == "hindi":
        modules_file = "modules_hindi.json"
    elif language == "telugu":
        modules_file = "modules_telugu.json"
    else:
        modules_file = "modules.json"  # Default is English

    with open(os.path.join(BASE_DIR, "static", modules_file)) as f:
        return json.load(f)


@app.route("/email")
def enroll_page():
    raw_email = request.args.get("email")  # gets email from URL query string
    if not raw_email:
        return "Email not provided", 400

    email = raw_email.replace('%40', '@')  # decode %40 to @ manually
    username = email.split("@")[0]

    session['email'] = email
    session.setdefault('lang', 'english')  # Set default language once

    return render_template("enroll_page.html", username=username, default_lang=session['lang'])

@app.route("/enroll")
def index():
    module_index = int(request.args.get("module", 0))
    
    # Check if language is passed in URL
    if 'lang' in request.args:
        session['lang'] = request.args['lang']  # Store selected language in session
    
    language = session.get('lang', 'english')
    selected_modules = load_modules(language)
    selected_module = selected_modules[module_index]

    return render_template("index.html", modules=selected_modules, selected_module=selected_module)

@app.route("/quiz")
def quiz():
    return render_template("quiz.html", questions=questions)

@app.route("/submit-quiz", methods=["POST"])
def submit_quiz():
    score = 0
    total = len(questions)
    answers = [q['answer'] for q in questions]

    for i, correct in enumerate(answers):
        selected = request.form.get(f"q{i+1}")
        if selected == correct:
            score += 1

    passed = score >= total * 0.8  # 80% pass criteria
    name = session.get('email')

    return render_template("result.html", name=name, score=score, total=total, passed=passed)

@app.route("/certificate", methods=["GET", "POST"])
def certificate():
    name = session.get('email')  # Retrieve name from session
    date_str = datetime.today().strftime('%B %d, %Y')
    return render_template("certificate.html", name=name, date=date_str)

def create_certificate():
    # Path to your HTML file
    html_path = "templates/certificate.html"
    # Output PDF file path
    pdf_path = "certificate.pdf"

    # Convert HTML to PDF
    pdfkit.from_file(html_path, pdf_path)

    return pdf_path

@app.route("/download-certificate", methods=["POST"])
def download_certificate():
    pdf_path = create_certificate()
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name="certificate.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    app.run(debug=True, port=7000)