import cv2
import os
import numpy as np
import face_recognition
from datetime import datetime, time
import csv

base_dir = os.path.dirname(os.path.abspath(__file__))

# ---------- Period Time Table ----------
periods = {
    "Period 1": (time(9,15), time(10,15)),
    "Period 2": (time(10,15), time(11,15)),
    "Period 3": (time(11,30), time(12,30)),
    "Period 4": (time(12,30), time(13,30)),
    "Period 5": (time(14,15), time(15,15)),
    "Period 6": (time(15,15), time(16,15))
}

def get_current_period():
    now = datetime.now().time()
    for p, (start, end) in periods.items():
        if start <= now <= end:
            return p
    return None

# ---------- Load Images ----------
images_path = os.path.join(base_dir, "Images")
images = []
student_list = []
person_type = []   # STU / TEA / STF

for file in os.listdir(images_path):
    if file.lower().endswith((".jpg",".png",".jpeg")):
        name = os.path.splitext(file)[0]
        parts = name.split("_")
        if len(parts) < 2:
            print(f"Skipping invalid file name: {file}")
            continue

        role = parts[0]  # STU / TEA / STF

        if role == "STU":
            if len(parts) < 3:
                print(f"Skipping invalid student file: {file}")
                continue
            roll = parts[1]
            person_name = parts[2]
            student_list.append(f"{roll}_{person_name}")
        else:  # TEA / STF
            roll = ""  # no roll
            person_name = parts[1]
            student_list.append(person_name)

        person_type.append(role)

        img = cv2.imread(os.path.join(images_path,file))
        if img is None:
            print(f"Cannot read image: {file}")
            continue
        images.append(img)

# ---------- Encode Faces ----------
known_encodings = []
for img in images:
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    enc = face_recognition.face_encodings(img_rgb)
    if enc:
        known_encodings.append(enc[0])
    else:
        known_encodings.append(None)

marked_today = set()

def mark_attendance(fullName, role):
    current_period = get_current_period()
    if current_period is None:
        print("❌ Outside period time")
        return

    today = datetime.now().strftime("%d-%m-%Y")
    now = datetime.now().strftime("%H:%M:%S")

    # Role-specific file
    if role == "STU":
        roll, name = fullName.split("_")
        file_name = os.path.join(base_dir,f"Attendance_Student_{today}.csv")
        header = ["Date","Roll No","Name","Time","Period"]
        data = [today, roll, name, now, current_period]
    elif role == "TEA":
        name = fullName
        file_name = os.path.join(base_dir,f"Attendance_Teacher_{today}.csv")
        header = ["Date","Name","Time","Period"]
        data = [today, name, now, current_period]
    else:  # STF
        name = fullName
        file_name = os.path.join(base_dir,f"Attendance_Staff_{today}.csv")
        header = ["Date","Name","Time","Period"]
        data = [today, name, now, current_period]

    # Avoid duplicate entries
    if (today, fullName, current_period) in marked_today:
        return
    marked_today.add((today, fullName, current_period))

    # Create file with header if not exists
    if not os.path.exists(file_name):
        with open(file_name,"w",newline="") as f:
            w = csv.writer(f)
            w.writerow(header)

    # Append attendance
    with open(file_name,"a",newline="") as f:
        w = csv.writer(f)
        w.writerow(data)

def start_attendance():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return "Camera Error"

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces_loc = face_recognition.face_locations(rgb)
        faces_enc = face_recognition.face_encodings(rgb, faces_loc)

        for enc,(top,right,bottom,left) in zip(faces_enc,faces_loc):
            matches = face_recognition.compare_faces(known_encodings, enc)
            face_dis = face_recognition.face_distance(known_encodings, enc)
            if len(face_dis)==0:
                continue
            idx = np.argmin(face_dis)
            if matches[idx]:
                fullName = student_list[idx]
                role = person_type[idx]
                mark_attendance(fullName, role)
                display = fullName.split("_")[-1] if role=="STU" else fullName
                display += f" ({role})"
                cv2.rectangle(frame,(left,top),(right,bottom),(0,255,0),2)
                cv2.putText(frame,display,(left,top-10),
                            cv2.FONT_HERSHEY_SIMPLEX,0.75,(0,255,0),2)

        cv2.imshow("AI Attendance System - Press q",frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return "Done"
