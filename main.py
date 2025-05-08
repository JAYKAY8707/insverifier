from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from datetime import timedelta, datetime

app = Flask(__name__)
app.secret_key = 'FMC8707$-secret-key-789'  # Required for sessions
app.permanent_session_lifetime = timedelta(seconds=60)  # Session timeout after 60 seconds
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medical.db'
db = SQLAlchemy(app)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class Insurance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class DoctorInsurance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    insurance_id = db.Column(db.Integer, db.ForeignKey('insurance.id'), nullable=False)
    doctor = db.relationship('Doctor', backref=db.backref('insurances', lazy=True))
    insurance = db.relationship('Insurance', backref=db.backref('doctors', lazy=True))

with app.app_context():
    db.create_all()

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated
insurances = []
relationships = []

html_template = """
<!doctype html>
<head>
  <title>First MedCare Insurance Verifier</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
  <style>
    .logo {
      height: 50px;
      vertical-align: middle;
      margin-right: 1rem;
    }
    .nav-logo {
      display: flex;
      align-items: center;
      gap: 2rem;
    }
    .nav-logo-img {
      height: 50px;
      width: auto;
    }
    .nav-links {
      display: flex;
      gap: 1.5rem;
    }
    .hero-logo {
      height: 120px;
      margin-bottom: 2rem;
    }
    body {
      font-family: 'Inter', sans-serif;
      margin: 0;
      padding: 0;
      background: #f8fafc;
      color: #1e293b;
    }
    nav {
      background: white;
      padding: 1rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    nav a {
      color: #1e293b;
      text-decoration: none;
      margin-right: 1.5rem;
      font-weight: 500;
    }
    nav a:hover {
      color: #3b82f6;
    }
    .hero {
      text-align: center;
      padding: 4rem 2rem;
      background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }
    .hero-logo {
      width: auto;
      height: 120px;
      margin-bottom: 2rem;
    }
    .hero h1 {
      font-size: 2.5rem;
      margin-bottom: 1rem;
      background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .hero h3 {
      color: #64748b;
      font-weight: 500;
      margin-bottom: 2rem;
    }
    .hero p {
      color: #475569;
      max-width: 600px;
      margin: 0 auto 2rem;
      line-height: 1.6;
    }
    .button-group {
      display: flex;
      gap: 1rem;
      justify-content: center;
    }
    .button {
      text-decoration: none;
      padding: 0.75rem 1.5rem;
      border-radius: 0.5rem;
      font-weight: 500;
      transition: all 0.2s;
    }
    .primary {
      background: #3b82f6;
      color: white;
    }
    .primary:hover {
      background: #2563eb;
    }
    .secondary {
      background: #64748b;
      color: white;
    }
    .secondary:hover {
      background: #475569;
    }
  </style>
</head>
<body>
  <nav>
    <div class="nav-logo">
      <img src="/static/FMC LOGO PNG GOOD.png" alt="First MedCare Logo" class="nav-logo-img">
      <div class="nav-links">
        <a href="/">Home</a>
        <a href="/query_page">Verify Insurance</a>
        <a href="/management">Management</a>
      </div>
    </div>
  </nav>
  <div class="hero">
    <img src="/static/FMC LOGO PNG GOOD.png" alt="First MedCare Logo" class="hero-logo">
    <h1>First MedCare Insurance Verifier</h1>
    <h3>Powered By Joseph</h3>
    <p>Streamline your insurance verification process with our easy-to-use platform. Check doctor-insurance compatibility instantly and manage your healthcare network efficiently.</p>
    <div class="button-group">
      <a href="/query_page" class="button primary">Verify Insurance</a>
      <a href="/management" class="button secondary">Management Portal</a>
    </div>
  </div>
</body>
"""

