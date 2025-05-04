import os
import cv2
import numpy as np
import face_recognition
from datetime import datetime
import mediapipe as mp
import smtplib
from email.message import EmailMessage
import logging
import dlib
import csv

# Configure logging
logging.basicConfig(
    filename='email_notifications.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

REGISTERED_DIR = 'registered_faces'
ATTENDANCE_FILE = 'attendance.csv'

if not os.path.exists(REGISTERED_DIR):
    os.makedirs(REGISTERED_DIR)

def send_email_notification(email, name):
    sender_email = "abhaychauhan5051@gmail.com"  # Replace with your email
    sender_password = "csvklapxmsnhubxj"  # Replace with your email password
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    msg = EmailMessage()
    msg.set_content(f"Hello {name},\n\nYour attendance has been successfully marked.\n\nThank you!\n")
    msg["Subject"] = "Attendance Marked"
    msg["From"] = sender_email
    msg["To"] = email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            logging.info(f"Email successfully sent to {email}")
    except Exception as e:
        logging.error(f"Failed to send email to {email}: {e}")
        print(f"Failed to send email to {email}: {e}")

def mark_attendance(name):
    date = datetime.now().strftime('%Y-%m-%d')
    time = datetime.now().strftime('%H:%M:%S')
    attendance_file = 'attendance.csv'
    with open('user_data.csv', 'r') as user_file:
        for line in user_file:
            parts = line.strip().split(',')
            if len(parts) >= 3 and parts[0] == name:
                _, email, rollno = parts[:3]
                with open(attendance_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([name, email, rollno, date, time, 'present'])
                send_email_notification(email, name)
                break

def is_already_present_today(name, date):
    if not os.path.exists(ATTENDANCE_FILE):
        return False
    with open(ATTENDANCE_FILE, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) >= 4 and parts[0] == name and parts[1] == date and parts[3] == 'present':
                return True
    return False

def mark_attendance_status(name, date, status):
    # status: 'present' or 'absent'
    now = datetime.now().strftime('%H:%M:%S')
    with open(ATTENDANCE_FILE, 'a') as f:
        f.write(f'{name},{date},{now},{status}\n')

def get_attendance_status(date):
    # Returns dict: {name: 'present'/'absent'} for all registered users for the date
    status = {}
    users = [os.path.splitext(fn)[0] for fn in os.listdir(REGISTERED_DIR) if fn.lower().endswith('.jpg')]
    for user in users:
        status[user] = 'absent'
    if os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) >= 6 and parts[3] == date:
                    status[parts[0]] = parts[5]
    return status

def load_registered_faces():
    encs, names = [], []
    for fn in os.listdir(REGISTERED_DIR):
        img = face_recognition.load_image_file(os.path.join(REGISTERED_DIR, fn))
        encs.append(face_recognition.face_encodings(img)[0])
        names.append(os.path.splitext(fn)[0])
    return encs, names

def save_face_image(name, img_bgr):
    path = os.path.join(REGISTERED_DIR, f'{name}.jpg')
    cv2.imwrite(path, img_bgr)
    return path

def recognize_faces_and_liveness(img_bgr):
    """
    Improved face detection and liveness detection method for better accuracy.
    Returns a list of dicts: [{ 'name': str or None, 'liveness': bool, 'box': (top, right, bottom, left) }]
    """
    known_encs, known_names = load_registered_faces()
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    # Use a more robust face detection model (e.g., dlib's CNN face detector)
    cnn_face_detector = dlib.cnn_face_detection_model_v1('mmod_human_face_detector.dat')
    face_locations = cnn_face_detector(rgb, 1)  # Upsample the image once for better accuracy

    encs = []
    refined_locations = []
    for face in face_locations:
        rect = face.rect
        top, right, bottom, left = rect.top(), rect.right(), rect.bottom(), rect.left()
        refined_locations.append((top, right, bottom, left))
        face_enc = face_recognition.face_encodings(rgb, [(top, right, bottom, left)])
        if face_enc:
            encs.append(face_enc[0])

    # Liveness detection setup
    mp_fm = mp.solutions.face_mesh
    results = []
    with mp_fm.FaceMesh(static_image_mode=True, max_num_faces=10, refine_landmarks=True) as fm:
        fm_res = fm.process(rgb)
        face_landmarks_list = fm_res.multi_face_landmarks if fm_res.multi_face_landmarks else []

        for i, (enc, loc) in enumerate(zip(encs, refined_locations)):
            name = None
            if known_encs:
                idx = np.argmin(face_recognition.face_distance(known_encs, enc))
                if face_recognition.compare_faces(known_encs, enc)[idx]:
                    name = known_names[idx]
            # Liveness: check blink for this face (if landmarks available)
            liveness = False
            if i < len(face_landmarks_list):
                liveness = is_blinking(face_landmarks_list[i])
            results.append({'name': name, 'liveness': bool(liveness), 'box': loc})
    return results

# Eye aspect ratio for blink detection
LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]

