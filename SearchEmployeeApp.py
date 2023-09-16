import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import sqlite3
from tkcalendar import DateEntry
from FormElements import FormElements
from PIL import Image, ImageTk
from ScrollableFrame import ScrollableFrame
from datetime import datetime
from EditEmployeeApp import EditEmployeeApp

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


class SearchEmployeeApp(FormElements):
    def __init__(self, main_frame, search_window):
        super().__init__()
        self.edit_icon = "icons/edit_icon.png"
        self.delete_icon = "icons/delete_icon.png"
        self.main_frame = main_frame
        self.root_search_window = search_window
        self.root_search_window.title("Поиск")

        self.risk_entries = []  # Список для хранения текстовых полей для факторов риска

        self.employees = []

        self.select_query = None
        self.search_params = None

        show_all_employees()

        self.create_search_widgets()

    def create_search_widgets(self):
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

        button_frame = tk.Frame(self.search_frame)
        button_frame.grid(row=9, columnspan=4, pady=10)
        tk.Button(button_frame, text="Поиск", command=self.perform_search, bg="green").pack(side="left", padx=5)
        tk.Button(button_frame, text="Отменить", command=self.cancel, bg="red").pack(side="right", padx=5)
        tk.Button(button_frame, text="Очистить всё", command=self.clear_all).pack(side="left", padx=20, pady=5)

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
        # Если есть сохраненные параметры для поиска, то пользуемся имя.
        # Нужно для корректной перерисовки результатов поиска после удаления/редактирования пользователя.
        if self.select_query and self.search_params:
            print(self.select_query)
            print(self.search_params)
            conn = sqlite3.connect("employee.db")
            cursor = conn.cursor()

            cursor.execute(self.select_query, self.search_params)
            rows = cursor.fetchall()

            conn.close()

            search_results = self.organize_search_results(rows)

            self.show_results(search_results)
            return

        last_name = self.last_name_var.get()
        first_name = self.first_name_var.get()
        middle_name = self.middle_name_var.get()
        birth_date = self.birth_date_var.get()
        position = self.position_var.get()
        planned_date = self.planned_date_var.get()
        actual_date = self.actual_date_var.get()
        risk_factors = [x.strip() for x in self.risk_search_entry.get("1.0", "end-1c").split(",")]

        # ToDo Move to a common function
        # Перевод поля даты в SQLite формат
        if birth_date:
            birth_date = datetime.strptime(birth_date, '%d.%m.%Y')
            birth_date = birth_date.strftime('%Y-%m-%d')
        if planned_date:
            planned_date = datetime.strptime(planned_date, '%d.%m.%Y')
            planned_date = planned_date.strftime('%Y-%m-%d')
        if actual_date:
            actual_date = datetime.strptime(actual_date, '%d.%m.%Y')
            actual_date = actual_date.strftime('%Y-%m-%d')

        # print(last_name, first_name, middle_name, birth_date, position, risk_factors, planned_date, actual_date)
        # print(not any([last_name, first_name, middle_name, birth_date, position, risk_factors, planned_date, actual_date]) or risk_factors == [''])
        if not any([last_name, first_name, middle_name, birth_date, position, planned_date, actual_date]) and risk_factors == ['']:
            messagebox.showerror("Ошибка", "Хотя бы одно поле должно быть заполнено", parent=self.root_search_window)
            return

        conn = sqlite3.connect("employee.db")
        cursor = conn.cursor()

        self.select_query = '''
                SELECT e.id, e.last_name, e.first_name, e.middle_name, e.birth_date, e.position, 
                    r.id, r.risk_name, r.planned_date, r.actual_date
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
        self.search_params = ['%' + last_name + '%', last_name,
                         '%' + first_name + '%', first_name,
                         '%' + middle_name + '%', middle_name,
                         birth_date, birth_date,
                         '%' + position + '%', position,
                         planned_date, planned_date,
                         actual_date, actual_date] + risk_factors + [','.join(risk_factors)]
        cursor.execute(self.select_query, self.search_params)
        rows = cursor.fetchall()

        conn.close()

        search_results = self.organize_search_results(rows)

        self.show_results(search_results)

    def organize_search_results(self, rows):
        search_results = []
        for row in rows:
            result = {
                "id" : row[0],
                "last_name": row[1],
                "first_name": row[2],
                "middle_name": row[3],
                "birth_date": row[4],
                "position": row[5],
                "risks": []
            }

            if row[6]:
                risk = {
                    "risk_id": row[6],
                    "risk": row[7],
                    "planned_date": row[8],
                    "actual_date": row[9]
                }
                result["risks"].append(risk)

            found = False
            for search_result in search_results:
                if (search_result["last_name"] == result["last_name"] and
                        search_result["first_name"] == result["first_name"] and
                        search_result["middle_name"] == result["middle_name"]):
                    found = True
                    if row[6]:
                        risk = {
                            "risk_id": row[6],
                            "risk": row[7],
                            "planned_date": row[8],
                            "actual_date": row[9]
                        }
                        search_result["risks"].append(risk)
                    break

            if not found:
                search_results.append(result)

        # Сортировка результатов по минимальной дате planned_date
        sorted_results = sorted(search_results, key=lambda x: min([risk.get("planned_date") for risk in x["risks"]]))

        return sorted_results

    def show_results(self, results):
        [print(result) for result in results]
        self.clear_main_frame()

        # text = ScrolledText(self.main_frame, state='disable')
        # text.pack(fill='both', expand=True)
        frame = ScrollableFrame(self.main_frame,
                                width=self.main_frame.winfo_screenwidth() // 2 - 25,
                                height=self.main_frame.winfo_screenheight() // 2 - 5)

        edit_icon = self.change_icon_size(self.edit_icon)
        delete_icon = self.change_icon_size(self.delete_icon)

        for row, result in enumerate(results):
            employee_frame = tk.Frame(frame.scrollable_frame)
            employee_frame.grid(row=row, column=0, columnspan=3, sticky="w", padx=10, pady=5)

            # ToDo Move to a common function
            # Перевод из SQLite формата в %d.%m.%Y
            result['birth_date'] = datetime.strptime(result['birth_date'], '%Y-%m-%d')
            result['birth_date'] = result['birth_date'].strftime('%d.%m.%Y')

            # Отображение информации о сотруднике (ФИО, дата рождения, должность)
            employee_info = f"{result['last_name']} {result['first_name']} {result['middle_name']}, " \
                            f"Дата рождения: {result['birth_date']}, Должность: {result['position']}"
            tk.Label(employee_frame, text=employee_info).grid(row=row, column=row, sticky="w")

            # Пустой прозрачный элемент для выравнивания
            tk.Label(employee_frame, text="", width=5).grid(row=row, column=row+1)

            # Кликабельная иконка для редактирования
            edit_button = tk.Label(employee_frame, image=edit_icon)
            edit_button.photo = edit_icon
            edit_button.grid(row=row, column=row+2, padx=5, sticky="e") # column +2, чтобы иконка показывалась в колонке рядом с надписью
            edit_button.bind("<Button-1>", lambda event, result=result: self.edit_employee(result))

            # Кликабельная иконка для удаления
            delete_button = tk.Label(employee_frame, image=delete_icon)
            delete_button.photo = delete_icon
            delete_button.grid(row=row, column=row+3, padx=5, sticky="e") # column +3, чтобы иконка показывалась в колонке рядом с иконкой редактирования
            delete_button.bind("<Button-1>", lambda event, result=result: self.delete_employee(result))

        frame.pack()

    # Изменение размера иконки редактирования
    def change_icon_size(self, icon: str):
        edit_image = Image.open(icon)
        edit_image = edit_image.resize((20, 20), Image.LANCZOS)
        edit_icon = ImageTk.PhotoImage(edit_image)
        return edit_icon

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget_name = widget.winfo_name()
            if widget_name != "!menu":
                widget.destroy()

    def edit_employee(self, employee_data):
        # Get employee ID
        employee_id = employee_data["id"]

        # Создаем новый экземпляр формы "Добавление пользователя"
        edit_form = tk.Toplevel(self.main_frame)
        edit_app = EditEmployeeApp(edit_form, employee_id)

        # Заполняем поля данными выбранного сотрудника
        edit_app.last_name_entry.insert(0, employee_data["last_name"])
        edit_app.first_name_entry.insert(0, employee_data["first_name"])
        edit_app.middle_name_entry.insert(0, employee_data["middle_name"])
        edit_app.birth_date_cal.set_date(employee_data["birth_date"])
        edit_app.position_entry.insert(0, employee_data["position"])

        # Заполняем риски
        for risk in employee_data["risks"]:
            # ToDo Move to a common function
            # Перевод из SQLite формата в %d.%m.%Y
            try:
                risk["planned_date"] = datetime.strptime(risk["planned_date"], '%Y-%m-%d')
                risk["planned_date"] = risk["planned_date"].strftime('%d.%m.%Y')

                risk["actual_date"] = datetime.strptime(risk["actual_date"], '%Y-%m-%d')
                risk["actual_date"] = risk["actual_date"].strftime('%d.%m.%Y')
            except ValueError:
                pass

            edit_app.edit_risk_entry(risk["risk_id"], risk["risk"], risk["planned_date"], risk["actual_date"])


    def delete_employee(self, employee_data):
        confirmed = messagebox.askokcancel(
            "Подтверждение удаления",
            "Данные по сотруднику будут удалены навсегда. Продолжить?",
            icon="warning"
        )
        print("Deleting-----------------------")
        print(employee_data)
        employee_id = employee_data["id"]
        if confirmed:
            # Удаление сотрудника и связанных рисков из базы данных
            conn = sqlite3.connect("employee.db")
            cursor = conn.cursor()

            # Удаление связанных рисков сотрудника
            cursor.execute("DELETE FROM risk_factor WHERE employee_id=?", (employee_id,))

            # Удаление самого сотрудника
            cursor.execute("DELETE FROM employee WHERE id=?", (employee_id,))

            conn.commit()
            conn.close()

            # Обновление отображения результатов
            self.perform_search()