management_template = """
<!doctype html>
<head>
  <title>Management - First MedCare Insurance Verifier</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
  <style>
    .logo {
      height: 40px;
      vertical-align: middle;
    }
    .nav-logo {
      display: flex;
      align-items: center;
      gap: 2rem;
    }
    .nav-logo-img {
      height: 50px;
      width: auto;
    }
    .nav-links {
      display: flex;
      gap: 1.5rem;
    }
    body {
      font-family: 'Inter', sans-serif;
      margin: 0;
      padding: 0;
      background: #f8fafc;
      color: #1e293b;
    }
    nav {
      background: white;
      padding: 1rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    nav a {
      color: #1e293b;
      text-decoration: none;
      margin-right: 1.5rem;
      font-weight: 500;
    }
    nav a:hover {
      color: #3b82f6;
    }
    .container {
      max-width: 800px;
      margin: 2rem auto;
      padding: 2rem;
    }
    .card {
      background: white;
      border-radius: 0.5rem;
      padding: 1.5rem;
      margin-bottom: 1.5rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    h2 {
      color: #1e293b;
      margin-top: 0;
      margin-bottom: 1rem;
    }
    input[type="text"] {
      padding: 0.5rem;
      border: 1px solid #e2e8f0;
      border-radius: 0.375rem;
      margin-right: 1rem;
      min-width: 200px;
    }
    select {
      padding: 0.5rem;
      border: 1px solid #e2e8f0;
      border-radius: 0.375rem;
      margin-right: 1rem;
      min-width: 200px;
    }
    input[type="submit"] {
      background: #3b82f6;
      color: white;
      border: none;
      padding: 0.5rem 1rem;
      border-radius: 0.375rem;
      cursor: pointer;
      font-weight: 500;
    }
    input[type="submit"]:hover {
      background: #2563eb;
    }
    ul {
      list-style: none;
      padding: 0;
      margin: 1rem 0;
    }
    li {
      padding: 0.5rem 0;
      color: #475569;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .relationship-item {
      background: #f1f5f9;
      padding: 0.75rem;
      border-radius: 0.375rem;
      margin-bottom: 0.5rem;
    }
    .unlink-btn {
      background: #ef4444;
      color: white;
      border: none;
      padding: 0.25rem 0.75rem;
      border-radius: 0.25rem;
      cursor: pointer;
    }
    .unlink-btn:hover {
      background: #dc2626;
    }
  </style>
</head>
<body>
  <nav>
    <div class="nav-logo">
      <img src="/static/FMC LOGO PNG GOOD.png" alt="First MedCare Logo" class="nav-logo-img">
      <div class="nav-links">
        <a href="/">Home</a>
        <a href="/query_page">Verify Insurance</a>
        <a href="/management">Management</a>
      </div>
    </div>
  </nav>
  <div class="container">
    <div class="card">
      <h2>Add Doctor</h2>
<form method="post" action="/add_doctor">
  Name: <input type="text" name="doctor_name">
  <input type="submit" value="Add">
</form>

<h2>Add Insurance</h2>
<form method="post" action="/add_insurance">
  Name: <input type="text" name="insurance_name">
  <input type="submit" value="Add">
</form>

<h2>Link Doctor to Insurance</h2>
<form method="post" action="/link">
  Doctor:
  <select name="doctor">
    {% for doc in doctors %}
      <option>{{ doc }}</option>
    {% endfor %}
  </select>
  Insurance:
  <select name="insurance">
    {% for ins in insurances %}
      <option>{{ ins }}</option>
    {% endfor %}
  </select>
  <input type="submit" value="Link">
</form>

<h3>Doctors</h3>
<ul>{% for d in doctors %}<li>{{ d }}</li>{% endfor %}</ul>

<h3>Insurances</h3>
<ul>{% for i in insurances %}<li>{{ i }}</li>{% endfor %}</ul>

<h3>Relationships</h3>
<ul>
{% for doc, ins in relationships %}
  <li>
    {{ doc }} accepts {{ ins }}
    <form method="post" action="/unlink" style="display: inline;">
      <input type="hidden" name="doctor" value="{{ doc }}">
      <input type="hidden" name="insurance" value="{{ ins }}">
      <input type="submit" value="Unlink">
    </form>
  </li>
{% endfor %}
</ul>
"""

