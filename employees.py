import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime
from tkcalendar import DateEntry

# Глобальные переменные для полей ввода
entry_full_name = None
entry_date_of_birth = None
entry_position = None
entry_planned_factors = None
entry_planned_dates = None
entry_actual_dates = None

def validate_date(date_str):
    try:
        datetime.strptime(date_str, '%d.%m.%Y')
        return True
    except ValueError:
        return False

def add_employee():
    global entry_full_name, entry_date_of_birth, entry_position, entry_planned_factors, entry_planned_dates, entry_actual_dates

    # Получаем значения из полей ввода
    full_name = entry_full_name.get()
    date_of_birth = entry_date_of_birth.get()
    position = entry_position.get()

    # Проверяем корректность ввода даты рождения
    if not validate_date(date_of_birth):
        messagebox.showerror("Error", "Invalid date format for Date of Birth. Please use the format: dd.mm.yyyy")
        return

    conn = sqlite3.connect("employees.db")
    cursor = conn.cursor()

    # Добавляем информацию о сотруднике в таблицу employees
    cursor.execute('INSERT INTO employees (full_name, date_of_birth, position) VALUES (?, ?, ?)', (full_name, date_of_birth, position))
    conn.commit()

    # Получаем id только что добавленного сотрудника
    cursor.execute('SELECT last_insert_rowid()')
    employee_id = cursor.fetchone()[0]

    # Добавляем информацию о планируемых факторах в таблицу planned_factors
    planned_factors = entry_planned_factors.get()
    planned_dates = entry_planned_dates.get()
    actual_dates = entry_actual_dates.get()

    # Разделяем планируемые факторы и даты на список, чтобы сохранить их отдельно
    planned_factors_list = planned_factors.split(',')
    planned_dates_list = planned_dates.split(',')
    actual_dates_list = actual_dates.split(',')

    for factor, planned_date, actual_date in zip(planned_factors_list, planned_dates_list, actual_dates_list):
        if not validate_date(planned_date) or (actual_date and not validate_date(actual_date)):
            messagebox.showerror("Error", "Invalid date format for Planned or Actual Dates. Please use the format: dd.mm.yyyy")
            conn.close()
            return

        cursor.execute('INSERT INTO planned_factors (employee_id, factor_name, planned_date, actual_date) VALUES (?, ?, ?, ?)', (employee_id, factor.strip(), planned_date, actual_date))

    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Employee added successfully.")


def update_employee():
    global entry_full_name, entry_date_of_birth, entry_position, entry_planned_factors, entry_planned_dates, entry_actual_dates

    # Получаем значения из полей ввода
    full_name = entry_full_name.get()
    date_of_birth = entry_date_of_birth.get()
    position = entry_position.get()

    # Проверяем корректность ввода даты рождения
    if not validate_date(date_of_birth):
        messagebox.showerror("Error", "Invalid date format for Date of Birth. Please use the format: dd.mm.yyyy")
        return

    conn = sqlite3.connect("employees.db")
    cursor = conn.cursor()

    # Обновляем информацию о сотруднике в таблице employees
    cursor.execute('UPDATE employees SET full_name=?, date_of_birth=?, position=? WHERE full_name=?', (full_name, date_of_birth, position, full_name))
    conn.commit()

    # Получаем id сотрудника
    cursor.execute('SELECT id FROM employees WHERE full_name=?', (full_name,))
    employee_id = cursor.fetchone()[0]

    # Обновляем информацию о планируемых факторах в таблице planned_factors
    planned_factors = entry_planned_factors.get()
    planned_dates = entry_planned_dates.get()
    actual_dates = entry_actual_dates.get()

    # Разделяем планируемые факторы и даты на список, чтобы сохранить их отдельно
    planned_factors_list = planned_factors.split(',')
    planned_dates_list = planned_dates.split(',')
    actual_dates_list = actual_dates.split(',')

    # Удаляем предыдущие данные о планируемых факторах для этого сотрудника
    cursor.execute('DELETE FROM planned_factors WHERE employee_id=?', (employee_id,))

    for factor, planned_date, actual_date in zip(planned_factors_list, planned_dates_list, actual_dates_list):
        if not validate_date(planned_date) or (actual_date and not validate_date(actual_date)):
            messagebox.showerror("Error", "Invalid date format for Planned or Actual Dates. Please use the format: dd.mm.yyyy")
            conn.close()
            return

        cursor.execute('INSERT INTO planned_factors (employee_id, factor_name, planned_date, actual_date) VALUES (?, ?, ?, ?)', (employee_id, factor.strip(), planned_date, actual_date))

    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Employee updated successfully.")


