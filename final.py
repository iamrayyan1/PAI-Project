import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import *
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    filename='diabetes_prediction.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Constants for input validation
FIELD_RANGES = {
    'Pregnancies': (0, 20),
    'Glucose': (0, 300),
    'Blood Pressure': (0, 200),
    'Skin Thickness': (0, 100),
    'Insulin': (0, 850),
    'BMI': (0, 70),
    'Diabetes Pedigree': (0, 2.5),
    'Age': (0, 120)
}


def load_model(model_path='diabetes_model.pkl'):
    try:
        return joblib.load(model_path)
    except Exception as e:
        logging.error(f"Error loading model: {e}")
        messagebox.showerror("Error", f"Failed to load model: {e}")
        return None


def validate_inputs():
    values = {}
    for field, var in zip(FIELD_RANGES.keys(), entry_vars):
        try:
            value = float(var.get())
            min_val, max_val = FIELD_RANGES[field]
            if not min_val <= value <= max_val:
                raise ValueError(f"{field} must be between {min_val} and {max_val}")
            values[field] = value
        except ValueError as e:
            raise ValueError(f"Invalid {field}: {str(e)}")
    return values


def predict_diabetes():
    if model is None:
        messagebox.showerror("Error", "Model not loaded")
        return

    try:
        values = validate_inputs()
        input_data = np.array([[values[field] for field in FIELD_RANGES.keys()]])

        prediction = model.predict(input_data)
        probability = model.predict_proba(input_data)[0][1]

        outcome = "Diabetic" if prediction[0] == 1 else "Non-Diabetic"
        show_prediction_result(outcome, probability, values)
        save_prediction(outcome, values)

    except ValueError as e:
        messagebox.showerror("Input Error", str(e))
    except Exception as e:
        logging.error(f"Prediction error: {e}")
        messagebox.showerror("Error", f"Prediction failed: {str(e)}")


def show_prediction_result(outcome, probability, values):
    result_window = tk.Toplevel(window)
    result_window.title("Prediction Result")
    result_window.geometry("400x300")

    try:
        result_window.iconbitmap("diabetes.png")
    except:
        pass

    style = ttk.Style()
    style.configure("Result.TLabel", font=("Helvetica", 12))

    ttk.Label(
        result_window,
        text=f"Prediction: {outcome}",
        style="Result.TLabel"
    ).pack(pady=10)

    ttk.Label(
        result_window,
        text=f"Probability: {probability:.2%}",
        style="Result.TLabel"
    ).pack(pady=10)

    for field, value in values.items():
        ttk.Label(
            result_window,
            text=f"{field}: {value}",
            style="Result.TLabel"
        ).pack(pady=2)


def save_prediction(outcome, values):
    try:
        values['Outcome'] = outcome
        df = pd.DataFrame([values])

        file_path = Path("diabetes_predictions.csv")
        df.to_csv(
            file_path,
            mode='a',
            header=not file_path.exists(),
            index=False
        )
        logging.info(f"Prediction saved: {values}")
    except Exception as e:
        logging.error(f"Error saving prediction: {e}")
        messagebox.showerror("Save Error", f"Could not save prediction: {e}")


def batch_predict():
    if model is None:
        messagebox.showerror("Error", "Model not loaded")
        return

    try:
        input_file = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")]
        )
        if not input_file:
            return

        data = pd.read_csv(input_file)
        required_columns = list(FIELD_RANGES.keys())

        # Validate columns
        if not all(col in data.columns for col in required_columns):
            missing = set(required_columns) - set(data.columns)
            raise ValueError(f"Missing required columns: {missing}")

        # Make predictions
        predictions = model.predict(data[required_columns])
        probabilities = model.predict_proba(data[required_columns])[:, 1]

        # Add predictions to dataframe
        data['Predicted_Outcome'] = predictions
        data['Probability'] = probabilities

        # Save results
        save_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if save_path:
            data.to_csv(save_path, index=False)
            messagebox.showinfo(
                "Success",
                f"Batch predictions saved to {save_path}"
            )

    except Exception as e:
        logging.error(f"Batch prediction error: {e}")
        messagebox.showerror("Error", f"Batch prediction failed: {str(e)}")


def reset_form():
    for var in entry_vars:
        var.set("")


def toggle_theme():
    if window.cget("bg") == "#25446C":
        set_light_theme()
    else:
        set_dark_theme()


def set_dark_theme():
    window.config(bg="#25446C")
    apply_theme("#25446C", "white", "#1E1E1E", "white")


def set_light_theme():
    window.config(bg="#FFFFFF")
    apply_theme("#FFFFFF", "black", "#F7F7F7", "black")


