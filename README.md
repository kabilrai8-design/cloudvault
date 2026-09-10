# cloudvault
# CloudVault ☁️
**Secure Cloud Storage & Data Access Management System**

Built during Web Development Internship at DLK Software Solutions.

---

## About
CloudVault is a Flask-based web app where users can securely upload, store, and share files using time-limited links with download tracking.

---

## Features
- 🔐 User Registration & Login (hashed passwords)
- 📁 File Upload with type & size validation (max 16MB)
- 🔗 Unique shareable link generation (UUID-based)
- ⏳ File expiry — links auto-expire after set days
- 📊 Download count tracking
- 🗑️ File delete from server + database
- 📱 Responsive UI — mobile friendly

---

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Database | SQLite + SQLAlchemy |
| Auth | Flask-Login, Werkzeug |
| Frontend | HTML5, CSS3, Bootstrap 5 |
| Templating | Jinja2 |

---

## Setup & Run

```bash
# Install dependencies
pip install flask flask-sqlalchemy flask-login werkzeug

# Run the app
python app.py
