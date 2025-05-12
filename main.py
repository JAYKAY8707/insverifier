from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from datetime import timedelta, datetime
from flask import jsonify

app = Flask(__name__)
app.secret_key = 'FMC8707$-secret-key-789'  # Required for sessions
app.permanent_session_lifetime = timedelta(seconds=60)  # Session timeout after 60 seconds
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medical.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
        <h2>Mass Link Doctors to Insurance</h2>
        <form method="post" action="/mass_link" style="display: inline-block; text-align: center;">
          <div class="form-group" style="flex-direction: column; align-items: flex-start;">
            <div style="margin-bottom: 1rem;">
              <input type="text" name="insurance_name" placeholder="Enter new insurance name" style="width: 300px;">
            </div>
            <div style="margin-bottom: 1rem;">
              <h4 style="margin-bottom: 0.5rem;">Select Doctors:</h4>
              <div style="max-height: 300px; overflow-y: auto; border: 1px solid #e2e8f0; padding: 1rem; border-radius: 0.5rem; width: 500px;">
                {% for doc in doctors %}
                  <div style="margin-bottom: 0.5rem; display: flex; align-items: center;">
                    <input type="checkbox" name="selected_doctors" value="{{ doc }}" id="doc_{{ loop.index }}" style="margin-right: 10px; width: 20px; height: 20px;">
                    <label for="doc_{{ loop.index }}" style="font-size: 1.1rem;">{{ doc }}</label>
                  </div>
                {% endfor %}
              </div>
            </div>
            <input type="submit" value="Link Selected Doctors" style="margin-top: 1rem;">
          </div>
        </form>

        <h2 style="margin-top: 2rem;">Link Doctor to Insurance</h2>
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

