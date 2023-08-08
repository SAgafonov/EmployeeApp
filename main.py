import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime, date
from tkcalendar import DateEntry
from PIL import Image, ImageTk


def show_all_employees():
    conn = sqlite3.connect("employee.db")
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, last_name, first_name, middle_name, birth_date, position
        FROM employee
    ''')
    employees = cursor.fetchall()

    for employee in employees:
        print(f"ID: {employee[0]}")
        print(f"Фамилия: {employee[1]}")
        print(f"Имя: {employee[2]}")
        print(f"Отчество: {employee[3]}")
        print(f"Дата рождения: {employee[4]}")
        print(f"Должность: {employee[5]}")
        print("Факторы риска:")

        cursor.execute('''
            SELECT risk_name, planned_date, actual_date
            FROM risk_factor
            WHERE employee_id = ?
        ''', (employee[0],))
        risk_factors = cursor.fetchall()

        for risk_factor in risk_factors:
            print(f"  Фактор риска: {risk_factor[0]}")
            print(f"  Планируемая дата: {risk_factor[1]}")
            print(f"  Фактическая дата: {risk_factor[2]}")

        print("-" * 20)

    conn.close()

class RiskFactor:
    def __init__(self, planned_date=None, actual_date=None):
        self.planned_date = planned_date
        self.actual_date = actual_date

# class Employee:
#     def __init__(self, last_name, first_name, middle_name, birth_date, position):
#         self.last_name = last_name
#         self.first_name = first_name
#         self.middle_name = middle_name
#         self.birth_date = birth_date
#         self.position = position
#         self.risk_factors = []
#
#     def add_risk_factor(self, risk_name, planned_date=None, actual_date=None):
#         risk_factor = RiskFactor(planned_date, actual_date)
#         self.risk_factors.append((risk_name, risk_factor))
#

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


class AddEmployeeApp(FormElements):
    def __init__(self, add_user_window):
        super().__init__()
        self.root_add_user_window = add_user_window
        self.root_add_user_window.title("Добавление пользователя")

        self.risk_entries = []  # Список для хранения текстовых полей для факторов риска

        self.error_label = tk.Label(self.root_add_user_window, text="", fg="red")
        self.error_label.pack()

        self.create_add_user_widgets()

    def create_add_user_widgets(self):
        self.employee_frame = tk.Frame(self.root_add_user_window)
        self.employee_frame.pack(side="left", padx=20, pady=20)

        # Поля для сотрудника
        tk.Label(self.employee_frame, text="Фамилия:").pack(anchor="w")
        self.last_name_entry = tk.Entry(self.employee_frame, textvariable=self.last_name_var)
        self.last_name_entry.pack(fill="x", anchor="w")

        tk.Label(self.employee_frame, text="Имя:").pack(anchor="w")
        self.first_name_entry = tk.Entry(self.employee_frame, textvariable=self.first_name_var)
        self.first_name_entry.pack(fill="x", anchor="w")

        tk.Label(self.employee_frame, text="Отчество:").pack(anchor="w")
        self.middle_name_entry = tk.Entry(self.employee_frame, textvariable=self.middle_name_var)
        self.middle_name_entry.pack(fill="x", anchor="w")

        tk.Label(self.employee_frame, text="Дата рождения:").pack(anchor="w")
        self.birth_date_cal = DateEntry(self.employee_frame, date_pattern="dd.MM.yyyy", textvariable=self.birth_date_var)
        self.birth_date_cal.pack(fill="x", anchor="w")

        tk.Label(self.employee_frame, text="Должность:").pack(anchor="w")
        self.position_entry = tk.Entry(self.employee_frame, textvariable=self.position_var)
        self.position_entry.pack(fill="x", anchor="w")

        # Рамка для факторов риска и скроллбара
        self.risk_frame = tk.Frame(self.root_add_user_window)
        self.risk_frame.pack(side="right", padx=10, pady=10, fill="both", expand=True)

        # Канвас для прокрутки
        self.risk_canvas = tk.Canvas(self.risk_frame)
        self.risk_canvas.pack(side="top", fill="both", expand=True)

        # Скроллбар для канваса будет находиться внутри risk_canvas, иначе он почти не виден
        self.risk_scrollbar = tk.Scrollbar(self.risk_canvas, command=self.risk_canvas.yview)
        self.risk_scrollbar.pack(side="right", fill="y")

        self.risk_canvas.config(yscrollcommand=self.risk_scrollbar.set)
        self.risk_canvas.bind("<Configure>",
                              lambda e: self.risk_canvas.configure(scrollregion=self.risk_canvas.bbox("all")))

        # Рамка для элементов рисков
        self.risk_entries_frame = tk.Frame(self.risk_canvas)
        self.risk_canvas.create_window((0, 0), window=self.risk_entries_frame, anchor="nw")

        # Кнопки "Добавить риск", "Добавить" и "Отменить"
        button_frame = tk.Frame(self.employee_frame)
        button_frame.pack(side="bottom", pady=10)
        tk.Button(button_frame, text="Добавить риск", command=self.add_risk_entry).pack(side="left", padx=15)
        tk.Button(button_frame, text="Добавить", command=self.add_employee, bg="green").pack(side="left", padx=5)
        tk.Button(button_frame, text="Отменить", command=self.cancel, bg="red").pack(side="right", padx=5)
        tk.Button(button_frame, text="Очистить риски", command=self.clear_risks).pack(side="left", padx=20, pady=5)
        tk.Button(button_frame, text="Очистить всё", command=self.clear_all).pack(side="left", padx=20, pady=5)

    def add_risk_entry(self):
        tk.Label(self.risk_entries_frame, text="Фактор риска:").pack()
        risk_entry = tk.Entry(self.risk_entries_frame)
        risk_entry.pack()
        self.risk_entries.append((risk_entry, None, None))  # (Текстовое поле, Planned Date, Actual Date)

        tk.Label(self.risk_entries_frame, text="Планируемая дата:").pack()
        planned_date_cal = DateEntry(self.risk_entries_frame, date_pattern="dd.MM.yyyy", textvariable=tk.StringVar())
        planned_date_cal.pack()
        planned_date_cal.set_date(self.current_date)
        self.risk_entries[-1] = (risk_entry, planned_date_cal, self.risk_entries[-1][2])

        tk.Label(self.risk_entries_frame, text="Фактическая дата:").pack()
        actual_date_cal = DateEntry(self.risk_entries_frame, date_pattern="dd.MM.yyyy", textvariable=tk.StringVar())
        actual_date_cal.pack()
        actual_date_cal.set_date(self.current_date)
        self.risk_entries[-1] = (risk_entry, planned_date_cal, actual_date_cal)

    def clear_risks(self):
        self.risk_entries_frame.destroy()
        self.risk_entries_frame = tk.Frame(self.risk_canvas)
        self.risk_canvas.create_window((0, 0), window=self.risk_entries_frame, anchor="nw")

        self.risk_entries = []

    def clear_all(self):
        self.last_name_entry.delete(0, tk.END)
        self.first_name_entry.delete(0, tk.END)
        self.middle_name_entry.delete(0, tk.END)
        self.birth_date_cal.set_date(self.current_date)
        self.position_entry.delete(0, tk.END)
        self.clear_risks()

    def add_employee(self):
        if self.validate_fields():
            last_name = self.last_name_var.get()
            first_name = self.first_name_var.get()
            middle_name = self.middle_name_var.get()
            birth_date = self.birth_date_var.get()
            position = self.position_var.get()

            conn = sqlite3.connect("employee.db")
            cursor = conn.cursor()

            # Сохранение данных сотрудника
            cursor.execute('''
                            INSERT INTO employee (last_name, first_name, middle_name, birth_date, position)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (last_name, first_name, middle_name, birth_date, position))
            employee_id = cursor.lastrowid

            # self.employee = Employee(last_name, first_name, middle_name, birth_date, position)
            # for risk_entry, planned_date_entry, actual_date_entry in self.risk_entries:
            #     risk_name = risk_entry.get()
            #     planned_date = planned_date_entry.get()
            #     actual_date = actual_date_entry.get()
            #     if risk_name:
            #         self.employee.add_risk_factor(risk_name, planned_date, actual_date)

            # Сохранение факторов риска
            for risk_entry in self.risk_entries:
                risk_name = risk_entry[0].get()
                planned_date = risk_entry[1].get()
                actual_date = risk_entry[2].get()

                if risk_name:
                    cursor.execute('''
                                    INSERT INTO risk_factor (employee_id, risk_name, planned_date, actual_date)
                                    VALUES (?, ?, ?, ?)
                                ''', (employee_id, risk_name, planned_date, actual_date))

            conn.commit()
            conn.close()

            messagebox.showinfo("Информация", "Информация о сотруднике и рисках сохранена.", parent=self.root_add_user_window)
            self.clear_all()
            #### TEST
            # print("ФИО:", self.employee.last_name, self.employee.first_name, self.employee.middle_name)
            # print("Дата рождения:", self.employee.birth_date)
            # print("Должность:", self.employee.position)
            # print("Факторы риска:")
            # for risk_name, risk_factor in self.employee.risk_factors:
            #     print(f"- {risk_name}")
            #     if risk_factor.planned_date:
            #         print(f"  Планируемая дата прохождения: {risk_factor.planned_date}")
            #     if risk_factor.actual_date:
            #         print(f"  Фактическая дата прохождения: {risk_factor.actual_date}")

            show_all_employees()

    def validate_fields(self):
        error_message = ""
        if not self.last_name_var.get():
            error_message += "Заполните фамилию.\n"
        if not self.first_name_var.get():
            error_message += "Заполните имя.\n"
        if not self.middle_name_var.get():
            error_message += "Заполните отчество.\n"
        if not self.birth_date_var.get():
            error_message += "Заполните дату рождения.\n"
        if not self.position_var.get():
            error_message += "Заполните должность.\n"
        if not self.risk_entries:
            error_message += f"Заполните хотя бы один риск.\n"

        for risk_entry, planned_date_cal, actual_date_cal in self.risk_entries:
            risk_name = risk_entry.get()
            planned_date = planned_date_cal.get_date()
            actual_date = actual_date_cal.get_date()

            if not risk_name:
                error_message += f"Заполните название риска.\n"
            if risk_name and not planned_date:
                error_message += f"Заполните планируемую дату для риска '{risk_name}'.\n"
            if risk_name and not actual_date:
                error_message += f"Заполните фактическую дату для риска '{risk_name}'.\n"

        if error_message:
            self.error_label.config(text=error_message)
            return False

        self.error_label.config(text="")
        return True

    def cancel(self):
        if messagebox.askyesno("Отмена", "Изменения не будут сохранены. Продолжить?", parent=self.root_add_user_window):
            self.root_add_user_window.destroy()

    def show_success_message(self, message: str):
        success_popup = tk.Toplevel(self.root_add_user_window)
        success_popup.title("Успех")
        success_popup.geometry("200x100")
        tk.Label(success_popup, text=message).pack(pady=20)
        tk.Button(success_popup, text="Закрыть", command=success_popup.destroy).pack()

