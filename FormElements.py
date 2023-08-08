import tkinter as tk
from datetime import datetime, date

class FormElements:
    def __init__(self):
        self.current_date = date.today().strftime("%d.%m.%Y")

        self.last_name_var = tk.StringVar()
        self.first_name_var = tk.StringVar()
        self.middle_name_var = tk.StringVar()
        self.birth_date_var = tk.StringVar()
        self.position_var = tk.StringVar()
        self.risk_name_var = tk.StringVar()
        self.planned_date_var = tk.StringVar()
        self.actual_date_var = tk.StringVar()