specialties_template = """
<!doctype html>
<head>
    <title>Our Specialties - First MedCare</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            margin: 0;
            padding: 0;
            background: #f8fafc;
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
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 1rem;
        }
        .specialty-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 1rem;
            padding: 1rem;
        }
        .specialty-button {
            background: white;
            border: 1px solid #e2e8f0;
            padding: 1.5rem;
            border-radius: 0.5rem;
            cursor: pointer;
            font-size: 1.1rem;
            transition: all 0.2s;
            text-align: center;
        }
        .specialty-button:hover {
            transform: scale(1.02);
            border-color: #3b82f6;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .modal {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 2rem;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            max-width: 500px;
            width: 90%;
            z-index: 1000;
        }
        .modal-backdrop {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 999;
        }
        .close-modal {
            position: absolute;
            top: 1rem;
            right: 1rem;
            border: none;
            background: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #64748b;
        }
        .doctor-info {
            margin-top: 1rem;
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
        <h2>Our Specialties</h2>
        <div class="specialty-grid">
            {% for specialty in specialties %}
                <button class="specialty-button" onclick="showSpecialtyDetails('{{ specialty }}')">
                    {{ specialty }}
                </button>
            {% endfor %}
        </div>
    </div>

    <div class="modal-backdrop" onclick="closeModal()"></div>
    <div class="modal">
        <button class="close-modal" onclick="closeModal()">&times;</button>
        <h3 id="modal-title"></h3>
        <div id="modal-content" class="doctor-info"></div>
    </div>

    <script>
        function showSpecialtyDetails(specialty) {
            fetch(`/specialty/${specialty}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('modal-title').textContent = specialty;
                    let content = '';
                    data.forEach(item => {
                        content += `<div class="doctor-info">
                            <strong>Dr. ${item.doctor}</strong><br>
                            Accepts: ${item.insurances.length ? item.insurances.join(', ') : 'No insurances listed'}
                        </div>`;
                    });
                    document.getElementById('modal-content').innerHTML = content;
                    document.querySelector('.modal').style.display = 'block';
                    document.querySelector('.modal-backdrop').style.display = 'block';
                });
        }

        function closeModal() {
            document.querySelector('.modal').style.display = 'none';
            document.querySelector('.modal-backdrop').style.display = 'none';
        }
    </script>
</body>
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
        <button onclick="showSearch('doctor')" class="search-button">Search by Doctor</button>
        <button onclick="showSearch('specialty')" class="search-button">Search by Specialty</button>
      </div>

      <div id="insuranceSearch" class="search-box" style="display: none;">
        <input type="text" onkeyup="filterItems('insurance')" placeholder="Search for insurance...">
        <div class="dropdown-content">
          {% for ins in insurances %}
            <a href="/query_page?insurance_query={{ ins }}">{{ ins }}</a>
          {% endfor %}
        </div>
      </div>

      <div id="specialtySearch" class="search-box specialty-container" style="display: none;">
        <div class="specialty-grid">
          {% for spec in specialties %}
            <button class="specialty-button" onclick="showResults('{{ spec }}')">{{ spec }}</button>
          {% endfor %}
        </div>
      </div>

      <style>
        .specialty-container {
          width: 100%;
          max-width: 800px;
          margin: 0 auto;
        }
        .specialty-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 1rem;
          padding: 1rem;
          width: 100%;
        }
        .specialty-button {
          background: #3b82f6;
          color: white;
          padding: 1rem;
          border: none;
          border-radius: 0.5rem;
          cursor: pointer;
          font-size: 1rem;
          transition: all 0.2s;
          width: 100%;
          text-align: center;
        }
        .specialty-button:hover {
          background: #2563eb;
          transform: scale(1.05);
        }
      </style>

      <div id="doctorSearch" class="search-box" style="display: none;">
          <div class="specialty-grid">
            {% for doc in doctors %}
              <button class="specialty-button" onclick="showDoctorResults('{{ doc }}')">{{ doc }}</button>
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

    function showResults(specialty) {
      window.location.href = `/query_page?specialty_query=${encodeURIComponent(specialty)}`;
    }

    function showDoctorResults(doctor) {
      window.location.href = `/query_page?doctor_query=${encodeURIComponent(doctor)}`;
    }
    </script>

    <style>
    .centered-title {
      text-align: center;      margin-bottom: 2rem;
    }

    .button-container {
      display: flex;
      justify-content: center;
      gap: 1rem;
      margin-bottom: 2rem;
    }

    .search-button {
      padding: 0.75rem 1.5rem;
      font-size: 1rem;
    }

    .search-box {
      position: relative;
      margin-top: 1rem;
    }

    .search-box input {
      width: 100%;
      padding: 0.75rem;
      border: 1px solid #e2e8f0;
      border-radius: 0.375rem;
      margin-bottom: 0.5rem;
    }

    .dropdown-content {
      display: none;
      position: absolute;
      background: white;
      width: 100%;
      max-height: 300px;
      overflow-y: auto;
      border: 1px solid #e2e8f0;
      border-radius: 0.375rem;
      z-index: 1000;
    }

    .dropdown-content a {
      color: #1e293b;
      padding: 0.75rem;
      text-decoration: none;
      display: block;
    }

    .dropdown-content a:hover {
      background: #f1f5f9;
    }
    </style>

    {% if insurance_query or doctor_query or specialty_query %}
      <div class="results">
        <h3>Search Results:</h3>
        <ul>
          {% for doc in matching_doctors %}
            <li class="doctor-result">
              <h4>{{ doc.name }}</h4>
              <p><strong>Specialties:</strong> {{ doc.specialties }}</p>
              {% if doc.insurances and not insurance_query %}
              <p><strong>Accepted Insurances:</strong> {{ doc.insurances }}</p>
              {% endif %}
            </li>
          {% endfor %}
        </ul>
      </div>

      <style>
        .doctor-result {
          background: white;
          padding: 1rem;
          margin-bottom: 1rem;
          border-radius: 0.5rem;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .doctor-result h4 {
          margin: 0 0 0.5rem 0;
          color: #1e293b;
        }
        .doctor-result p {
          margin: 0.25rem 0;
          color: #4b5563;
        }
      </style>
    {% endif %}
  </div>
</body>
"""

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['authenticated'] = request.form['password'] == 'FMC8707$'
        if session['authenticated']:
            session.permanent = True  # Make the session permanent
            return redirect(url_for('management'))
        else:
            return render_template_string('<p>Incorrect password</p><a href="{{ url_for("login") }}">Try again</a>')
    return render_template_string("""
<head>
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f8fafc;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        form {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            width: 300px;
            margin-bottom: 1rem;
        }
        input {
            margin: 10px 0;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background-color: #3b82f6;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        button:hover {
            background-color: #2563eb;
        }
    </style>
</head>
<form method="post">
    <input type="password" name="password" placeholder="Password">
    <button type="submit">Login</button>
</form>
<a href="/" style="text-decoration: none;">
    <button style="background-color: #64748b; padding: 10px 15px; border: none; border-radius: 4px; color: white; cursor: pointer; transition: background-color 0.2s;">
        Back to Home
    </button>
</a>
""")

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('index'))

