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

class Specialty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class DoctorSpecialty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    specialty_id = db.Column(db.Integer, db.ForeignKey('specialty.id'), nullable=False)
    doctor = db.relationship('Doctor', backref=db.backref('specialties', lazy=True))
    specialty = db.relationship('Specialty', backref=db.backref('doctors', lazy=True))

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
      text-align: center;
    }
    .card {
      background: white;
      border-radius: 0.5rem;
      padding: 2rem;
      margin-bottom: 2rem;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    form {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1rem;
      margin-bottom: 2rem;
    }
    .form-row {
      display: flex;
      gap: 2rem;
      margin-bottom: 2rem;
      justify-content: space-between;
      flex-wrap: wrap;
    }
    .form-column {
      flex: 1;
      min-width: 300px;
    }
    .form-group {
      display: flex;
      gap: 1rem;
      align-items: center;
      flex-wrap: nowrap;
      justify-content: flex-start;
      width: 100%;
    }
    .form-group input[type="text"] {
      flex: 1;
      min-width: 0;
    }
    .form-group input[type="submit"] {
      white-space: nowrap;
    }
    h2, h3 {
      color: #1e293b;
      margin-bottom: 1.5rem;
      text-align: center;
    }
    ul {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 0.75rem;
    }
    li {
      background: #f8fafc;
      padding: 0.75rem 1.5rem;
      border-radius: 0.5rem;
      width: 100%;
      max-width: 500px;
      box-sizing: border-box;
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
    input[type="submit"], button, .button, select, input[type="text"] {
      transition: all 0.2s ease-in-out;
      transform-origin: center;
    }

    input[type="submit"], button, .button {
      background: #3b82f6;
      color: white;
      border: none;
      padding: 0.5rem 1rem;
      border-radius: 0.375rem;
      cursor: pointer;
      font-weight: 500;
    }

    input[type="submit"]:hover, button:hover, .button:hover {
      background: #2563eb;
      transform: scale(1.05);
    }

    input[type="submit"]:active, button:active, .button:active {
      transform: scale(0.95);
    }

    select:hover, input[type="text"]:hover {
      transform: scale(1.02);
      border-color: #3b82f6;
    }

    select:focus, input[type="text"]:focus {
      transform: scale(1.02);
      border-color: #2563eb;
      outline: none;
      box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
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
      <div class="form-row">
        <div class="form-column">
          <h2>Add Doctor</h2>
          <form method="post" action="/add_doctor">
            <div class="form-group">
              <input type="text" name="doctor_name" placeholder="Enter doctor name">
              <input type="submit" value="Add Doctor">
            </div>
          </form>
        </div>
        <div class="form-column">
          <h2>Add Insurance</h2>
          <form method="post" action="/add_insurance">
            <div class="form-group">
              <input type="text" name="insurance_name" placeholder="Enter insurance name">
              <input type="submit" value="Add Insurance">
            </div>
          </form>
        </div>
        <div class="form-column">
          <h2>Add Specialty</h2>
          <form method="post" action="/add_specialty">
            <div class="form-group">
              <input type="text" name="specialty_name" placeholder="Enter specialty">
              <input type="submit" value="Add">
            </div>
          </form>
        </div>
      </div>

      <div class="form-column" style="width: 100%; text-align: center;">
        <h2>Link Doctor to Insurance</h2>
        <form method="post" action="/link" style="display: inline-block; text-align: center;">
          <div class="form-group" style="justify-content: center;">
            <select name="doctor">
              {% for doc in doctors %}
                <option>{{ doc }}</option>
              {% endfor %}
            </select>
            <select name="insurance">
              {% for ins in insurances %}
                <option>{{ ins }}</option>
              {% endfor %}
            </select>
            <input type="submit" value="Link">
          </div>
        </form>

        <h2 style="margin-top: 2rem;">Link Doctor to Specialty</h2>
        <form method="post" action="/link_specialty" style="display: inline-block; text-align: center;">
          <div class="form-group" style="justify-content: center;">
            <select name="doctor">
              {% for doc in doctors %}
                <option>{{ doc }}</option>
              {% endfor %}
            </select>
            <select name="specialty">
              {% for spec in specialties %}
                <option>{{ spec }}</option>
              {% endfor %}
            </select>
            <input type="submit" value="Link">
          </div>
        </form>
      </div>

<h3>Doctors</h3>
<ul>
{% for d in doctors %}
  <li>
    {{ d }}
    <form method="post" action="/delete_doctor" style="display: inline;">
      <input type="hidden" name="doctor_name" value="{{ d }}">
      <input type="submit" value="Delete" style="background: #ef4444;">
    </form>
  </li>
{% endfor %}
</ul>

<h3>Insurances</h3>
<ul>
{% for i in insurances %}
  <li>
    {{ i }}
    <form method="post" action="/delete_insurance" style="display: inline;">
      <input type="hidden" name="insurance_name" value="{{ i }}">
      <input type="submit" value="Delete" style="background: #ef4444;">
    </form>
  </li>
{% endfor %}
</ul>

<h3>Specialties</h3>
<ul>
{% for s in specialties %}
  <li>
    {{ s }}
    <form method="post" action="/delete_specialty" style="display: inline;">
      <input type="hidden" name="specialty_name" value="{{ s }}">
      <input type="submit" value="Delete" style="background: #ef4444;">
    </form>
  </li>
{% endfor %}
</ul>

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

<h3>Specialty Relationships</h3>
<ul>
{% for doc, spec in specialty_relationships %}
  <li>
    {{ doc }} has specialty {{ spec }}
    <form method="post" action="/unlink_specialty" style="display: inline;">
      <input type="hidden" name="doctor" value="{{ doc }}">
      <input type="hidden" name="specialty" value="{{ spec }}">
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
    input[type="submit"], button, .button, select, input[type="text"] {
      transition: all 0.2s ease-in-out;
      transform-origin: center;
    }

    input[type="submit"], button, .button {
      background: #3b82f6;
      color: white;
      border: none;
      padding: 0.5rem 1rem;
      border-radius: 0.375rem;
      cursor: pointer;
      font-weight: 500;
    }

    input[type="submit"]:hover, button:hover, .button:hover {
      background: #2563eb;
      transform: scale(1.05);
    }

    input[type="submit"]:active, button:active, .button:active {
      transform: scale(0.95);
    }

    select:hover, input[type="text"]:hover {
      transform: scale(1.02);
      border-color: #3b82f6;
    }

    select:focus, input[type="text"]:focus {
      transform: scale(1.02);
      border-color: #2563eb;
      outline: none;
      box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
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
    <h2 class="centered-title">Verify Insurance Compatibility</h2>
    <div class="search-container">
      <div class="button-container">
        <button onclick="showSearch('insurance')" class="search-button">Search by Insurance</button>
        <button onclick="showSearch('specialty')" class="search-button">Search by Specialty</button>
        <button onclick="showSearch('doctor')" class="search-button">Search by Doctor</button>
      </div>

      <div id="insuranceSearch" class="search-box" style="display: none;">
        <input type="text" onkeyup="filterItems('insurance')" placeholder="Search for insurance...">
        <div class="dropdown-content">
          {% for ins in insurances %}
            <a href="/query_page?insurance_query={{ ins }}">{{ ins }}</a>
          {% endfor %}
        </div>
      </div>

      <div id="specialtySearch" class="search-box" style="display: none;">
        <div class="specialty-grid">
          {% for spec in specialties %}
            <a href="/specialty/{{ spec }}" class="specialty-button">{{ spec }}</a>
          {% endfor %}
        </div>
      </div>

      <div id="doctorSearch" class="search-box" style="display: none;">
        <input type="text" onkeyup="filterItems('doctor')" placeholder="Search for doctor...">
        <div class="dropdown-content">
          {% for doc in doctors %}
            <a href="/query_page?doctor_query={{ doc }}">{{ doc }}</a>
          {% endfor %}
        </div>
      </div>
    </div>

    <script>
    function showSearch(type) {
      // Hide all search boxes
      document.querySelectorAll('.search-box').forEach(box => box.style.display = 'none');
      // Show selected search box
      document.getElementById(type + 'Search').style.display = 'block';
    }

    function filterItems(type) {
      var input = document.querySelector('#' + type + 'Search input');
      var filter = input.value.toUpperCase();
      var dropdown = document.querySelector('#' + type + 'Search .dropdown-content');
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

    function updateResults(type, value) {
      window.location.href = `/query_page?${type}_query=${encodeURIComponent(value)}`;
    }
    </script>

    <style>
    .centered-title {
      text-align: center;
      margin-bottom: 2rem;
    }

    .button-container {
      display: flex;
      gap: 1rem;
      margin-bottom: 2rem;
      justify-content: center;
      flex-wrap: wrap;
    }

    .search-button {
      padding: 0.75rem 1.5rem;
      background: #3b82f6;
      color: white;
      border: none;
      border-radius: 0.375rem;
      cursor: pointer;
      font-weight: 500;
      transition: background-color 0.2s;
      min-width: 200px;
    }

    .search-button:hover {
      background: #2563eb;
    }

    .search-box {
      max-width: 500px;
      margin: 0 auto;
    }

    .search-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      width: 100%;
    }
    </style>

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

.specialty-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  padding: 1rem;
}

.specialty-button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  color: #1e293b;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s;
}

.specialty-button:hover {
  transform: scale(1.05);
  background: #f8fafc;
  border-color: #3b82f6;
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

@app.route("/add_specialty", methods=["POST"])
def add_specialty():
    name = request.form["specialty_name"]
    if name:
        specialty = Specialty(name=name)
        db.session.add(specialty)
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

@app.route("/link_specialty", methods=["POST"])
def link_specialty():
    doctor = Doctor.query.filter_by(name=request.form["doctor"]).first()
    specialty = Specialty.query.filter_by(name=request.form["specialty"]).first()
    if doctor and specialty:
        link = DoctorSpecialty(doctor=doctor, specialty=specialty)
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

@app.route("/unlink_specialty", methods=["POST"])
def unlink_specialty():
    doctor = Doctor.query.filter_by(name=request.form["doctor"]).first()
    specialty = Specialty.query.filter_by(name=request.form["specialty"]).first()
    if doctor and specialty:
        DoctorSpecialty.query.filter_by(doctor=doctor, specialty=specialty).delete()
        db.session.commit()
    return redirect(url_for("management"))

@app.route("/delete_doctor", methods=["POST"])
def delete_doctor():
    name = request.form["doctor_name"]
    doctor = Doctor.query.filter_by(name=name).first()
    if doctor:
        DoctorInsurance.query.filter_by(doctor=doctor).delete()
        DoctorSpecialty.query.filter_by(doctor=doctor).delete()
        db.session.delete(doctor)
        db.session.commit()
    return redirect(url_for("management"))

@app.route("/delete_insurance", methods=["POST"])
def delete_insurance():
    name = request.form["insurance_name"]
    insurance = Insurance.query.filter_by(name=name).first()
    if insurance:
        DoctorInsurance.query.filter_by(insurance=insurance).delete()
        db.session.delete(insurance)
        db.session.commit()
    return redirect(url_for("management"))

@app.route("/delete_specialty", methods=["POST"])
def delete_specialty():
    name = request.form["specialty_name"]
    specialty = Specialty.query.filter_by(name=name).first()
    if specialty:
        DoctorSpecialty.query.filter_by(specialty=specialty).delete()
        db.session.delete(specialty)
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
                align-items: center                height: 100vh;
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
                margin: 0.5rem auto;
                border: 1px solid #e2e8f0;
                border-radius: 0.375rem;
                box-sizing: border-box;
                display: block;
            }
            input[type="submit"], button, .button, select, input[type="text"] {
                transition: all 0.2s ease-in-out;
                transform-origin: center;
            }

            input[type="submit"], button, .button {
                background: #3b82f6;
                color: white;
                border: none;
                cursor: pointer;
                font-weight: 500;
                padding: 0.5rem 1rem;
                border-radius: 0.375rem;
            }

            input[type="submit"]:hover, button:hover, .button:hover {
                background: #2563eb;
                transform: scale(1.05);
            }

            input[type="submit"]:active, button:active, .button:active {
                transform: scale(0.95);
            }

            select:hover, input[type="text"]:hover {
                transform: scale(1.02);
                border-color: #3b82f6;
            }

            select:focus, input[type="text"]:focus {
                transform: scale(1.02);
                border-color: #2563eb;
                outline: none;
                box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
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
    specialties = [s.name for s in Specialty.query.all()]
    relationships = [(d.doctor.name, d.insurance.name) for d in DoctorInsurance.query.all()]
    specialty_relationships = [(d.doctor.name, d.specialty.name) for d in DoctorSpecialty.query.all()]
    return render_template_string(management_template, doctors=doctors, insurances=insurances, specialties=specialties, relationships=relationships, specialty_relationships=specialty_relationships)

@app.route("/specialty/<specialty_name>")
def specialty_details(specialty_name):
    specialty = Specialty.query.filter_by(name=specialty_name).first()
    if specialty:
        doctors_with_specialty = DoctorSpecialty.query.filter_by(specialty=specialty).all()
        result = []
        for relation in doctors_with_specialty:
            doctor = relation.doctor
            insurances = [r.insurance.name for r in DoctorInsurance.query.filter_by(doctor=doctor).all()]
            result.append({
                'doctor': doctor.name,
                'insurances': insurances
            })
        return render_template_string("""
            <!doctype html>
            <head>
                <title>{{ specialty_name }} - Doctors</title>
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
                <style>
                    body { font-family: 'Inter', sans-serif; margin: 0; padding: 0; background: #f8fafc; }
                    .container { max-width: 800px; margin: 2rem auto; padding: 1rem; }
                    .doctor-card { background: white; padding: 1.5rem; margin-bottom: 1rem; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
                    .doctor-name { font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem; }
                    .insurance-list { color: #64748b; }
                    .back-link { display: inline-block; margin-bottom: 1rem; color: #3b82f6; text-decoration: none; }
                    .back-link:hover { text-decoration: underline; }
                </style>
            </head>
            <body>
                <div class="container">
                    <a href="/query_page" class="back-link">← Back to Search</a>
                    <h2>Doctors Specializing in {{ specialty_name }}</h2>
                    {% for item in result %}
                        <div class="doctor-card">
                            <div class="doctor-name">{{ item.doctor }}</div>
                            <div class="insurance-list">
                                Accepted Insurance: {{ ', '.join(item.insurances) if item.insurances else 'None' }}
                            </div>
                        </div>
                    {% endfor %}
                </div>
            </body>
        """, specialty_name=specialty_name, result=result)
    return redirect(url_for('query_page'))

@app.route("/query_page")
def query_page():
    doctors = [d.name for d in Doctor.query.all()]
    insurances = [i.name for i in Insurance.query.all()]
    specialties = [s.name for s in Specialty.query.all()]
    doctor_name = request.args.get("doctor_query", "")
    insurance_name = request.args.get("insurance_query", "")
    specialty_name = request.args.get("specialty_query", "")
    result = []

    if doctor_name:
        doctor = Doctor.query.filter_by(name=doctor_name).first()
        if doctor:
            insurance_relations = DoctorInsurance.query.filter_by(doctor=doctor).all()
            specialty_relations = DoctorSpecialty.query.filter_by(doctor=doctor).all()
            result = ([f"Specialty: {r.specialty.name}" for r in specialty_relations] + 
                     [f"Accepts: {r.insurance.name}" for r in insurance_relations])
    elif insurance_name:
        insurance = Insurance.query.filter_by(name=insurance_name).first()
        if insurance:
            relations = DoctorInsurance.query.filter_by(insurance=insurance).all()
            result = [f"Accepted by: {r.doctor.name}" for r in relations]
    elif specialty_name:
        specialty = Specialty.query.filter_by(name=specialty_name).first()
        if specialty:
            relations = DoctorSpecialty.query.filter_by(specialty=specialty).all()
            result = [f"Doctor with this specialty: {r.doctor.name}" for r in relations]

    return render_template_string(query_template, doctors=doctors, insurances=insurances, query_result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