def apply_theme(bg, fg, input_bg, input_fg):
    title_frame.config(bg=bg)
    input_frame.config(bg=bg)
    footer_frame.config(bg=bg)

    for widget in input_frame.winfo_children():
        if isinstance(widget, tk.Label):
            widget.config(bg=bg, fg=fg)

    title_label.config(bg=bg, fg=fg)
    footer_label.config(bg=bg, fg=fg)



def show_help():
    help_text = """
Diabetes Prediction System - Help

Input Fields:
1. Pregnancies: Number of times pregnant (0-20)
2. Glucose: Plasma glucose concentration (0-300 mg/dL)
3. Blood Pressure: Diastolic blood pressure (0-200 mm Hg)
4. Skin Thickness: Triceps skinfold thickness (0-100 mm)
5. Insulin: 2-Hour serum insulin (0-850 mu U/ml)
6. BMI: Body Mass Index (0-70)
7. Diabetes Pedigree: Diabetes pedigree function (0-2.5)
8. Age: Age in years (0-120)

Features:
- Individual prediction
- Batch prediction from CSV
- Dark/Light theme
- Result saving
- Input validation

Note: All values must be within the specified ranges for accurate prediction.
"""
    messagebox.showinfo("Help", help_text)


def create_tooltip(widget, text):

    def show_tooltip(event):
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root + 25}+{event.y_root + 20}")

        label = tk.Label(
            tooltip,
            text=text,
            justify=tk.LEFT,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            font=("Helvetica", "10", "normal")
        )
        label.pack()

        def hide_tooltip():
            tooltip.destroy()

        tooltip.timer = tooltip.after(2000, hide_tooltip)
        widget.tooltip = tooltip

    def hide_tooltip(event):
        tooltip = getattr(widget, 'tooltip', None)
        if tooltip:
            tooltip.after_cancel(tooltip.timer)
            tooltip.destroy()
            widget.tooltip = None

    widget.bind('<Enter>', show_tooltip)
    widget.bind('<Leave>', hide_tooltip)



import hashlib
import sqlite3
import re


class UserDatabase:
    def __init__(self, db_path='user_database.db'):
        """Initialize database connection and create users table."""
        self.db_path = db_path
        self.create_user_table()

    def create_user_table(self):
        """Create users table if it doesn't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        password TEXT NOT NULL,
                        email TEXT,
                        full_name TEXT
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not create user table: {e}")

    def hash_password(self, password):
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def validate_email(self, email):
        """Validate email format using regex."""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    def register_user(self, username, password, email, full_name):
        """Register a new user with comprehensive validation."""
        # Input validation
        if not all([username, password, email, full_name]):
            messagebox.showerror("Error", "All fields are required")
            return False

        # Username validation
        if len(username) < 4:
            messagebox.showerror("Error", "Username must be at least 4 characters long")
            return False

        # Password strength validation
        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters long")
            return False

        # Email validation
        if not self.validate_email(email):
            messagebox.showerror("Error", "Invalid email format")
            return False

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if username already exists
                cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
                if cursor.fetchone():
                    messagebox.showerror("Error", "Username already exists")
                    return False

                # Check if email already exists
                cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
                if cursor.fetchone():
                    messagebox.showerror("Error", "Email already registered")
                    return False

                # Insert new user
                hashed_password = self.hash_password(password)
                cursor.execute(
                    "INSERT INTO users (username, password, email, full_name) VALUES (?, ?, ?, ?)",
                    (username, hashed_password, email, full_name)
                )
                conn.commit()

                messagebox.showinfo("Success", "User registered successfully")
                return True

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Registration failed: {e}")
            return False

    def authenticate_user(self, username, password):
        """Authenticate user credentials."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Retrieve user's hashed password
                cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
                result = cursor.fetchone()

                # Check credentials
                if result and result[0] == self.hash_password(password):
                    return True
                else:
                    messagebox.showerror("Login Failed", "Invalid username or password")
                    return False

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Login failed: {e}")
            return False