@app.route('/management', methods=['GET', 'POST'])
@requires_auth
def management():
    global insurances, relationships
    doctors = [d.name for d in Doctor.query.all()]
    insurances = [i.name for i in Insurance.query.all()]
    specialties = [s.name for s in Specialty.query.all()]
    relationships = [(d.doctor.name, d.insurance.name) for d in DoctorInsurance.query.all()]
    specialty_relationships = [(ds.doctor.name, ds.specialty.name) for ds in DoctorSpecialty.query.all()]

    return render_template_string(management_template, doctors=doctors, insurances=insurances, relationships=relationships, specialties=specialties, specialty_relationships=specialty_relationships)

@app.route('/add_doctor', methods=['POST'])
@requires_auth
def add_doctor():
    doctor_name = request.form['doctor_name']
    new_doctor = Doctor(name=doctor_name)
    db.session.add(new_doctor)
    db.session.commit()
    return redirect(url_for('management'))

@app.route('/add_insurance', methods=['POST'])
@requires_auth
def add_insurance():
    insurance_name = request.form['insurance_name']
    new_insurance = Insurance(name=insurance_name)
    db.session.add(new_insurance)
    db.session.commit()
    return redirect(url_for('management'))

@app.route('/add_specialty', methods=['POST'])
@requires_auth
def add_specialty():
    try:
        specialty_name = request.form['specialty_name']
        if specialty_name:
            new_specialty = Specialty(name=specialty_name)
            db.session.add(new_specialty)
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error adding specialty: {e}")
    return redirect(url_for('management'))

@app.route('/delete_doctor', methods=['POST'])
@requires_auth
def delete_doctor():
    doctor_name = request.form['doctor_name']
    doctor_to_delete = Doctor.query.filter_by(name=doctor_name).first()
    if doctor_to_delete:
        # Delete all doctor-insurance relationships
        DoctorInsurance.query.filter_by(doctor_id=doctor_to_delete.id).delete()
        # Delete all doctor-specialty relationships
        DoctorSpecialty.query.filter_by(doctor_id=doctor_to_delete.id).delete()
        # Delete the doctor
        db.session.delete(doctor_to_delete)
        db.session.commit()
    return redirect(url_for('management'))

@app.route('/delete_insurance', methods=['POST'])
@requires_auth
def delete_insurance():
    insurance_name = request.form['insurance_name']
    insurance_to_delete = Insurance.query.filter_by(name=insurance_name).first()
    if insurance_to_delete:
        # Delete all doctor-insurance relationships
        DoctorInsurance.query.filter_by(insurance_id=insurance_to_delete.id).delete()
        # Delete the insurance
        db.session.delete(insurance_to_delete)
        db.session.commit()
    return redirect(url_for('management'))

@app.route('/delete_specialty', methods=['POST'])
@requires_auth
def delete_specialty():
    specialty_name = request.form['specialty_name']
    specialty_to_delete = Specialty.query.filter_by(name=specialty_name).first()
    if specialty_to_delete:
        # Delete all doctor-specialty relationships
        DoctorSpecialty.query.filter_by(specialty_id=specialty_to_delete.id).delete()
        # Delete the specialty
        db.session.delete(specialty_to_delete)
        db.session.commit()
    return redirect(url_for('management'))

