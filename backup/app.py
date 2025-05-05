from flask import Flask, request, jsonify, send_from_directory, render_template_string, session
import numpy as np
import cv2
import base64
import os
from face_utils import save_face_image, recognize_faces_and_liveness_sequence, mark_attendance, get_attendance_status, mark_attendance_status, save_user_data, fetch_all_users, fetch_user_by_name, delete_user
from datetime import datetime
import csv

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key_here'  # Change this in production

ADMIN_PASSWORD = 'abhay123'  # Change this in production

def is_admin():
    return session.get('is_admin', False)

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_admin():
            return jsonify({'success': False, 'error': 'Admin login required'}), 401
        return f(*args, **kwargs)
    return decorated

# Serve index.html at root
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# Serve static files (style.css, script.js)
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

def read_image_from_request(img_data_b64):
    img_bytes = base64.b64decode(img_data_b64)
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    rollno = data.get('rollno')
    img_b64 = data.get('image')
    if not name or not email or not rollno or not img_b64:
        return jsonify({'success': False, 'error': 'Missing name, email, rollno, or image'}), 400
    img = read_image_from_request(img_b64)
    save_face_image(name, img)
    save_user_data(name, email, rollno)
    return jsonify({'success': True, 'message': f'{name} registered with email {email} and rollno {rollno}'})

@app.route('/attendance', methods=['POST'])
def attendance():
    data = request.json
    images_b64 = data.get('images')
    if not images_b64 or not isinstance(images_b64, list):
        return jsonify({'success': False, 'error': 'Missing images'}), 400
    imgs = [read_image_from_request(b64) for b64 in images_b64]
    results = recognize_faces_and_liveness_sequence(imgs)
    marked = []
    for res in results:
        if res['name'] and res['liveness']:
            mark_attendance(res['name'])
            marked.append(res['name'])
    return jsonify({'success': True, 'names': marked, 'details': results})

@app.route('/attendance_log', methods=['GET'])
def attendance_log():
    # Return attendance log as JSON (support new format)3
    records = []
    if os.path.exists('attendance.csv'):
        with open('attendance.csv', 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) >= 4:
                    records.append({'name': parts[0], 'date': parts[1], 'time': parts[2], 'status': parts[3]})
    return jsonify({'records': records})

@app.route('/attendance_status', methods=['GET'])
def attendance_status():
    # ?date=YYYY-MM-DD
    date = request.args.get('date')
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    status = get_attendance_status(date)
    return jsonify({'date': date, 'status': status})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    password = data.get('password')
    if password == ADMIN_PASSWORD:
        session['is_admin'] = True
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Invalid password'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('is_admin', None)
    return jsonify({'success': True})

@app.route('/is_admin', methods=['GET'])
def is_admin_route():
    return jsonify({'is_admin': is_admin()})

@app.route('/manual_attendance', methods=['POST'])
@admin_required
def manual_attendance():
    data = request.json
    name = data.get('name')
    date = data.get('date')
    status = data.get('status')  # 'present' or 'absent'
    if not name or not date or status not in ['present', 'absent']:
        return jsonify({'success': False, 'error': 'Missing or invalid parameters'}), 400
    mark_attendance_status(name, date, status)
    return jsonify({'success': True, 'message': f'{name} marked {status} for {date}'})

@app.route('/users', methods=['GET'])
def users():
    # List registered users (names, emails, roll numbers, and image filenames)
    users = []
    for user in fetch_all_users():
        name, email, rollno = user
        image_filename = f"{name}.jpg" if os.path.exists(os.path.join('registered_faces', f"{name}.jpg")) else None
        users.append({'name': name, 'email': email, 'rollno': rollno, 'image': image_filename})
    return jsonify({'users': users})

@app.route('/user/<name>', methods=['DELETE'])
def delete_user_route(name):
    # Delete a registered user (remove their image)
    img_path = os.path.join('registered_faces', f'{name}.jpg')
    if os.path.exists(img_path):
        os.remove(img_path)
    delete_user(name)
    return jsonify({'success': True, 'message': f'{name} deleted'})

@app.route('/download_attendance', methods=['GET'])
@admin_required
def download_attendance():
    date = request.args.get('date')
    if not os.path.exists('attendance.csv'):
        return jsonify({'success': False, 'error': 'Attendance log not found'}), 404

    temp_path = 'attendance_with_headers.csv'
    with open('attendance.csv', 'r') as f:
        lines = f.readlines()

    with open(temp_path, 'w') as f:
        f.write('Name,Email,Roll Number,Date,Time,Status\n')  # Add column headers
        if date:
            filtered = [line for line in lines if len(line.split(',')) >= 4 and line.split(',')[3] == date]
            f.writelines(filtered)
        else:
            f.writelines(lines)

    resp = send_from_directory('.', temp_path, as_attachment=True)
    import threading
    threading.Timer(2.0, lambda: os.remove(temp_path)).start()  # Clean up temp file
    return resp

@app.route('/attendance_analytics', methods=['GET'])
def attendance_analytics():
    date = request.args.get('date')
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    status = get_attendance_status(date)
    total = len(status)
    present = sum(1 for v in status.values() if v == 'present')
    absent = total - present
    percent = (present / total * 100) if total > 0 else 0
    return jsonify({
        'date': date,
        'total': total,
        'present': present,
        'absent': absent,
        'percent': round(percent, 2),
        'status': status
    })

@app.route('/edit_user', methods=['POST'])
def edit_user():
    data = request.json
    name = data.get('name')
    new_email = data.get('email')
    new_rollno = data.get('rollno')

    if not name or not new_email or not new_rollno:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400

    updated = False
    user_data_file = 'user_data.csv'
    temp_file = 'user_data_temp.csv'

    with open(user_data_file, 'r') as infile, open(temp_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        for row in reader:
            if row[0] == name:
                writer.writerow([name, new_email, new_rollno])
                updated = True
            else:
                writer.writerow(row)

    if updated:
        os.replace(temp_file, user_data_file)
        return jsonify({'success': True, 'message': 'User details updated successfully'})
    else:
        os.remove(temp_file)
        return jsonify({'success': False, 'error': 'User not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)