class LoginRegistrationApp:
    def __init__(self, on_successful_login):
        """Initialize the login and registration application."""
        self.user_db = UserDatabase()
        self.on_successful_login = on_successful_login

    def create_login_window(self):
        """Create the main login window."""
        self.login_window = tk.Tk()
        self.login_window.title("Diabetes Prediction System - Login")
        self.login_window.geometry("400x600")

        icon = PhotoImage(file='images/diabetes icon.png')
        self.login_window.iconphoto(True, icon)

        # Login Frame
        login_frame = tk.Frame(self.login_window, padx=20, pady=20)
        login_frame.pack(expand=True, fill=tk.BOTH)

        # Logo
        try:
            logo = tk.PhotoImage(file='images/healthcare app.png')
            logo_label = tk.Label(login_frame, image=logo)
            logo_label.image = logo  # Keep a reference
            logo_label.pack(pady=20)
        except:
            pass

        # Title
        title_label = tk.Label(
            login_frame,
            text="Diabetes Prediction System",
            font=("Times New Roman", 16, "bold")
        )
        title_label.pack(pady=10)

        # Username
        username_label = tk.Label(login_frame, text="Username", font=("Helvetica", 12))
        username_label.pack(pady=(10, 5))
        self.username_entry = ttk.Entry(login_frame, font=("Helvetica", 12), width=30)
        self.username_entry.pack(pady=5)

        # Password
        password_label = tk.Label(login_frame, text="Password", font=("Helvetica", 12))
        password_label.pack(pady=(10, 5))
        self.password_entry = ttk.Entry(login_frame, show="*", font=("Helvetica", 12), width=30)
        self.password_entry.pack(pady=5)

        # Login Button
        login_button = ttk.Button(
            login_frame,
            text="Login",
            command=self.login_action
        )
        login_button.pack(pady=10)

        # Register Button
        register_button = ttk.Button(
            login_frame,
            text="Register New User",
            command=self.open_registration_window
        )
        register_button.pack(pady=5)

        # Help Text
        help_label = tk.Label(
            login_frame,
            text="Hint: Register first if you're a new user.",
            font=("Helvetica", 10)
        )
        help_label.pack(pady=10)

        self.login_window.mainloop()

    def login_action(self):
        """Handle login process."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.user_db.authenticate_user(username, password):
            self.login_window.destroy()
            self.on_successful_login()

    def open_registration_window(self):
        """Create registration window."""
        # Close login window if open
        if hasattr(self, 'login_window'):
            self.login_window.destroy()

        # Create registration window
        reg_window = tk.Tk()
        reg_window.title("Diabetes Prediction System - Registration")
        reg_window.geometry("400x600")

        # Try to set window icon
        try:
            reg_window.iconbitmap("images/diabetes icon.png")
        except:
            pass

        # Registration Frame
        reg_frame = tk.Frame(reg_window, padx=20, pady=20)
        reg_frame.pack(expand=True, fill=tk.BOTH)

        # Title
        title_label = tk.Label(
            reg_frame,
            text="Create New Account",
            font=("Times New Roman", 16, "bold")
        )
        title_label.pack(pady=10)

        # Full Name
        full_name_label = tk.Label(reg_frame, text="Full Name", font=("Helvetica", 12))
        full_name_label.pack(pady=(10, 5))
        full_name_entry = ttk.Entry(reg_frame, font=("Helvetica", 12), width=30)
        full_name_entry.pack(pady=5)

        # Username
        username_label = tk.Label(reg_frame, text="Username", font=("Helvetica", 12))
        username_label.pack(pady=(10, 5))
        username_entry = ttk.Entry(reg_frame, font=("Helvetica", 12), width=30)
        username_entry.pack(pady=5)

        # Email
        email_label = tk.Label(reg_frame, text="Email", font=("Helvetica", 12))
        email_label.pack(pady=(10, 5))
        email_entry = ttk.Entry(reg_frame, font=("Helvetica", 12), width=30)
        email_entry.pack(pady=5)

        # Password
        password_label = tk.Label(reg_frame, text="Password", font=("Helvetica", 12))
        password_label.pack(pady=(10, 5))
        password_entry = ttk.Entry(reg_frame, show="*", font=("Helvetica", 12), width=30)
        password_entry.pack(pady=5)

        # Confirm Password
        confirm_password_label = tk.Label(reg_frame, text="Confirm Password", font=("Helvetica", 12))
        confirm_password_label.pack(pady=(10, 5))
        confirm_password_entry = ttk.Entry(reg_frame, show="*", font=("Helvetica", 12), width=30)
        confirm_password_entry.pack(pady=5)

        def register_action():
            """Handle user registration."""
            # Check password match
            if password_entry.get() != confirm_password_entry.get():
                messagebox.showerror("Error", "Passwords do not match")
                return

            # Attempt registration
            registration_success = self.user_db.register_user(
                username_entry.get(),
                password_entry.get(),
                email_entry.get(),
                full_name_entry.get()
            )

            if registration_success:
                reg_window.destroy()
                self.create_login_window()

        def back_to_login():
            """Return to login window."""
            reg_window.destroy()
            self.create_login_window()

        # Register Button
        register_button = ttk.Button(
            reg_frame,
            text="Register",
            command=register_action
        )
        register_button.pack(pady=10)

        # Back to Login Button
        back_button = ttk.Button(
            reg_frame,
            text="Back to Login",
            command=back_to_login
        )
        back_button.pack(pady=5)

        # Password Requirements
        requirements_label = tk.Label(
            reg_frame,
            text="Password must be at least 8 characters long",
            font=("Helvetica", 10, "italic")
        )
        requirements_label.pack(pady=5)

        def register_user(self, username, password, email, full_name):
            """Register a new user with comprehensive validation."""
            print(f"Attempting to register: {username}, {email}")  # Debug print

            # Input validation
            if not all([username, password, email, full_name]):
                print("Registration failed: All fields are required")  # Debug print
                messagebox.showerror("Error", "All fields are required")
                return False

            # Username validation
            if len(username) < 4:
                print("Registration failed: Username too short")  # Debug print
                messagebox.showerror("Error", "Username must be at least 4 characters long")
                return False

            # Password strength validation
            if len(password) < 8:
                print("Registration failed: Password too short")  # Debug print
                messagebox.showerror("Error", "Password must be at least 8 characters long")
                return False

            # Email validation
            if not self.validate_email(email):
                print("Registration failed: Invalid email")  # Debug print
                messagebox.showerror("Error", "Invalid email format")
                return False

            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()

                    # Check if username already exists
                    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
                    if cursor.fetchone():
                        print(f"Registration failed: Username {username} already exists")  # Debug print
                        messagebox.showerror("Error", "Username already exists")
                        return False

                    # Check if email already exists
                    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
                    if cursor.fetchone():
                        print(f"Registration failed: Email {email} already registered")  # Debug print
                        messagebox.showerror("Error", "Email already registered")
                        return False

                    # Insert new user
                    hashed_password = self.hash_password(password)
                    cursor.execute(
                        "INSERT INTO users (username, password, email, full_name) VALUES (?, ?, ?, ?)",
                        (username, hashed_password, email, full_name)
                    )
                    conn.commit()

                    print("User registered successfully")  # Debug print
                    messagebox.showinfo("Success", "User registered successfully")
                    return True

            except sqlite3.Error as e:
                print(f"Database Error during registration: {e}")  # Debug print
                messagebox.showerror("Database Error", f"Registration failed: {e}")
                return False

        reg_window.mainloop()




def main():
    def start_main_application():
        try:
            login_app.login_window.destroy()
        except:
            pass

        global window, model, entry_vars, title_label, footer_label,title_frame, input_frame, footer_frame
        window = tk.Tk()
        window.title("Diabetes Prediction System")
        window.geometry("600x750")

        icon = PhotoImage(file='images/diabetes icon.png')
        window.iconphoto(True, icon)

        window.title("Diabetes Prediction System")
        window.geometry("600x750")

        # Load model
        model = load_model()

        title_frame = tk.Frame(window)
        title_frame.pack(fill=tk.X)

        logo = tk.PhotoImage(file='images/healthcare app.png')
        title_label = tk.Label(
            title_frame,
            text="Diabetes Prediction System",
            font=("Times New Roman", 20, "bold"),
            image=logo,
            compound=tk.TOP
        )
        title_label.pack(pady=10)

        input_frame = tk.Frame(window, padx=20, pady=20, relief="sunken")
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        fields = list(FIELD_RANGES.keys())
        entry_vars = [tk.StringVar() for _ in fields]

        for idx, (field, var) in enumerate(zip(fields, entry_vars)):
            label = tk.Label(input_frame, text=field, font=("Helvetica", 12))
            label.grid(row=idx, column=0, sticky="w", pady=10)

            entry = ttk.Entry(input_frame, textvariable=var, font=("Helvetica", 12), width=30)
            entry.grid(row=idx, column=1, pady=10)

            min_val, max_val = FIELD_RANGES[field]
            create_tooltip(entry, f"Valid range: {min_val} - {max_val}")

        buttons_frame = tk.Frame(window, bg="#25446C")
        buttons_frame.pack(pady=10)

        ttk.Button(buttons_frame, text="Predict", command=predict_diabetes).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Reset", command=reset_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Batch Predict", command=batch_predict).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Toggle Theme", command=toggle_theme).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Help", command=show_help).pack(side=tk.LEFT, padx=5)

        footer_frame = tk.Frame(window)
        footer_frame.pack(fill=tk.X)
        footer_label = tk.Label(
            footer_frame,
            text="© 2024 Diabetes Prediction System - Developed by 3Rs.",
            font=("Helvetica", 10)
        )
        footer_label.pack(pady=10)

        set_dark_theme()

        window.mainloop()

    login_app = LoginRegistrationApp(start_main_application)
    login_app.create_login_window()


if __name__ == "__main__":
    main()