class SearchEmployeeApp(FormElements):
    def __init__(self, main_frame, search_window):
        super().__init__()
        self.main_frame = main_frame
        self.root_search_window = search_window
        self.root_search_window.title("Поиск")

        # self.search_frame = None  # Форма поиска

        self.risk_entries = []  # Список для хранения текстовых полей для факторов риска

        self.employees = []

        show_all_employees()

        self.create_search_widgets()

    def create_search_widgets(self):
        # if self.search_frame:
        #     self.search_frame.destroy()

        self.search_frame = tk.Frame(self.root_search_window)
        self.search_frame.pack(side="left", padx=20, pady=20)

        # Поля для сотрудника
        tk.Label(self.search_frame, text="Фамилия:").grid(row=0, column=0, sticky="w")
        self.last_name_var = tk.StringVar()
        self.last_name_entry = tk.Entry(self.search_frame, textvariable=self.last_name_var)
        self.last_name_entry.grid(row=0, column=1, sticky="w")

        tk.Label(self.search_frame, text="Имя:").grid(row=1, column=0, sticky="w")
        self.first_name_var = tk.StringVar()
        self.first_name_entry = tk.Entry(self.search_frame, textvariable=self.first_name_var)
        self.first_name_entry.grid(row=1, column=1, sticky="w")

        tk.Label(self.search_frame, text="Отчество:").grid(row=2, column=0, sticky="w")
        self.middle_name_var = tk.StringVar()
        self.middle_name_entry = tk.Entry(self.search_frame, textvariable=self.middle_name_var)
        self.middle_name_entry.grid(row=2, column=1, sticky="w")

        tk.Label(self.search_frame, text="Дата рождения:").grid(row=3, column=0, sticky="w")
        self.birth_date_var = tk.StringVar()
        self.birth_date_cal = DateEntry(self.search_frame, date_pattern="dd.MM.yyyy", textvariable=self.birth_date_var)
        self.birth_date_cal.grid(row=3, column=1, sticky="w")
        self.birth_date_cal.delete(0, tk.END)  # очищаем строку

        tk.Label(self.search_frame, text="Должность:").grid(row=4, column=0, sticky="w")
        self.position_var = tk.StringVar()
        self.position_entry = tk.Entry(self.search_frame, textvariable=self.position_var)
        self.position_entry.grid(row=4, column=1, sticky="w")

        self.risk_search_label = tk.Label(self.search_frame, text="Факторы риска\n(через запятую):")
        self.risk_search_label.grid(row=0, column=2, padx=10, pady=3, sticky="w")
        self.risk_search_entry = tk.Text(self.search_frame, height=5)
        self.risk_search_entry.grid(row=0, column=3, columnspan=2, sticky="w")

        tk.Label(self.search_frame, text="Планируемая дата:").grid(row=2, column=2, sticky="w", padx=10, pady=3)
        self.planned_date_var = tk.StringVar()
        self.planned_date_cal = DateEntry(self.search_frame, date_pattern="dd.MM.yyyy",
                                          textvariable=self.planned_date_var)
        self.planned_date_cal.grid(row=2, column=3, sticky="w")
        self.planned_date_cal.set_date(self.current_date)
        self.planned_date_cal.delete(0, tk.END)  # очищаем строку

        tk.Label(self.search_frame, text="Фактическая дата:").grid(row=3, column=2, sticky="w", padx=10, pady=3)
        self.actual_date_var = tk.StringVar()
        self.actual_date_cal = DateEntry(self.search_frame, date_pattern="dd.MM.yyyy",
                                         textvariable=self.actual_date_var)
        self.actual_date_cal.grid(row=3, column=3, sticky="w")
        self.actual_date_cal.set_date(self.current_date)
        self.actual_date_cal.delete(0, tk.END)  # очищаем строку

        # # Поля для сотрудника
        # tk.Label(self.search_frame, text="Фамилия:").pack(anchor="w")
        # self.last_name_entry = tk.Entry(self.search_frame, textvariable=self.last_name_var)
        # self.last_name_entry.pack(fill="x", anchor="w")

        # tk.Label(self.search_frame, text="Имя:").pack(anchor="w")
        # self.first_name_entry = tk.Entry(self.search_frame, textvariable=self.first_name_var)
        # self.first_name_entry.pack(fill="x", anchor="w")
        #
        # tk.Label(self.search_frame, text="Отчество:").pack(anchor="w")
        # self.middle_name_entry = tk.Entry(self.search_frame, textvariable=self.middle_name_var)
        # self.middle_name_entry.pack(fill="x", anchor="w")
        #
        # tk.Label(self.search_frame, text="Дата рождения:").pack(anchor="w")
        # self.birth_date_cal = DateEntry(self.search_frame, date_pattern="dd.MM.yyyy", textvariable=self.birth_date_var)
        # self.birth_date_cal.pack(fill="x", anchor="w")
        # self.birth_date_cal.delete(0, tk.END) # очищаем строку
        #
        # tk.Label(self.search_frame, text="Должность:").pack(anchor="w")
        # self.position_entry = tk.Entry(self.search_frame, textvariable=self.position_var)
        # self.position_entry.pack(fill="x", anchor="w")
        #
        # self.risk_search_label = tk.Label(self.search_frame, text="Факторы риска (через запятую):")
        # self.risk_search_label.pack(padx=10, pady=5, anchor="w")
        # self.risk_search_entry = tk.Entry(self.search_frame)
        # self.risk_search_entry.pack(fill="x", padx=10, pady=5)
        #
        # tk.Label(self.search_frame, text="Планируемая дата:").pack()
        # self.planned_date_cal = DateEntry(self.search_frame, date_pattern="dd.MM.yyyy", textvariable=self.planned_date_var)
        # self.planned_date_cal.pack()
        # self.planned_date_cal.set_date(self.current_date)
        # self.planned_date_cal.delete(0, tk.END) # очищаем строку
        #
        # tk.Label(self.search_frame, text="Фактическая дата:").pack()
        # self.actual_date_cal = DateEntry(self.search_frame, date_pattern="dd.MM.yyyy", textvariable=self.actual_date_var)
        # self.actual_date_cal.pack()
        # self.actual_date_cal.set_date(self.current_date)
        # self.actual_date_cal.delete(0, tk.END) # очищаем строку

        # # Рамка для факторов риска и скроллбара
        # self.risk_frame = tk.Frame(self.root_search_window)
        # self.risk_frame.pack(side="right", padx=10, pady=10, fill="both", expand=True)
        #
        # # Канвас для прокрутки
        # self.risk_canvas = tk.Canvas(self.risk_frame)
        # self.risk_canvas.pack(side="top", fill="both", expand=True)
        #
        # # Скроллбар для канваса будет находиться внутри risk_canvas, иначе он почти не виден
        # self.risk_scrollbar = tk.Scrollbar(self.risk_canvas, command=self.risk_canvas.yview)
        # self.risk_scrollbar.pack(side="right", fill="y")
        #
        # self.risk_canvas.config(yscrollcommand=self.risk_scrollbar.set)
        # self.risk_canvas.bind("<Configure>",
        #                       lambda e: self.risk_canvas.configure(scrollregion=self.risk_canvas.bbox("all")))
        #
        # # Рамка для элементов рисков
        # self.risk_entries_frame = tk.Frame(self.risk_canvas)
        # self.risk_canvas.create_window((0, 0), window=self.risk_entries_frame, anchor="nw")

        # # Кнопки "Добавить риск", "Поиск" и "Отменить"
        # button_frame = tk.Frame(self.search_frame)
        # button_frame.pack(side="bottom", pady=10)
        # tk.Button(button_frame, text="Поиск", command=self.perform_search, bg="green").pack(side="left", padx=5)
        # tk.Button(button_frame, text="Отменить", command=self.cancel, bg="red").pack(side="right", padx=5)
        # tk.Button(button_frame, text="Очистить всё", command=self.clear_all).pack(side="left", padx=20, pady=5)
        button_frame = tk.Frame(self.search_frame)
        button_frame.grid(row=9, columnspan=4, pady=10)
        tk.Button(button_frame, text="Поиск", command=self.perform_search, bg="green").pack(side="left", padx=5)
        tk.Button(button_frame, text="Отменить", command=self.cancel, bg="red").pack(side="right", padx=5)
        tk.Button(button_frame, text="Очистить всё", command=self.clear_all).pack(side="left", padx=20, pady=5)

    # def add_risk_entry(self):
    #     tk.Label(self.risk_entries_frame, text="Фактор риска:").pack()
    #     risk_entry = tk.Entry(self.risk_entries_frame)
    #     risk_entry.pack()
    #     self.risk_entries.append((risk_entry, None, None))  # (Текстовое поле, Planned Date, Actual Date)
    #
    #     tk.Label(self.risk_entries_frame, text="Планируемая дата:").pack()
    #     planned_date_cal = DateEntry(self.risk_entries_frame, date_pattern="dd.MM.yyyy", textvariable=tk.StringVar())
    #     planned_date_cal.pack()
    #     planned_date_cal.set_date(self.current_date)
    #     self.risk_entries[-1] = (risk_entry, planned_date_cal, self.risk_entries[-1][2])
    #
    #     tk.Label(self.risk_entries_frame, text="Фактическая дата:").pack()
    #     actual_date_cal = DateEntry(self.risk_entries_frame, date_pattern="dd.MM.yyyy", textvariable=tk.StringVar())
    #     actual_date_cal.pack()
    #     actual_date_cal.set_date(self.current_date)
    #     self.risk_entries[-1] = (risk_entry, planned_date_cal, actual_date_cal)

    # def clear_risks(self):
    #     self.risk_entries_frame.destroy()
    #     self.risk_entries_frame = tk.Frame(self.risk_canvas)
    #     self.risk_canvas.create_window((0, 0), window=self.risk_entries_frame, anchor="nw")
    #
    #     self.risk_entries = []

    def clear_all(self):
        self.last_name_entry.delete(0, tk.END)
        self.first_name_entry.delete(0, tk.END)
        self.middle_name_entry.delete(0, tk.END)
        self.birth_date_cal.delete(0, tk.END) # очищаем строку
        self.position_entry.delete(0, tk.END)
        self.risk_search_entry.delete("1.0", "end")
        self.planned_date_cal.delete(0, tk.END) # очищаем строку
        self.actual_date_cal.delete(0, tk.END) # очищаем строку

    def cancel(self):
        if messagebox.askyesno("Отмена", "Закрыть форму поиска?", parent=self.root_search_window):
            self.root_search_window.destroy()

    def perform_search(self):
        last_name = self.last_name_var.get()
        first_name = self.first_name_var.get()
        middle_name = self.middle_name_var.get()
        birth_date = self.birth_date_var.get()
        position = self.position_var.get()
        planned_date = self.planned_date_var.get()
        actual_date = self.actual_date_var.get()
        risk_factors = [x.strip() for x in self.risk_search_entry.get("1.0", "end-1c").split(",")]

        print(last_name, first_name, middle_name, birth_date, position, risk_factors, planned_date, actual_date)
        print(not any([last_name, first_name, middle_name, birth_date, position, risk_factors, planned_date, actual_date]) or risk_factors == [''])
        if not any([last_name, first_name, middle_name, birth_date, position, planned_date, actual_date]) and risk_factors == ['']:
            messagebox.showerror("Ошибка", "Хотя бы одно поле должно быть заполнено", parent=self.root_search_window)
            return

        conn = sqlite3.connect("employee.db")
        cursor = conn.cursor()

        query = '''
                SELECT e.last_name, e.first_name, e.middle_name, e.birth_date, e.position, 
                    r.risk_name, r.planned_date, r.actual_date
                FROM employee e
                LEFT JOIN risk_factor r ON e.id = r.employee_id
                WHERE (e.last_name LIKE ? OR ? = '') AND
                  (e.first_name LIKE ? OR ? = '') AND
                  (e.middle_name LIKE ? OR ? = '') AND
                  (e.birth_date = ? OR ? = '') AND
                  (e.position LIKE ? OR ? = '') AND
                  (r.planned_date = ? OR ? = '') AND
                  (r.actual_date = ? OR ? = '') AND
                  (r.risk_name IN ({seq}) OR ? = '')
        '''.format(seq=','.join(['?']*len(risk_factors)))
        search_params = ['%' + last_name + '%', last_name,
                         '%' + first_name + '%', first_name,
                         '%' + middle_name + '%', middle_name,
                         birth_date, birth_date,
                         '%' + position + '%', position,
                         planned_date, planned_date,
                         actual_date, actual_date] + risk_factors + [','.join(risk_factors)]
        cursor.execute(query, search_params)
        rows = cursor.fetchall()

        conn.close()

        search_results = self.organize_search_results(rows)

        self.show_results(search_results)

    def organize_search_results(self, rows):
        search_results = []
        for row in rows:
            result = {
                "last_name": row[0],
                "first_name": row[1],
                "middle_name": row[2],
                "birth_date": row[3],
                "position": row[4],
                "risks": []
            }

            if row[5]:
                risk = {
                    "risk": row[5],
                    "planned_date": row[6],
                    "actual_date": row[7]
                }
                result["risks"].append(risk)

            found = False
            for search_result in search_results:
                if (search_result["last_name"] == result["last_name"] and
                        search_result["first_name"] == result["first_name"] and
                        search_result["middle_name"] == result["middle_name"]):
                    found = True
                    if row[5]:
                        risk = {
                            "risk": row[5],
                            "planned_date": row[6],
                            "actual_date": row[7]
                        }
                        search_result["risks"].append(risk)
                    break

            if not found:
                search_results.append(result)

        return search_results

    def show_results(self, results):
        print(results)
        pass
    #     self.clear_main_frame()
    #
    #     for result in results:
    #         employee_frame = tk.Frame(self.main_frame)
    #         employee_frame.pack(fill="x", padx=10, pady=5)
    #
    #         # ... (создание меток и иконок аналогично форме добавления пользователя)
    #
    #         tk.Button(employee_frame, image=edit_icon, command=lambda r=result: self.edit_employee(r)).pack(
    #             side="right")
    #         tk.Button(employee_frame, image=delete_icon, command=lambda r=result: self.delete_employee(r)).pack(
    #             side="right")
    #
    # def clear_main_frame(self):
    #     for widget in self.main_frame.winfo_children():
    #         widget.destroy()


