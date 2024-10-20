#Importing necessary libraries
import face_recognition
import cv2
import numpy as np
import os
import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from PyQt5 import QtWidgets, QtCore, QtGui
import sys


# Initialize global variables
attendance_df = pd.DataFrame(columns=['Employee ID', 'Date', 'Time'])
recognized_employees = set()
employee_images = {}
employee_ids = []


# Load employee images from the specified directory
def load_employee_images():
    path = '/Users/avantika/Desktop/zidio/images'
    for employee_folder in os.listdir(path):
        folder_path = os.path.join(path, employee_folder)
        
        if os.path.isdir(folder_path):  # Ensure it's a folder, not a file
            employee_ids.append(employee_folder)
            employee_images[employee_folder] = []
            
            for image_file in os.listdir(folder_path):
                image_path = os.path.join(folder_path, image_file)
                employee_images[employee_folder].append(image_path)

# Function to find encodings of the images and average them per employee
def findEncodings():
    known_faces = []
    
    for employee_id, image_paths in employee_images.items():
        employee_encodings = []
        
        for image_path in image_paths:
            img = face_recognition.load_image_file(image_path)
            img_encoding = face_recognition.face_encodings(img)
            
        if img_encoding:  # Only add valid encodings
            employee_encodings.append(img_encoding[0])
            # Calculate the average encoding for the employee

        if employee_encodings:
            avg_encoding = np.mean(employee_encodings, axis=0)
            known_faces.append(avg_encoding)
        else:
            print(f"No valid face encodings found for Employee ID: {employee_id}")
    
    return known_faces

    # Mark attendance
def markAttendance(employee_id):
    global attendance_df
    now = datetime.now()
    date_string = now.strftime('%Y-%m-%d')
    time_string = now.strftime('%H:%M:%S')
    
    # Create a DataFrame for the new entry
    new_entry = pd.DataFrame({'Employee ID': [employee_id], 'Date': [date_string], 'Time': [time_string]})
    
    # Use pd.concat to add the new entry to the existing DataFrame
    attendance_df = pd.concat([attendance_df, new_entry], ignore_index=True)

# Function to start the attendance system
def start_attendance_system():
    global recognized_employees
    recognized_employees = set()  # Reset recognized employees for a new session

    encodeListKnown = findEncodings()
    print('Encoding complete!')

    cap = cv2.VideoCapture(0)  # Start the webcam
    frame_count = 0  # Initialize a frame counter

    try:
        while True:
            success, img = cap.read()
            if not success:
                messagebox.showerror("Error", "Failed to capture image from webcam")
                break
            
            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)  # Resize for faster processing
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            # Find faces and encodings in the webcam frame
            facesCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

                # Find the best match
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    employee_id = employee_ids[matchIndex].upper()

                    # Only mark attendance if the employee hasn't been recognized already
                    if employee_id not in recognized_employees:
                        markAttendance(employee_id)
                        recognized_employees.add(employee_id)  # Add to the recognized list
                        print(f'Face recognized: Employee ID {employee_id}')
            
            # Update the display every 5 frames to reduce output clutter
            if frame_count % 5 == 0:
                cv2.imshow('Attendance System', img)

            frame_count += 1  # Increment frame counter

            # Add a break condition to stop the loop in the GUI
            key = cv2.waitKey(1)
            if key == ord('q'):
                break

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        save_attendance_to_excel()

# Save attendance data to an Excel file
def save_attendance_to_excel():
    attendance_df.to_excel('Attendance.xlsx', index=False)
    print("Attendance saved to attendance.xlsx")

class AttendanceApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Employee Attendance System')
        self.setGeometry(100, 100, 400, 200)

        # Layouts
        vbox = QtWidgets.QVBoxLayout()

        # Buttons
        self.load_btn = QtWidgets.QPushButton('Load Employee Images', self)
        self.load_btn.clicked.connect(self.load_images)
        vbox.addWidget(self.load_btn)

        self.start_btn = QtWidgets.QPushButton('Start Attendance System', self)
        self.start_btn.clicked.connect(self.start_attendance)
        vbox.addWidget(self.start_btn)

        self.setLayout(vbox)

    # Button actions
    def load_images(self):
        load_employee_images()
        QtWidgets.QMessageBox.information(self, "Info", "Employee Images Loaded!")

    def start_attendance(self):
        start_attendance_system()
        QtWidgets.QMessageBox.information(self, "Info", "Attendance Completed!")

# Main execution
def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = AttendanceApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

                

