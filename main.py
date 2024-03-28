import tkinter as tk
from firebase_admin import credentials, initialize_app, db
import threading
import asyncio
from test_test_model import open_camera, close_camera

# Firebase initialization
cred = credentials.Certificate("account_lupa_sdk.json")
initialize_app(cred, {'databaseURL': 'https://lupa-6edbe-default-rtdb.asia-southeast1.firebasedatabase.app/'})
root_ref = db.reference('classes')  # Base reference to 'classes' in database


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Classroom Checker")
        self.geometry("300x100")

        # UI Components
        self.label = tk.Label(self, text="Enter class code")
        self.label.pack()

        self.entry = tk.Entry(self)
        self.entry.pack()

        self.button = tk.Button(self, text="Check Class", command=self.check_class)
        self.button.pack()

    def check_class(self):
        class_code = self.entry.get()
        threading.Thread(target=self.query_firebase, args=(class_code,)).start()

    async def async_check_class_deletion(self, class_id):
        while True:
            if not root_ref.child(class_id).get():
                print("Class deleted, stopping camera.")
                close_camera()
                break
            await asyncio.sleep(5)  # Check every 5 seconds

    def query_firebase(self, code):
        classes = root_ref.get()
        for class_id, details in classes.items():
            if details['code'] == code:
                if details['started']:
                    open_camera()
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.async_check_class_deletion(class_id))
                else:
                    print("Class hasn't started yet.")


if __name__ == "__main__":
    app = Application()
    app.mainloop()
