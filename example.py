import tkinter as tk
from tkinter import simpledialog, messagebox
import cv2, os, numpy as np, face_recognition
import mediapipe as mp
from datetime import datetime

# ——— setup ———
if not os.path.exists('registered_faces'):
    os.makedirs('registered_faces')
attendance_file = 'attendance.csv'

mp_fd = mp.solutions.face_detection
mp_fm = mp.solutions.face_mesh
mp_drw = mp.solutions.drawing_utils

def mark_attendance(name):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(attendance_file, 'a') as f:
        f.write(f'{name},{now}\n')

def load_registered_faces():
    encs, names = [], []
    for fn in os.listdir('registered_faces'):
        img = face_recognition.load_image_file(f'registered_faces/{fn}')
        encs.append(face_recognition.face_encodings(img)[0])
        names.append(os.path.splitext(fn)[0])
    return encs, names

def register_face():
    name = simpledialog.askstring("Input","Enter name:")
    if not name: return
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret: break
        cv2.imshow("Register (press 's')", frame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            cv2.imwrite(f'registered_faces/{name}.jpg', frame)
            messagebox.showinfo("Done", f"{name} registered!")
            break
    cap.release(); cv2.destroyAllWindows()

# ——— blink detector helpers ———
LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144]   # MediaPipe landmarks
RIGHT_EYE_IDX= [362, 385, 387, 263, 373, 380]

def eye_aspect_ratio(landmarks, idx_list):
    # compute distances between vertical landmarks and horizontal
    pts = np.array([[landmarks[i].x, landmarks[i].y] for i in idx_list])
    # vertical dist
    A = np.linalg.norm(pts[1] - pts[5])
    B = np.linalg.norm(pts[2] - pts[4])
    # horizontal
    C = np.linalg.norm(pts[0] - pts[3])
    return (A + B) / (2.0 * C)

def detect_faces():
    known_encs, known_names = load_registered_faces()
    cap = cv2.VideoCapture(0)

    with mp_fd.FaceDetection(model_selection=0, min_detection_confidence=0.5) as fd, \
         mp_fm.FaceMesh(max_num_faces=1,
                        refine_landmarks=True,
                        min_detection_confidence=0.5,
                        min_tracking_confidence=0.5) as fm:

        blinked = False
        EAR_THRESH = 0.25

        while True:
            ret, frame = cap.read()
            if not ret: break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 1) face detection
            fd_res = fd.process(rgb)
            # 2) face mesh for liveness
            fm_res = fm.process(rgb)

            if fm_res.multi_face_landmarks:
                lm = fm_res.multi_face_landmarks[0].landmark
                leftEAR  = eye_aspect_ratio(lm, LEFT_EYE_IDX)
                rightEAR = eye_aspect_ratio(lm, RIGHT_EYE_IDX)
                ear = (leftEAR + rightEAR) / 2.0

                if ear < EAR_THRESH:
                    blinked = True
                    cv2.putText(frame, "Blink detected ✅", (10,30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                else:
                    cv2.putText(frame, "Please blink to verify liveness", (10,30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

            # only if a face is detected and liveness confirmed…
            if fd_res.detections and blinked:
                for det in fd_res.detections:
                    b = det.location_data.relative_bounding_box
                    ih, iw, _ = frame.shape
                    x, y = int(b.xmin*iw), int(b.ymin*ih)
                    w, h = int(b.width*iw), int(b.height*ih)
                    top, right, bottom, left = y, x+w, y+h, x

                    # 3) recognition
                    encs = face_recognition.face_encodings(
                        rgb,
                        known_face_locations=[(top,right,bottom,left)],
                        num_jitters=1
                    )
                    if encs:
                        idx = np.argmin(face_recognition.face_distance(known_encs, encs[0]))
                        if face_recognition.compare_faces(known_encs, encs[0])[idx]:
                            name = known_names[idx]
                            mark_attendance(name)
                            cv2.putText(frame, name, (x, y-10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                        else:
                            cv2.putText(frame, "Unknown", (x, y-10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

                    cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)

            cv2.imshow("Attendance (Esc to exit)", frame)
            if cv2.waitKey(5) & 0xFF == 27:
                break

    cap.release()
    cv2.destroyAllWindows()

# ——— GUI ———
root = tk.Tk(); root.title("Secure Face Attendance")
tk.Button(root, text="Register New Face", command=register_face,
          width=30, height=2, bg='lightblue').pack(pady=20)
tk.Button(root, text="Start Secure Attendance", command=detect_faces,
          width=30, height=2, bg='lightgreen').pack(pady=20)
root.mainloop()
