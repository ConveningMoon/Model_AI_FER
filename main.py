import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from datetime import datetime
from firebase_admin import credentials, initialize_app, db
import threading
import asyncio
from test_test_model import open_camera, close_camera, send_info
import json
import os
import sys
import requests
import numpy as np

ctk.set_appearance_mode("dark")  # Options: "System" (default), "light", "dark"


def get_credential_path():
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, 'account_lupa_sdk.json')


# Firebase initialization
cred = credentials.Certificate(get_credential_path())
initialize_app(cred, {'databaseURL': 'https://lupa-6edbe-default-rtdb.asia-southeast1.firebasedatabase.app/'})
root_ref = db.reference('classes')  # Base reference to 'classes' in database
report_ref = db.reference('reports')

response_localId = ''


def sign_in_with_email_and_password(email, password):
    payload = json.dumps({"email": email, "password": password, "returnSecureToken": True})
    web_api = "AIzaSyAAAnTrhhpHdsgz6dD6t017dFh1pddjsW0"
    REST_API_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={web_api}"

    r = requests.post(REST_API_URL, data=payload)

    return r.json()


class QuestionnaireWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Class Feedback")
        self.geometry("600x400")
        self.protocol("WM_DELETE_WINDOW", self.on_close)  # Disable close button

        # Sections
        self.responses = {"MATERIAL": [], "TEACHER": [], "SPACE": []}

        self.create_questionnaire()

    def create_questionnaire(self):
        row = 1
        # Header for ratings
        ratings = ["1 - Completely agree", "2 - ", "3", "4", "5", "6", "7 - Completely disagree"]
        for i, rating in enumerate(ratings, start=1):
            label = ctk.CTkLabel(self, text=rating, text_color="#FFFFFF")
            label.grid(row=0, column=i, padx=5, pady=5)

        questions = {
            "MATERIAL": [
                "Did you feel interested in the material studied?",
                "Have you understood the material studied?",
                "Have you found all the necessary information in the material?"
            ],
            "TEACHER": [
                "Was there good and easy communication with the teacher?",
                "Did you manage to understand the teacher's explanations?",
                "Was the teacher able to answer your questions?"
            ],
            "SPACE": [
                "Do you consider that the environment you are in supports your concentration?",
                "Did you feel completely focused during class time?"
            ]
        }

        for category, qs in questions.items():
            for question in qs:
                self.add_question(question, self.responses[category], row)
                row += 1

        submit_btn = ctk.CTkButton(self, text="Submit", command=self.submit)
        submit_btn.grid(row=row, columnspan=8, pady=20)

    def add_question(self, question, response_list, row):
        label = ctk.CTkLabel(self, text=question, text_color="#FFFFFF")
        label.grid(row=row, column=0, sticky="w", padx=5, pady=5)
        var = tk.IntVar(value=0)  # Default value set to 0
        response_list.append(var)
        for value in range(1, 8):
            rb = ctk.CTkRadioButton(self, text=str(value), variable=var, value=value)
            rb.grid(row=row, column=value, padx=5)  # Arrange buttons in columns

    def submit(self):
        if all(value.get() > 0 for scores_list in self.responses.values() for value in scores_list):
            avg_scores = {category: np.mean([score.get() for score in scores])
                          for category, scores in self.responses.items()}
            send_info(response_localId, report_ref, avg_scores)
            self.destroy()
        else:
            ctk.CTkMessageBox.showwarning("Incomplete", "Please answer all questions.")

    def on_close(self):
        pass  # Disable close functionality



class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login")
        self.geometry("300x160")

        self.email_label = ctk.CTkLabel(self, text="Email:", text_color="#343638")
        self.email_label.pack()  # Provide vertical padding
        self.email_entry = ctk.CTkEntry(self)
        self.email_entry.pack()  # Provide vertical padding for spacing

        self.password_label = ctk.CTkLabel(self, text="Password:", text_color="#343638")
        self.password_label.pack()  # Provide vertical padding

        # Add padding between password entry and login button
        self.password_entry = ctk.CTkEntry(self, show="*")
        self.password_entry.pack(pady=(0, 10))  # Increase vertical padding to create more space

        self.login_button = ctk.CTkButton(self, text="Login", command=self.login_user)
        self.login_button.pack(pady=(0, 10))  # Optional vertical padding for the button if needed

    def login_user(self):
        global response_localId
        email = self.email_entry.get()
        password = self.password_entry.get()
        user = sign_in_with_email_and_password(email, password)

        if "localId" in user:  # Assuming successful login if "localId" is part of the response
            response_localId = user['localId']
            self.destroy()
            Application().mainloop()  # Open Classroom Checker Window
        else:
            messagebox.showerror("Login failed", "Please check your credentials")


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Classroom Checker")
        self.geometry("300x100")

        # UI Components modified for CustomTkinter
        self.label = ctk.CTkLabel(self, text="Enter class code", text_color="#343638")
        self.label.pack()

        self.entry = ctk.CTkEntry(self)
        self.entry.pack(pady=(0, 10))

        self.button = ctk.CTkButton(self, text="Enter Class", command=self.check_class)
        self.button.pack(pady=(0, 10))

    def check_class(self):
        class_code = self.entry.get()
        threading.Thread(target=self.query_firebase, args=(class_code,)).start()

    async def async_check_class_deletion(self, class_id):
        while True:
            if not root_ref.child(class_id).get():
                self.entry.configure(state="normal")
                self.button.configure(state="normal")
                print("Class deleted, stopping camera.")
                close_camera()
                questionnaire = QuestionnaireWindow()
                questionnaire.mainloop()
                break
            await asyncio.sleep(5)  # Check every 5 seconds

    def query_firebase(self, code):
        classes = root_ref.get()
        for class_id, details in classes.items():
            if details['code'] == code:
                if details['started']:
                    now = datetime.now()
                    # Extract hour and minute
                    hour = int(details['startedTime']['hour'])
                    minute = int(details['startedTime']['minutes'])
                    current_hour = now.hour
                    current_minute = now.minute
                    # Calculate total minutes from midnight
                    total_minutes1 = hour * 60 + minute
                    total_minutes2 = current_hour * 60 + current_minute
                    # Difference in minutes
                    difference_in_minutes = total_minutes2 - total_minutes1
                    if difference_in_minutes <= 15:  # 15 minutes as the maximum late time to join to the class
                        self.entry.configure(state="disabled")
                        self.button.configure(state="disabled")
                        open_camera(details['subject'])
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(self.async_check_class_deletion(class_id))
                else:
                    print("Class hasn't started yet.")


if __name__ == "__main__":
    LoginWindow().mainloop()