def eye_aspect_ratio(landmarks, idx_list):
    pts = np.array([[landmarks[i].x, landmarks[i].y] for i in idx_list])
    A = np.linalg.norm(pts[1] - pts[5])
    B = np.linalg.norm(pts[2] - pts[4])
    C = np.linalg.norm(pts[0] - pts[3])
    return (A + B) / (2.0 * C)

def is_blinking(landmarks):
    leftEAR = eye_aspect_ratio(landmarks.landmark, LEFT_EYE_IDX)
    rightEAR = eye_aspect_ratio(landmarks.landmark, RIGHT_EYE_IDX)
    ear = (leftEAR + rightEAR) / 2.0
    EAR_THRESH = 0.25
    return ear < EAR_THRESH

def recognize_faces_and_liveness_sequence(imgs):
    """
    imgs: list of BGR images (frames)
    Returns a list of dicts: [{ 'name': str or None, 'liveness': bool, 'box': (top, right, bottom, left) }]
    """
    if not imgs:
        return []
    # Use the first frame to detect faces and get locations
    rgb0 = cv2.cvtColor(imgs[0], cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb0)
    encs = face_recognition.face_encodings(rgb0, face_locations)
    known_encs, known_names = load_registered_faces()
    # For each face, track EAR across frames
    face_ears = [[] for _ in face_locations]
    for img in imgs:
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Use mediapipe face mesh to get landmarks for all faces
        mp_fm = mp.solutions.face_mesh
        with mp_fm.FaceMesh(static_image_mode=True, max_num_faces=10, refine_landmarks=True) as fm:
            fm_res = fm.process(rgb)
            face_landmarks_list = fm_res.multi_face_landmarks if fm_res.multi_face_landmarks else []
            for i, landmarks in enumerate(face_landmarks_list):
                leftEAR = eye_aspect_ratio(landmarks.landmark, LEFT_EYE_IDX)
                rightEAR = eye_aspect_ratio(landmarks.landmark, RIGHT_EYE_IDX)
                ear = (leftEAR + rightEAR) / 2.0
                if i < len(face_ears):
                    face_ears[i].append(ear)
    results = []
    for i, (enc, loc) in enumerate(zip(encs, face_locations)):
        name = None
        if known_encs:
            idx = np.argmin(face_recognition.face_distance(known_encs, enc))
            if face_recognition.compare_faces(known_encs, enc)[idx]:
                name = known_names[idx]
        # Liveness: check if EAR drops below threshold and rises (blink)
        ears = face_ears[i] if i < len(face_ears) else []
        EAR_THRESH = 0.25
        blinked = False
        for j in range(1, len(ears)):
            if ears[j-1] > EAR_THRESH and ears[j] < EAR_THRESH:
                # eye closed
                for k in range(j+1, len(ears)):
                    if ears[k] > EAR_THRESH:
                        blinked = True
                        break
            if blinked:
                break
        results.append({'name': name, 'liveness': bool(blinked), 'box': loc})
    return results