query_template = """
<!doctype html>
<head>
  <title>Insurance Verification - First MedCare</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
  <style>
    .logo {
      height: 40px;
      vertical-align: middle;
    }
    .nav-logo {
      display: flex;
      align-items: center;
      gap: 2rem;
    }
    .nav-logo-img {
      height: 50px;
      width: auto;
    }
    .nav-links {
      display: flex;
      gap: 1.5rem;
    }
    body {
      font-family: 'Inter', sans-serif;
      margin: 0;
      padding: 0;
      background: #f8fafc;
      color: #1e293b;
    }
    nav {
      background: white;
      padding: 1rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    nav a {
      color: #1e293b;
      text-decoration: none;
      margin-right: 1.5rem;
      font-weight: 500;
    }
    nav a:hover {
      color: #3b82f6;
    }
    .container {
      max-width: 800px;
      margin: 2rem auto;
      padding: 2rem;
      background: white;
      border-radius: 0.5rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    h2 {
      color: #1e293b;
      margin-bottom: 1.5rem;
    }
    form {
      margin-bottom: 2rem;
    }
    select {
      padding: 0.5rem;
      border: 1px solid #e2e8f0;
      border-radius: 0.375rem;
      margin-right: 1rem;
      min-width: 200px;
    }
    input[type="submit"] {
      background: #3b82f6;
      color: white;
      border: none;
      padding: 0.5rem 1rem;
      border-radius: 0.375rem;
      cursor: pointer;
      font-weight: 500;
    }
    input[type="submit"]:hover {
      background: #2563eb;
    }
    .results {
      background: #f1f5f9;
      padding: 1.5rem;
      border-radius: 0.375rem;
      margin-top: 2rem;
    }
    .results ul {
      list-style: none;
      padding: 0;
      margin: 0;
    }
    .results li {
      padding: 0.5rem 0;
      color: #475569;
    }
  </style>
</head>
<body>
  <nav>
    <div class="nav-logo">
      <img src="/static/FMC LOGO PNG GOOD.png" alt="First MedCare Logo" class="nav-logo-img">
      <div class="nav-links">
        <a href="/">Home</a>
        <a href="/query_page">Verify Insurance</a>
        <a href="/management">Management</a>
      </div>
    </div>
  </nav>
  <div class="container">
    <h2>Verify Insurance Compatibility</h2>
    <div class="search-container">
  <div class="search-box">
    <input type="text" id="doctorSearch" onkeyup="filterDoctors()" placeholder="Search for doctors...">
    <div id="doctorDropdown" class="dropdown-content">
      {% for doc in doctors %}
        <a href="/query_page?doctor_query={{ doc }}">{{ doc }}</a>
      {% endfor %}
    </div>
  </div>

  <div class="search-box">
    <input type="text" id="insuranceSearch" onkeyup="filterInsurances()" placeholder="Search for insurances...">
    <div id="insuranceDropdown" class="dropdown-content">
      {% for ins in insurances %}
        <a href="/query_page?insurance_query={{ ins }}">{{ ins }}</a>
      {% endfor %}
    </div>
  </div>
</div>

<script>
function filterDoctors() {
  var input = document.getElementById("doctorSearch");
  var filter = input.value.toUpperCase();
  var dropdown = document.getElementById("doctorDropdown");
  var links = dropdown.getElementsByTagName("a");

  for (var i = 0; i < links.length; i++) {
    var txtValue = links[i].textContent || links[i].innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      links[i].style.display = "";
    } else {
      links[i].style.display = "none";
    }
  }
  dropdown.style.display = filter ? "block" : "none";
}

function filterInsurances() {
  var input = document.getElementById("insuranceSearch");
  var filter = input.value.toUpperCase();
  var dropdown = document.getElementById("insuranceDropdown");
  var links = dropdown.getElementsByTagName("a");

  for (var i = 0; i < links.length; i++) {
    var txtValue = links[i].textContent || links[i].innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      links[i].style.display = "";
    } else {
      links[i].style.display = "none";
    }
  }
  dropdown.style.display = filter ? "block" : "none";
}
</script>

<style>
.search-container {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
}

.search-box {
  position: relative;
  flex: 1;
}

.search-box input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
}

.dropdown-content {
  display: none;
  position: absolute;
  background-color: #fff;
  min-width: 100%;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  border-radius: 0.375rem;
  max-height: 300px;
  overflow-y: auto;
  z-index: 1000;
}

.dropdown-content a {
  color: #1e293b;
  padding: 0.75rem;
  text-decoration: none;
  display: block;
}

.dropdown-content a:hover {
  background-color: #f1f5f9;
}
</style>

{% if query_result %}
<h3>Query Result</h3>
<ul>
  {% for item in query_result %}
    <li>{{ item }}</li>
  {% endfor %}
</ul>
{% endif %}
"""

@app.route("/")
def index():
    doctors = [d.name for d in Doctor.query.all()]
    insurances = [i.name for i in Insurance.query.all()]
    relationships = [(d.doctor.name, d.insurance.name) for d in DoctorInsurance.query.all()]
    return render_template_string(html_template, doctors=doctors, insurances=insurances, relationships=relationships)