def delete_employee():
    global entry_full_name

    full_name = entry_full_name.get()

    conn = sqlite3.connect("employees.db")
    cursor = conn.cursor()
    cursor.execute('DELETE FROM employees WHERE full_name = ?', (full_name,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Employee deleted successfully.")

def check_planned_dates():
    current_date = datetime.today().strftime('%Y-%m-%d')

    conn = sqlite3.connect("employees.db")
    cursor = conn.cursor()
    cursor.execute('SELECT full_name, planned_factors, planned_dates FROM employees WHERE planned_dates = ?', (current_date,))
    rows = cursor.fetchall()
    conn.close()

    if rows:
        result = "List of employees with planned factors on {}: \n".format(current_date)
        for row in rows:
            result += f"Full Name: {row[0]}, Planned Factors: {row[1]}, Planned Date: {row[2]}\n"
        messagebox.showinfo("Planned Factors Today", result)
    else:
        messagebox.showinfo("Planned Factors Today", "No employees have planned factors for today.")

def main():
    global entry_full_name, entry_date_of_birth, entry_position, entry_planned_factors, entry_planned_dates, entry_actual_dates

    window = tk.Tk()
    window.title("Employee Management App")

    label_full_name = tk.Label(window, text="Full Name:")
    label_full_name.grid(row=0, column=0)
    entry_full_name = tk.Entry(window)
    entry_full_name.grid(row=0, column=1)

    entry_position = tk.Entry(window)
    entry_position.grid(row=2, column=1)

    entry_planned_factors = tk.Entry(window)
    entry_planned_factors.grid(row=3, column=1)

    label_date_of_birth = tk.Label(window, text="Date of Birth:")
    label_date_of_birth.grid(row=1, column=0)
    entry_date_of_birth = DateEntry(window, date_pattern='dd.mm.yyyy')
    entry_date_of_birth.grid(row=1, column=1)

    label_position = tk.Label(window, text="Position:")
    label_position.grid(row=2, column=0)
    entry_position = tk.Entry(window)
    entry_position.grid(row=2, column=1)

    label_planned_factors = tk.Label(window, text="Planned Factors:")
    label_planned_factors.grid(row=3, column=0)
    entry_planned_factors = tk.Entry(window)
    entry_planned_factors.grid(row=3, column=1)

    label_planned_dates = tk.Label(window, text="Planned Dates:")
    label_planned_dates.grid(row=4, column=0)
    entry_planned_dates = DateEntry(window, date_pattern='dd.mm.yyyy')
    entry_planned_dates.grid(row=4, column=1)

    label_actual_dates = tk.Label(window, text="Actual Dates:")
    label_actual_dates.grid(row=5, column=0)
    entry_actual_dates = DateEntry(window, date_pattern='dd.mm.yyyy')
    entry_actual_dates.grid(row=5, column=1)

    button_add = tk.Button(window, text="Add Employee", command=add_employee)
    button_add.grid(row=6, column=0)

    button_update = tk.Button(window, text="Update Employee", command=update_employee)
    button_update.grid(row=7, column=0)

    button_delete = tk.Button(window, text="Delete Employee", command=delete_employee)
    button_delete.grid(row=7, column=2)

    button_check_dates = tk.Button(window, text="Check Planned Dates", command=check_planned_dates)
    button_check_dates.grid(row=7, column=0, columnspan=3)

    window.mainloop()

if __name__ == "__main__":
    main()
