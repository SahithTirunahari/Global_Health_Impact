from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'dev-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'ppt', 'pptx', 'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Mock database
USERS = {
    'test@example.com': {
        'password': 'password123',
        'name': 'Test User',
    }
}

FILES = [
    {'id': 1, 'name': 'research_paper.pdf', 'size': '2.3 MB', 'user': 'test@example.com', 'date': '2024-01-15'},
    {'id': 2, 'name': 'data_analysis.csv', 'size': '1.1 MB', 'user': 'test@example.com', 'date': '2024-01-20'},
    {'id': 3, 'name': 'presentation.pptx', 'size': '5.2 MB', 'user': 'test@example.com', 'date': '2024-02-01'},
]

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = USERS.get(email)
        if user and user['password'] == password:
            session['email'] = email
            return redirect(url_for('dashboard'))
        
        return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

# BUG #1: No authentication check!
# Anyone can access dashboard without logging in
@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('login'))
        
    email = session.get('email')
    user = USERS.get(email)
    user_files = [f for f in FILES if f['user'] == email]
    
    return render_template('dashboard.html', 
                         user=user, 
                         files=user_files)

# BUG #2: N+1 query pattern
# In a real app with database, this would be very slow
@app.route('/api/files')
def get_files():
    if 'email' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    email = session['email']
    result = []
    current_user = USERS.get(email)
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
        
    user_files = [f for f in FILES if f['user'] == email]
    
    for file in user_files:
        result.append({
            'id': file['id'],
            'name': file['name'],
            'size': file['size'],
            'date': file['date'],
            'user_name': current_user['name']
        })
    
    return jsonify(result)

# BUG #3: No file type validation
# Only checks extension, not actual file content
@app.route('/upload', methods=['POST'])
def upload():
    if 'email' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        size_bytes = os.path.getsize(file_path)
        size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
        
        new_file = {
            'id': len(FILES) + 1,
            'name': filename,
            'size': size_str,
            'user': session['email'],
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        FILES.append(new_file)
        return redirect(url_for('dashboard'))
    
    return 'Invalid file type', 400

@app.route('/search')
def search():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    query = request.args.get('q', '').lower()
    email = session['email']
    
    user_files = [f for f in FILES if f['user'] == email]
    
    if query:
        filtered = [f for f in user_files if f['name'].lower().startswith(query)]
        return render_template('dashboard.html', 
                             user=USERS.get(email),
                             files=filtered,
                             search_query=query)
    
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
