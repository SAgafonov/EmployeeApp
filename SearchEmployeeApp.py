import tkinter as tk
from tkinter import messagebox
import sqlite3
from tkcalendar import DateEntry
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


class SearchEmployeeApp(FormElements):
    def __init__(self, main_frame, search_window):
        super().__init__()
        self.main_frame = main_frame
        self.root_search_window = search_window
        self.root_search_window.title("Поиск")

        self.risk_entries = []  # Список для хранения текстовых полей для факторов риска

        self.employees = []

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