@app.route('/mass_link', methods=['POST'])
@requires_auth
def mass_link():
    insurance_name = request.form['insurance_name']
    selected_doctors = request.form.getlist('selected_doctors')

    # Check if insurance exists, create if it doesn't
    insurance = Insurance.query.filter_by(name=insurance_name).first()
    if not insurance:
        insurance = Insurance(name=insurance_name)
        db.session.add(insurance)
        db.session.flush()

    # Link selected doctors
    for doctor_name in selected_doctors:
        doctor = Doctor.query.filter_by(name=doctor_name).first()
        if doctor:
            # Check if relationship already exists
            existing = DoctorInsurance.query.filter_by(
                doctor_id=doctor.id, 
                insurance_id=insurance.id
            ).first()
            if not existing:
                new_relationship = DoctorInsurance(
                    doctor_id=doctor.id, 
                    insurance_id=insurance.id
                )
                db.session.add(new_relationship)

    db.session.commit()
    return redirect(url_for('management'))

@app.route('/link', methods=['POST'])
@requires_auth
def link():
    doctor_name = request.form['doctor']
    insurance_name = request.form['insurance']

    doctor = Doctor.query.filter_by(name=doctor_name).first()
    insurance = Insurance.query.filter_by(name=insurance_name).first()

    if doctor and insurance:
        new_relationship = DoctorInsurance(doctor_id=doctor.id, insurance_id=insurance.id)
        db.session.add(new_relationship)
        db.session.commit()
    return redirect(url_for('management'))

@app.route('/unlink', methods=['POST'])
@requires_auth
def unlink():
    doctor_name = request.form['doctor']
    insurance_name = request.form['insurance']

    doctor = Doctor.query.filter_by(name=doctor_name).first()
    insurance = Insurance.query.filter_by(name=insurance_name).first()

    if doctor and insurance:
        relationship_to_delete = DoctorInsurance.query.filter_by(doctor_id=doctor.id, insurance_id=insurance.id).first()
        if relationship_to_delete:
            db.session.delete(relationship_to_delete)
            db.session.commit()
    return redirect(url_for('management'))

@app.route('/link_specialty', methods=['POST'])
@requires_auth
def link_specialty():
    doctor_name = request.form['doctor']
    specialty_name = request.form['specialty']

    doctor = Doctor.query.filter_by(name=doctor_name).first()
    specialty = Specialty.query.filter_by(name=specialty_name).first()

    if doctor and specialty:
        new_specialty_relationship = DoctorSpecialty(doctor_id=doctor.id, specialty_id=specialty.id)
        db.session.add(new_specialty_relationship)
        db.session.commit()
    return redirect(url_for('management'))

@app.route('/unlink_specialty', methods=['POST'])
@requires_auth
def unlink_specialty():
    doctor_name = request.form['doctor']
    specialty_name = request.form['specialty']

    doctor = Doctor.query.filter_by(name=doctor_name).first()
    specialty = Specialty.query.filter_by(name=specialty_name).first()

    if doctor and specialty:
        relationship_to_delete = DoctorSpecialty.query.filter_by(doctor_id=doctor.id, specialty_id=specialty.id).first()
        if relationship_to_delete:
            db.session.delete(relationship_to_delete)
            db.session.commit()
    return redirect(url_for('management'))

@app.route('/specialties')
def specialties_page():
    specialties = [s.name for s in Specialty.query.all()]
    return render_template_string(specialties_template, specialties=specialties)

@app.route('/specialty/<specialty>')
def specialty(specialty):
    doctors = []
    specialty_obj = Specialty.query.filter_by(name=specialty).first()
    if specialty_obj:
        for ds in specialty_obj.doctors:
            doctor_name = ds.doctor.name
            insurances = [di.insurance.name for di in ds.doctor.insurances]
            doctors.append({'doctor': doctor_name, 'insurances': insurances})
    return jsonify(doctors)

