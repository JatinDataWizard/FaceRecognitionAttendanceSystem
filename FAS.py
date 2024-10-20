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