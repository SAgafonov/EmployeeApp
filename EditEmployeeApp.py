import tkinter as tk
from tkinter import messagebox
import sqlite3
from tkcalendar import DateEntry
from datetime import datetime
from PIL import Image, ImageTk
from FormElements import FormElements

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


class EditEmployeeApp(FormElements):
    def __init__(self, add_user_window, employee_id):
        super().__init__()
        self.employee_id = employee_id

        self.root_edit_user_window = add_user_window
        self.root_edit_user_window.title("Редактирование пользователя")
        self.delete_icon = "icons/delete_icon.png"

        self.risk_entries = []  # Список для хранения текстовых полей для факторов риска

        self.error_label = tk.Label(self.root_edit_user_window, text="", fg="red")
        self.error_label.pack()

        self.create_add_user_widgets()

    def create_add_user_widgets(self):
        self.employee_frame = tk.Frame(self.root_edit_user_window)
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
        self.risk_frame = tk.Frame(self.root_edit_user_window)
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
        tk.Button(button_frame, text="Добавить риск", command=self.edit_risk_entry).pack(side="left", padx=15)
        tk.Button(button_frame, text="Сохранить", command=self.edit_employee, bg="green").pack(side="left", padx=5)
        tk.Button(button_frame, text="Отменить", command=self.cancel, bg="red").pack(side="right", padx=5)
        tk.Button(button_frame, text="Очистить риски", command=self.clear_risks).pack(side="left", padx=20, pady=5)
        tk.Button(button_frame, text="Очистить всё", command=self.clear_all).pack(side="left", padx=20, pady=5)

    def edit_risk_entry(self, employee_id=None, risk_id=None, risk_name=None, risk_planned_date=None, risk_actual_date=None):
        risk_frame = tk.Frame(self.risk_entries_frame)
        risk_frame.pack()
        # Создаем лэйбл для названия поля
        tk.Label(risk_frame, text="Фактор риска:").pack()
        # Создаем Entry для поля ввода
        risk_entry = tk.Entry(risk_frame)

        # Кликабельная иконка для удаления
        delete_icon = self.change_icon_size(self.delete_icon)
        delete_button = tk.Label(risk_frame, image=delete_icon)
        delete_button.photo = delete_icon
        # ToDo Сделать, чтобы риск убирался с формы после нажатия на кнопку
        delete_button.bind("<Button-1>", lambda event, risk=risk_id, employee=employee_id: self.delete_risk(risk, employee))
        delete_button.pack(side="right")

        # Если передавалось имя риска, заполняем поле с названием (обычно при редактировании)
        if risk_name:
            risk_entry.insert(0, risk_name)

        risk_entry.pack()
        self.risk_entries.append((risk_id, risk_entry, None, None))  # (Текстовое поле, Planned Date, Actual Date)

        tk.Label(self.risk_entries_frame, text="Планируемая дата:").pack()
        planned_date_cal = DateEntry(self.risk_entries_frame, date_pattern="dd.MM.yyyy", textvariable=tk.StringVar())
        planned_date_cal.pack()
        if risk_planned_date:
            planned_date_cal.set_date(risk_planned_date)
        else:
            planned_date_cal.set_date(self.current_date)
        self.risk_entries[-1] = (risk_id, risk_entry, planned_date_cal, self.risk_entries[-1][2])

        tk.Label(self.risk_entries_frame, text="Фактическая дата:").pack()
        actual_date_cal = DateEntry(self.risk_entries_frame, date_pattern="dd.MM.yyyy", textvariable=tk.StringVar())
        actual_date_cal.pack()
        if risk_actual_date:
            actual_date_cal.set_date(risk_actual_date)
        else:
            actual_date_cal.set_date(self.current_date)
        self.risk_entries[-1] = (risk_id, risk_entry, planned_date_cal, actual_date_cal)

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

    def get_employee_info(self, employee_id):
        """
        Получить инфу по рискам юзера.
        :param employee_id:
        :return:
        """
        pass

    def edit_employee(self):
        if self.validate_fields():
            last_name = self.last_name_var.get()
            first_name = self.first_name_var.get()
            middle_name = self.middle_name_var.get()
            birth_date = self.birth_date_var.get()
            position = self.position_var.get()

            # ToDo Move to a common function
            # Перевод поля даты в SQLite формат
            birth_date = datetime.strptime(birth_date, '%d.%m.%Y')
            birth_date = birth_date.strftime('%Y-%m-%d')

            conn = sqlite3.connect("employee.db")
            cursor = conn.cursor()

            # Сохранение данных сотрудника
            cursor.execute('''
                            UPDATE employee 
                            SET last_name = ?, first_name= ?, middle_name= ?, birth_date= ?, position= ?
                            WHERE id = ?
                        ''', (last_name, first_name, middle_name, birth_date, position, self.employee_id))

            # self.employee = Employee(last_name, first_name, middle_name, birth_date, position)
            # for risk_entry, planned_date_entry, actual_date_entry in self.risk_entries:
            #     risk_name = risk_entry.get()
            #     planned_date = planned_date_entry.get()
            #     actual_date = actual_date_entry.get()
            #     if risk_name:
            #         self.employee.add_risk_factor(risk_name, planned_date, actual_date)

            # Сохранение факторов риска
            for risk_entry in self.risk_entries:
                risk_id = risk_entry[0]
                risk_name = risk_entry[1].get()
                planned_date = risk_entry[2].get()
                actual_date = risk_entry[3].get()

                print(risk_name)

                # ToDo Move to a common function
                # Перевод поля даты в SQLite формат
                try:
                    planned_date = datetime.strptime(planned_date, '%d.%m.%Y')
                    planned_date = planned_date.strftime('%Y-%m-%d')

                    actual_date = datetime.strptime(actual_date, '%d.%m.%Y')
                    actual_date = actual_date.strftime('%Y-%m-%d')
                except ValueError:
                    pass

                if risk_id:
                    cursor.execute('''
                                    UPDATE risk_factor 
                                    SET risk_name = ?, planned_date = ?, actual_date = ?
                                    WHERE id = ?
                                ''', (risk_name, planned_date, actual_date, risk_id))
                else:
                    cursor.execute('''
                                    INSERT INTO risk_factor (employee_id, risk_name, planned_date, actual_date)
                                    VALUES (?, ?, ?, ?)
                                ''', (self.employee_id, risk_name, planned_date, actual_date))

            conn.commit()
            conn.close()

            messagebox.showinfo("Информация", "Информация о сотруднике и рисках обновлена.", parent=self.root_edit_user_window)
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

        for risk_id, risk_entry, planned_date_cal, actual_date_cal in self.risk_entries:
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
        if messagebox.askyesno("Отмена", "Изменения не будут сохранены. Продолжить?", parent=self.root_edit_user_window):
            self.root_edit_user_window.destroy()

    def show_success_message(self, message: str):
        success_popup = tk.Toplevel(self.root_edit_user_window)
        success_popup.title("Успех")
        success_popup.geometry("200x100")
        tk.Label(success_popup, text=message).pack(pady=20)
        tk.Button(success_popup, text="Закрыть", command=success_popup.destroy).pack()

    def delete_risk(self, risk_id, employee_id):
        # ToDo
        # ToDo Вызвать get_employee_info(), если рисков 1, то выдавать предупреждение, что у юзера не может быть
        # ToDo меньше одного риска.
        confirmed = messagebox.askokcancel(
            "Подтверждение удаления",
            "Риск будет удален. Продолжить?",
            icon="warning",
            parent=self.root_edit_user_window
        )
        print("Deleting-----------------------")
        print(risk_id)
        if confirmed:
            # Удаление сотрудника и связанных рисков из базы данных
            conn = sqlite3.connect("employee.db")
            cursor = conn.cursor()

            # Удаление связанных рисков сотрудника
            cursor.execute("DELETE FROM risk_factor WHERE id=?", (risk_id,))

            conn.commit()
            conn.close()

    # Изменение размера иконки редактирования
    def change_icon_size(self, icon: str):
        edit_image = Image.open(icon)
        edit_image = edit_image.resize((20, 20), Image.LANCZOS)
        edit_icon = ImageTk.PhotoImage(edit_image)
        return edit_icon
