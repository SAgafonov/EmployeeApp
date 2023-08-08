import tkinter as tk
from tkinter import messagebox
import sqlite3

from tkcalendar import DateEntry
from PIL import Image, ImageTk

from AddEmployeeApp import AddEmployeeApp
from SearchEmployeeApp import SearchEmployeeApp


# class RiskFactor:
#     def __init__(self, planned_date=None, actual_date=None):
#         self.planned_date = planned_date
#         self.actual_date = actual_date

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