@app.route('/standalone_verify')
def standalone_verify():
    insurance_query = request.args.get('insurance_query')
    doctor_query = request.args.get('doctor_query')
    specialty_query = request.args.get('specialty_query')

    doctors = [d.name for d in Doctor.query.all()]
    insurances = [i.name for i in Insurance.query.all()]
    specialties = [s.name for s in Specialty.query.all()]

    matching_doctors = []
    matching_insurance = []

    def get_doctor_details(doctor, search_type='all'):
        specialties = [ds.specialty.name for ds in doctor.specialties]
        insurances = [di.insurance.name for di in doctor.insurances] if search_type != 'insurance' else []
        return {
            'name': doctor.name,
            'specialties': ', '.join(specialties) if specialties else 'No specialties listed',
            'insurances': ', '.join(insurances) if insurances else 'No insurances listed'
        }

    def get_doctor_details(doctor, search_type='all'):
        specialties = [ds.specialty.name for ds in doctor.specialties]
        insurances = [di.insurance.name for di in doctor.insurances] if search_type != 'insurance' else []
        return {
            'name': doctor.name,
            'specialties': ', '.join(specialties) if specialties else 'No specialties listed',
            'insurances': ', '.join(insurances) if insurances else 'No insurances listed'
        }

    if insurance_query:
        insurance = Insurance.query.filter_by(name=insurance_query).first()
        if insurance:
            for doctor_rel in insurance.doctors:
                matching_doctors.append(get_doctor_details(doctor_rel.doctor, search_type='insurance'))

    if doctor_query:
        doctor = Doctor.query.filter_by(name=doctor_query).first()
        if doctor:
            matching_doctors = [get_doctor_details(doctor, search_type='doctor')]

    if specialty_query:
        specialty = Specialty.query.filter_by(name=specialty_query).first()
        if specialty:
            for doctor_specialty in specialty.doctors:
                matching_doctors.append(get_doctor_details(doctor_specialty.doctor, search_type='specialty'))

    return render_template_string("""
<!doctype html>
<head>
  <title>Insurance Verification - First MedCare</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
  <style>
    body {
      font-family: 'Inter', sans-serif;
      margin: 0;
      padding: 0;
      background: #f8fafc;
      color: #1e293b;
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
      text-align: center;
    }
    .search-container {
      margin-top: 2rem;
    }
    .button-container {
      display: flex;
      justify-content: center;
      gap: 1rem;
      margin-bottom: 2rem;
    }
    .search-button {
      background: #3b82f6;
      color: white;
      border: none;
      padding: 0.75rem 1.5rem;
      border-radius: 0.5rem;
      cursor: pointer;
      font-size: 1rem;
      transition: all 0.2s;
    }
    .search-button:hover {
      background: #2563eb;
      transform: scale(1.05);
    }
    .search-box {
      position: relative;
      margin-top: 1rem;
    }
    .search-box input {
      width: 100%;
      padding: 0.75rem;
      border: 1px solid #e2e8f0;
      border-radius: 0.375rem;
      margin-bottom: 0.5rem;
    }
    .dropdown-content {
      display: none;
      position: absolute;
      background: white;
      width: 100%;
      max-height: 300px;
      overflow-y: auto;
      border: 1px solid #e2e8f0;
      border-radius: 0.375rem;
      z-index: 1000;
    }
    .dropdown-content a {
      color: #1e293b;
      padding: 0.75rem;
      text-decoration: none;
      display: block;
    }
    .dropdown-content a:hover {
      background: #f1f5f9;
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
    .specialty-container {
      width: 100%;
      max-width: 800px;
      margin: 0 auto;
    }
    .specialty-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 1rem;
      padding: 1rem;
      width: 100%;
    }
    .specialty-button {
      background: #3b82f6;
      color: white;
      padding: 1rem;
      border: none;
      border-radius: 0.5rem;
      cursor: pointer;
      font-size: 1rem;
      transition: all 0.2s;
      width: 100%;
      text-align: center;
    }
    .specialty-button:hover {
      background: #2563eb;
      transform: scale(1.05);
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Insurance Verification</h2>
    <div class="search-container">
      <div class="button-container">
        <button onclick="showSearch('insurance')" class="search-button">Search by Insurance</button>
        <button onclick="showSearch('doctor')" class="search-button">Search by Doctor</button>
        <button onclick="showSearch('specialty')" class="search-button">Search by Specialty</button>
      </div>

      <div id="insuranceSearch" class="search-box" style="display: none;">
        <input type="text" onkeyup="filterItems('insurance')" placeholder="Search for insurance...">
        <div class="dropdown-content">
          {% for ins in insurances %}
            <a href="/standalone_verify?insurance_query={{ ins }}">{{ ins }}</a>
          {% endfor %}
        </div>
      </div>

      <div id="doctorSearch" class="search-box" style="display: none;">
          <div class="specialty-grid">
            {% for doc in doctors %}
              <button class="specialty-button" onclick="showDoctorResults('{{ doc }}')">{{ doc }}</button>
            {% endfor %}
          </div>
      </div>

      <div id="specialtySearch" class="search-box specialty-container" style="display: none;">
        <div class="specialty-grid">
          {% for spec in specialties %}
            <button class="specialty-button" onclick="showResults('{{ spec }}')">{{ spec }}</button>
          {% endfor %}
        </div>
      </div>
    </div>

    {% if insurance_query or doctor_query or specialty_query %}
      <div class="results">
        <h3>Search Results:</h3>
        <ul>
          {% for doc in matching_doctors %}
            <li class="doctor-result">
              <h4>{{ doc.name }}</h4>
              <p><strong>Specialties:</strong> {{ doc.specialties }}</p>
              {% if doc.insurances and not insurance_query %}
              <p><strong>Accepted Insurances:</strong> {{ doc.insurances }}</p>
              {% endif %}
            </li>
          {% endfor %}
        </ul>
      </div>

      <style>
        .doctor-result {
          background: white;
          padding: 1rem;
          margin-bottom: 1rem;
          border-radius: 0.5rem;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .doctor-result h4 {
          margin: 0 0 0.5rem 0;
          color: #1e293b;
        }
        .doctor-result p {
          margin: 0.25rem 0;
          color: #4b5563;
        }
      </style>
    {% endif %}
  </div>

  <script>
    function showSearch(type) {
      document.querySelectorAll('.search-box').forEach(box => box.style.display = 'none');
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

    function showResults(specialty) {
      window.location.href = `/standalone_verify?specialty_query=${encodeURIComponent(specialty)}`;
    }

    function showDoctorResults(doctor) {
      window.location.href = `/standalone_verify?doctor_query=${encodeURIComponent(doctor)}`;
    }
  </script>
</body>
    """,
    doctors=doctors,
    insurances=insurances,
    specialties=specialties,
    insurance_query=insurance_query,
    doctor_query=doctor_query,
    specialty_query=specialty_query,
    matching_doctors=matching_doctors,
    matching_insurance=matching_insurance)