class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Меню приложения")

        self.new_width = root.winfo_screenwidth() // 2  # Получение половины ширины экрана
        self.new_height = root.winfo_screenheight() // 2  # Получение половины высоты экрана
        self.root.geometry(f"{self.new_width}x{self.new_height}")  # Установка новых размеров

        # Создание меню
        menu_bar = tk.Menu(self.root)

        # Добавление пунктов в меню
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Добавление пользователя", command=self.open_add_user_window)
        file_menu.add_command(label="Поиск", command=self.open_search_window)
        file_menu.add_command(label="Обновить", command=self.open_update_window)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.exit_app)
        menu_bar.add_cascade(label="Меню", menu=file_menu)

        self.root.config(menu=menu_bar)


    def open_add_user_window(self):
        add_user_window = tk.Toplevel(self.root)
        add_user_window.title("Добавление пользователя")
        add_user_window.geometry(f"{self.new_width}x{self.new_height}")
        AddEmployeeApp(add_user_window)

    def open_search_window(self):
        search_window = tk.Toplevel(root)
        search_window.title("Поиск")
        search_window.geometry(f"{self.new_width}x{self.new_height}")  # Используем новые размеры
        SearchEmployeeApp(self.root, search_window)


    def open_update_window(self):
        update_window = tk.Toplevel(root)
        update_window.title("Обновить")
        update_window.geometry(f"{self.new_width}x{self.new_height}")

    def exit_app(self):
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainMenu(root)
    root.mainloop()

