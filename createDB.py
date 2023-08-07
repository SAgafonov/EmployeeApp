import sqlite3

# Создание таблицы Employee
def create_employee_table():
    conn = sqlite3.connect("employee.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employee (
            id INTEGER PRIMARY KEY,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            middle_name TEXT,
            birth_date DATE,
            position TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Создание таблицы RiskFactor
def create_risk_factor_table():
    conn = sqlite3.connect("employee.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS risk_factor (
            id INTEGER PRIMARY KEY,
            employee_id INTEGER NOT NULL,
            risk_name TEXT NOT NULL,
            planned_date DATE,
            actual_date DATE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employee (id)
        )
    ''')
    conn.commit()
    conn.close()

# Удаление всех таблиц
def drop_tables():
    conn = sqlite3.connect("employee.db")
    cursor = conn.cursor()
    cursor.execute('''
        DROP TABLE employee;
        DROP TABLE risk_factor;
    ''')
    conn.commit()
    conn.close()

# Создание таблиц в базе данных
create_employee_table()
create_risk_factor_table()
