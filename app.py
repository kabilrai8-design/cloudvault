from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from models import db, User, File
from config import Config
import os, uuid

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# ─── Routes ───────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))
        
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials!', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    files = File.query.filter_by(user_id=current_user.id).order_by(File.uploaded_at.desc()).all()
    return render_template('dashboard.html', files=files)

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        flash('No file selected!', 'danger')
        return redirect(url_for('dashboard'))
    
    file = request.files['file']
    expiry_days = int(request.form.get('expiry_days', 7))

    if file and allowed_file(file.filename):
        original_name = file.filename
        filename = secure_filename(file.filename)
        unique_name = str(uuid.uuid4()) + '_' + filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(filepath)

        new_file = File(
            filename=unique_name,
            original_name=original_name,
            file_size=os.path.getsize(filepath),
            file_type=filename.rsplit('.', 1)[1].lower(),
            share_token=str(uuid.uuid4()),
            expiry_date=datetime.utcnow() + timedelta(days=expiry_days),
            user_id=current_user.id
        )
        db.session.add(new_file)
        db.session.commit()
        flash('File uploaded successfully!', 'success')
    else:
        flash('File type not allowed!', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/download/<int:file_id>')
@login_required
def download(file_id):
    file = File.query.get_or_404(file_id)
    file.download_count += 1
    db.session.commit()
    return send_from_directory(app.config['UPLOAD_FOLDER'], file.filename, as_attachment=True, download_name=file.original_name)

@app.route('/share/<token>')
def share(token):
    file = File.query.filter_by(share_token=token).first_or_404()
    if file.expiry_date and datetime.utcnow() > file.expiry_date:
        flash('This link has expired!', 'danger')
        return redirect(url_for('index'))
    file.download_count += 1
    db.session.commit()
    return send_from_directory(app.config['UPLOAD_FOLDER'], file.filename, as_attachment=True, download_name=file.original_name)

@app.route('/files')
@login_required
def files():
    all_files = File.query.filter_by(user_id=current_user.id).all()
    return render_template(
        'files.html',
        files=all_files,
        now=datetime.utcnow()
    )

@app.route('/delete/<int:file_id>')
@login_required
def delete(file_id):
    file = File.query.get_or_404(file_id)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    db.session.delete(file)
    db.session.commit()
    flash('File deleted!', 'success')
    return redirect(url_for('dashboard'))

# ─── Run ──────────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        os.makedirs('uploads', exist_ok=True)
        db.create_all()
    app.run(debug=True)