@app.route('/query_page')
def query_page():
    insurance_query = request.args.get('insurance_query')
    doctor_query = request.args.get('doctor_query')
    specialty_query = request.args.get('specialty_query')

    doctors = [d.name for d in Doctor.query.all()]
    insurances = [i.name for i in Insurance.query.all()]
    specialties = [s.name for s in Specialty.query.all()]

    matching_doctors = []
    matching_insurance = []

    def get_doctor_details(doctor, search_type='all'):
        specialties = [ds.specialty.name for ds in doctor.specialties]
        insurances = [di.insurance.name for di in doctor.insurances] if search_type != 'insurance' else []
        return {
            'name': doctor.name,
            'specialties': ', '.join(specialties) if specialties else 'No specialties listed',
            'insurances': ', '.join(insurances) if insurances else 'No insurances listed'
        }

    if insurance_query:
        insurance = Insurance.query.filter_by(name=insurance_query).first()
        if insurance:
            for doctor_rel in insurance.doctors:
                matching_doctors.append(get_doctor_details(doctor_rel.doctor, search_type='insurance'))

    if doctor_query:
        doctor = Doctor.query.filter_by(name=doctor_query).first()
        if doctor:
            matching_doctors = [get_doctor_details(doctor, search_type='doctor')]

    if specialty_query:
        specialty = Specialty.query.filter_by(name=specialty_query).first()
        if specialty:
            for doctor_specialty in specialty.doctors:
                matching_doctors.append(get_doctor_details(doctor_specialty.doctor, search_type='specialty'))

    return render_template_string(query_template,
                               doctors=doctors,
                               insurances=insurances,
                               specialties=specialties,
                               insurance_query=insurance_query,
                               doctor_query=doctor_query,
                               specialty_query=specialty_query,
                               matching_doctors=matching_doctors,
                               matching_insurance=matching_insurance)

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
