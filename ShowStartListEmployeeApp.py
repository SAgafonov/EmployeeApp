import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import sqlite3
from tkcalendar import DateEntry
from FormElements import FormElements
from PIL import Image, ImageTk
from datetime import datetime
from ScrollableFrame import ScrollableFrame
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


class ShowStartListEmployeeApp(FormElements):
    def __init__(self, main_window):
        super().__init__()
        self.edit_icon = "icons/edit_icon.png"
        self.delete_icon = "icons/delete_icon.png"
        # self.main_frame = tk.Frame(main_window)
        self.main_frame = main_window

        self.risk_entries = []  # Список для хранения текстовых полей для факторов риска

        self.employees = []

        self.select_query = None
        self.search_params = None

        # show_all_employees()

        self.perform_search()

    def get_employee_data(self, employee_id):
        conn = sqlite3.connect("employee.db")
        cursor = conn.cursor()

        # Выбираем только записи, для которых планируемая дата риска сегодня или +7 дней
        self.select_query = '''
                        SELECT e.id, e.last_name, e.first_name, e.middle_name, e.birth_date, e.position, r.id, r.risk_name, r.planned_date, r.actual_date
                        FROM employee AS e
                        LEFT JOIN risk_factor AS r ON e.id = r.employee_id
                        WHERE 
                            e.id = ? AND
                            (r.planned_date = DATE('now')
                            OR r.planned_date BETWEEN DATE('now') AND DATE('now', '+7 days'))
                        ORDER BY r.planned_date ASC;
                '''
        search_params = [employee_id]
        cursor.execute(self.select_query, search_params)
        rows = cursor.fetchall()

        conn.close()
        search_results = self.organize_search_results(rows)
        return search_results[0]

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

            # search_results = self.organize_search_results(rows)

            self.show_results(rows)
            return

        conn = sqlite3.connect("employee.db")
        cursor = conn.cursor()
        
        # Выбираем только записи, для которых планируемая дата риска сегодня или +7 дней
        self.select_query = '''
                SELECT e.id, e.last_name, e.first_name, e.middle_name, e.birth_date, e.position, r.id, r.risk_name, r.planned_date, r.actual_date
                FROM employee AS e
                LEFT JOIN risk_factor AS r ON e.id = r.employee_id
                WHERE
                    r.planned_date = DATE('now')
                    OR r.planned_date BETWEEN DATE('now') AND DATE('now', '+7 days')
                ORDER BY r.planned_date ASC
                LIMIT 50;
        '''
        cursor.execute(self.select_query)
        rows = cursor.fetchall()

        conn.close()

        search_results = self.organize_search_results(rows)

        self.show_results(search_results)
        return search_results

    def organize_search_results(self, rows) -> list:
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
        # sorted_results = sorted(search_results, key=lambda x: min([risk.get("planned_date") for risk in x["risks"]]))

        return search_results

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
        employee_data = self.get_employee_data(employee_id)
        print(employee_data)

        # ToDo Move to a common function
        # Перевод из SQLite формата в %d.%m.%Y
        employee_data['birth_date'] = datetime.strptime(employee_data['birth_date'], '%Y-%m-%d')
        employee_data['birth_date'] = employee_data['birth_date'].strftime('%d.%m.%Y')

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
            print(risk['risk'])
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