@app.route("/add_doctor", methods=["POST"])
def add_doctor():
    name = request.form["doctor_name"]
    if name:
        doctor = Doctor(name=name)
        db.session.add(doctor)
        db.session.commit()
    return redirect(url_for("management"))

@app.route("/add_insurance", methods=["POST"])
def add_insurance():
    name = request.form["insurance_name"]
    if name:
        insurance = Insurance(name=name)
        db.session.add(insurance)
        db.session.commit()
    return redirect(url_for("management"))

@app.route("/link", methods=["POST"])
def link():
    doctor = Doctor.query.filter_by(name=request.form["doctor"]).first()
    insurance = Insurance.query.filter_by(name=request.form["insurance"]).first()
    if doctor and insurance:
        link = DoctorInsurance(doctor=doctor, insurance=insurance)
        db.session.add(link)
        db.session.commit()
    return redirect(url_for("management"))

@app.route("/unlink", methods=["POST"])
def unlink():
    doctor = Doctor.query.filter_by(name=request.form["doctor"]).first()
    insurance = Insurance.query.filter_by(name=request.form["insurance"]).first()
    if doctor and insurance:
        DoctorInsurance.query.filter_by(doctor=doctor, insurance=insurance).delete()
        db.session.commit()
    return redirect(url_for("management"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == "FMC8707$":
            session.permanent = True
            session['authenticated'] = True
            return redirect(url_for("management"))
        return "Invalid password", 401
    return '''
    <!doctype html>
    <head>
        <title>Login - First MedCare</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
        <style>
            .logo {
              height: 40px;
              vertical-align: middle;
            }
            .nav-logo {
              display: flex;
              align-items: center;
              gap: 2rem;
            }
            .nav-logo-img {
              height: 50px;
              width: auto;
            }
            .nav-links {
              display: flex;
              gap: 1.5rem;
            }
            body {
                font-family: 'Inter', sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: #f8fafc;
            }
            .login-container {
                background: white;
                padding: 2rem;
                border-radius: 0.5rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                width: 300px;
            }
            input {
                width: 100%;
                padding: 0.75rem;
                margin: 0.5rem 0;
                border: 1px solid #e2e8f0;
                border-radius: 0.375rem;
            }
            input[type="submit"] {
                background: #3b82f6;
                color: white;
                border: none;
                cursor: pointer;
                font-weight: 500;
            }
            input[type="submit"]:hover {
                background: #2563eb;
            }
            h2 {
                margin: 0 0 1rem 0;
                color: #1e293b;
                text-align: center;
            }
            .back-button {
                display: block;
                text-align: center;
                margin-top: 1rem;
                color: #3b82f6;
                text-decoration: none;
            }
            .back-button:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h2>Management Login</h2>
            <form method="post">
                <input type="password" name="password" placeholder="Enter password" required>
                <input type="submit" value="Login">
            </form>
            <a href="/" class="back-button">← Back to Home</a>
        </div>
    </body>
    '''

@app.route("/management")
@requires_auth
def management():
    doctors = [d.name for d in Doctor.query.all()]
    insurances = [i.name for i in Insurance.query.all()]
    relationships = [(d.doctor.name, d.insurance.name) for d in DoctorInsurance.query.all()]
    return render_template_string(management_template, doctors=doctors, insurances=insurances, relationships=relationships)

@app.route("/query_page")
def query_page():
    doctors = [d.name for d in Doctor.query.all()]
    insurances = [i.name for i in Insurance.query.all()]
    doctor_name = request.args.get("doctor_query", "")
    insurance_name = request.args.get("insurance_query", "")
    result = []

    if doctor_name:
        doctor = Doctor.query.filter_by(name=doctor_name).first()
        if doctor:
            relations = DoctorInsurance.query.filter_by(doctor=doctor).all()
            result = [f"Accepts: {r.insurance.name}" for r in relations]
    elif insurance_name:
        insurance = Insurance.query.filter_by(name=insurance_name).first()
        if insurance:
            relations = DoctorInsurance.query.filter_by(insurance=insurance).all()
            result = [f"Accepted by: {r.doctor.name}" for r in relations]

    return render_template_string(query_template, doctors=doctors, insurances=insurances, query_result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)