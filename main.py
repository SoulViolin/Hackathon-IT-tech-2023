# pip install pyTelegramBotAPI
# pip install cryptography
from settings import *
import telebot
from telebot import types
from cryptography.fernet import Fernet
from contextlib import closing
import sqlite3
import json

bot = telebot.TeleBot(token, parse_mode=None)
_last_msg_id = None
_last_msg_text = None
_current_page = 0

def DBMS_Connection(query, values=''):
    conn = sqlite3.connect('TechnicalSchool.db')
    cur = conn.cursor()

    cur.execute(query, values)
    result = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return result

def get_admin_credentials():
    # загрузим ключ для дешифровки данных
    cipher_suite = Fernet(key)

    # загружаем и дешифруем данные
    decrypted_text = cipher_suite.decrypt(encrypted_data)

    # преобразуем данные из bytes в Python dict и возвращаем
    return json.loads(decrypted_text.decode())

# Создание таблицы users
DBMS_Connection('''
          CREATE TABLE IF NOT EXISTS users
          (id INTEGER PRIMARY KEY, 
           chat_id TEXT, 
           login TEXT UNIQUE, 
           password TEXT, 
           role TEXT)
          ''')

# Создание таблицы student_info
DBMS_Connection('''
          CREATE TABLE IF NOT EXISTS student_info
          (login TEXT PRIMARY KEY, 
           first_name TEXT, 
           last_name TEXT,
           course INTEGER, 
           grade TEXT, 
           debts TEXT, 
           FOREIGN KEY (login) REFERENCES users (login))
          ''')

# Создание таблицы teacher_info
DBMS_Connection('''
          CREATE TABLE IF NOT EXISTS teacher_info
          (login TEXT PRIMARY KEY, 
           first_name TEXT, 
           last_name TEXT,
           patronymic TEXT, 
           lesson TEXT, 
           office TEXT, 
           number Text,
           FOREIGN KEY (login) REFERENCES users (login))
          ''')

# Объединенная функция регистрации и авторизации
def process_reg_log(message, mode):
    login = message.text
    user_exist = DBMS_Connection('SELECT * FROM users WHERE login = ?', (login,)) is not None
    
    if user_exist and mode == 'reg':
        bot.send_message(message.chat.id, f'Пользователь с логином {login} уже существует')
    elif not user_exist and mode == 'log':
        bot.send_message(message.chat.id, f'Пользователя с таким логином {login} не существует')
    else:
        bot.send_message(message.chat.id, "Введите пароль:")
        bot.register_next_step_handler(message, process_role_password, login, mode)

def process_role_password(message, login, mode):
    if mode == 'reg':
        password = message.text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button1 = types.KeyboardButton('Студент')
        button2 = types.KeyboardButton('Преподаватель')
        button3 = types.KeyboardButton('Администратор')

        markup.row(button1)
        markup.row(button2)
        markup.row(button3)

        msg = bot.send_message(message.chat.id, "Выберите роль:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_password, login, password, mode)
    elif mode == 'log':
        password = message.text
        stored_password = DBMS_Connection("SELECT password FROM users WHERE login = ?", (login,))[0]

        if stored_password == password:
            update_session_and_notify(message.chat.id, login)
            start_handler(message)
        else:
            bot.send_message(message.chat.id, "Невёрный пароль")

def get_admin_credentials():
    # загрузим ключ для дешифровки данных
    cipher_suite = Fernet(key)

    # загружаем и дешифруем данные
    decrypted_text = cipher_suite.decrypt(encrypted_data)

    # преобразуем данные из bytes в Python dict и возвращаем
    return json.loads(decrypted_text.decode())

def process_password(message, login, password, mode):
    role = message.text

    admin_credentials = get_admin_credentials()

    if role == 'Администратор' and login == admin_credentials["login"] and password == admin_credentials["password"]:
        DBMS_Connection("INSERT INTO users (chat_id, login, password, role) VALUES (?, ?, ?, ?)",
                        (message.chat.id, login, password, 'admin')
                        )
        bot.send_message(message.chat.id, f"Вы были зарегистрированы как администратор")
    elif role == 'Преподаватель':
        DBMS_Connection("INSERT INTO users (chat_id, login, password, role) VALUES (?, ?, ?, ?)",
                        (message.chat.id, login, password, 'teacher')
                        )
        bot.send_message(message.chat.id, f"Вы были зарегистрированы как преподаватель")
    else:
        DBMS_Connection("INSERT INTO users (chat_id, login, password, role) VALUES (?, ?, ?, ?)",
                        (message.chat.id, login, password, 'student')
                        )
        bot.send_message(message.chat.id, f"Вы были зарегистрированы как студент")
    start_handler(message)

# Проверяет, авторизован ли пользователь, и возвращает его login и role, если он авторизован 
def check_auth(chat_id):
    result = DBMS_Connection('SELECT login, role FROM users WHERE chat_id = ?', (chat_id,))
    return result if result else (None, None)

# Функция для обновления информации о сессии и отправки уведомления при необходимости
def update_session_and_notify(chat_id, login):
    old_chat_id = DBMS_Connection("SELECT chat_id FROM users WHERE login = ?", (login,))[0]

    if old_chat_id and old_chat_id != chat_id:
        bot.send_message(old_chat_id, f"Выполнен вход в ваш аккаунт с другого устройства.")

    DBMS_Connection("UPDATE users SET chat_id = ? WHERE login = ?", (chat_id, login))

# Функция для разлогинивания пользователя.
def logout(chat_id):
    DBMS_Connection('UPDATE users SET chat_id = NULL WHERE chat_id = ?', (chat_id,))
    
# Определение клавиатур
def get_student_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    button1 = types.KeyboardButton('Расписание')
    button2 = types.KeyboardButton('Учебный план')
    button3 = types.KeyboardButton('Контактные данные')
    button4 = types.KeyboardButton('Материалы')
    button5 = types.KeyboardButton('Информация об отделениях')
    button6 = types.KeyboardButton('Заявления')
    button7 = types.KeyboardButton('Выход', )

    # Добавление кнопок на клавиатуру
    markup.row(button1, button2)
    markup.row(button3)
    markup.row(button4, button5, button6)
    markup.row(button7)

    return markup

def get_teacher_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    button1 = types.KeyboardButton('Расписание')
    button2 = types.KeyboardButton('Заявления')
    button3 = types.KeyboardButton('Материалы')
    button4 = types.KeyboardButton('Контактные данные')
    button5 = types.KeyboardButton('Выход', )

    # Добавление кнопок на клавиатуру
    markup.row(button1, button2)
    markup.row(button3)
    markup.row(button4)
    markup.row(button5)

    return markup

def get_admin_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Просмотр данных')
    button2 = types.KeyboardButton('Создание данных')
    button3 = types.KeyboardButton('Обновление данных')
    button4 = types.KeyboardButton('Удаление данных')
    button5 = types.KeyboardButton('Выход')

    markup.row(button1, button3)
    markup.row(button2,button4)
    markup.row(button5)

    return markup

def get_unauthorized_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Авторизация')
    button2 = types.KeyboardButton('Регистрация')

    # Добавление кнопок на клавиатуру
    markup.add(button1, button2)

    return markup

# =========================
# Обработка команды start
@bot.message_handler(commands=['start'])
def start_handler(message):
    login, role = check_auth(message.chat.id)

    if login:
        if role == 'student':
            bot.send_message(message.chat.id, f"Здравствуйте, {login}. Вы вошли как студент.", reply_markup=get_student_keyboard())
        elif role == 'teacher':
            bot.send_message(message.chat.id, f"Здравствуйте, {login}. Вы вошли как преподаватель.", reply_markup=get_teacher_keyboard())
        elif role == 'admin':
            bot.send_message(message.chat.id, f"Здравствуйте, {login}. Вы вошли как администратор.", reply_markup=get_admin_keyboard())
    else:
        bot.send_message(message.chat.id, "Здравствуйте\nЕсли у Вас уже есть аккаунт, введите <b>Авторизация</b>. \nЕсли нет - <b>Регистрация</b>", parse_mode="HTML", reply_markup=get_unauthorized_keyboard())

# =========================
# Права администратора
def admin_CRUD_operations(table_name, operation, values=None, condition=None):
    conn = sqlite3.connect('TechnicalSchool.db')
    cur = conn.cursor()

    if operation == 'create':
        query = f"INSERT INTO {table_name} VALUES ({', '.join('?' * len(values))})"
        cur.execute(query, values)
        
    elif operation == 'read':
        query = f"SELECT * FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        cur.execute(query)
        result = cur.fetchall()
        conn.close()
        return result
    
    elif operation == 'update':
        set_values = ', '.join([f'{key} = ?' for key in values.keys()])
        query = f"UPDATE {table_name} SET {set_values} WHERE {condition}"
        cur.execute(query, list(values.values()))
        
    elif operation == 'delete':
        query = f"DELETE FROM {table_name} WHERE {condition}"
        cur.execute(query)
    
    conn.commit()
    cur.close()
    conn.close()

@bot.message_handler(func=lambda message: message.text == "Просмотр данных")
def handle_view_data_button(message):
    msg = bot.reply_to(message, "Введите имя таблицы:")
    bot.register_next_step_handler(msg, view_data)

def view_data(message):
    table_name = message.text
    result = admin_CRUD_operations(table_name, "read")
    bot.send_message(message.chat.id, str(result))

@bot.message_handler(func=lambda message: message.text == "Создание данных")
def handle_create_data_button(message):
    bot.send_message(message.chat.id, "Введите имя таблицы")
    bot.register_next_step_handler(message, ask_data_for_create)

def ask_data_for_create(message):
    table_name = message.text
    bot.send_message(message.chat.id, "Введите данные в формате JSON")
    bot.register_next_step_handler(message, lambda msg: create_data(msg, table_name))

def create_data(message, table_name):
    data = json.loads(message.text)
    admin_CRUD_operations(table_name, "create", values=data)

@bot.message_handler(func=lambda message: message.text == "Обновление данных")
def handle_update_data_button(message):
    bot.send_message(message.chat.id, "Введите имя таблицы")
    bot.register_next_step_handler(message, ask_data_for_update)

def ask_data_for_update(message):
    table_name = message.text
    bot.send_message(message.chat.id, "Введите данные и условие в формате JSON {'values': {...}, 'condition': '...'}")
    bot.register_next_step_handler(message, lambda msg: update_data(msg, table_name))

def update_data(message, table_name):
    data = json.loads(message.text)
    admin_CRUD_operations(table_name, "update", values=data["values"], condition=data["condition"])

@bot.message_handler(func=lambda message: message.text == "Удаление данных")
def handle_delete_data_button(message):

    bot.send_message(message.chat.id, "Введите имя таблицы")
    bot.register_next_step_handler(message, ask_condition_for_delete)

def ask_condition_for_delete(message):
    table_name = message.text
    bot.send_message(message.chat.id, "Введите условие для удаления (при необходимости)")
    bot.register_next_step_handler(message, lambda msg: delete_data(msg, table_name))

def delete_data(message, table_name):
    condition = message.text if message.text.strip() != "" else None
    admin_CRUD_operations(table_name, "delete", condition=condition)

# =========================
# Обработчик для кнопки с текстом "Выход"
@bot.message_handler(func=lambda message: message.text == "Выход")
def handle_logout_button(message):
    logout(message.chat.id)
    start_handler(message)
    bot.send_message(message.chat.id, "Вы успешно вышли из аккаунта.")

# =========================
# Обработчик для кнопки с текстом "Авторизация"
@bot.message_handler(func=lambda message: message.text in ["Авторизация", "Регистрация"])
def reg_log_handler(message):
    mode = 'reg' if message.text == 'Регистрация' else 'log'
    
    bot.send_message(message.chat.id, "Введите логин:")
    bot.register_next_step_handler(message, process_reg_log, mode)

# =============================================================================
# Обработчик для кнопки с текстом "Контактные данные"
def get_db_connection():
    return sqlite3.connect('TechnicalSchool.db')

def get_all_teachers(conn):
    cur = conn.cursor()
    cur.execute('SELECT first_name, last_name, patronymic FROM teacher_info')
    teachers = [f"{t[0]} {t[1]} {t[2]}" for t in cur.fetchall()]
    cur.close()
    return teachers

def get_teacher_info(conn, teacher_name):
    cur = conn.cursor()
    first_name, last_name, patronymic = teacher_name.split(' ')
    cur.execute('SELECT * FROM teacher_info WHERE first_name = ? AND last_name = ? AND patronymic = ?',
                (first_name, last_name, patronymic))
    teacher_info = cur.fetchone()
    cur.close()
    return teacher_info

def get_teacher_pages(teachers, teachers_per_page=3):
    return [teachers[i:i+teachers_per_page] for i in range(0, len(teachers), teachers_per_page)]

def show_teacher_info(conn, message, teacher_name):
    global _last_msg_id, _last_msg_text
    teacher_info = get_teacher_info(conn, teacher_name)
    new_text = f"{teacher_name}:\n {teacher_info}"
    if _last_msg_text != new_text:
        if _last_msg_id is not None:
            bot.edit_message_text(chat_id=message.chat.id, message_id=_last_msg_id, text=new_text)
            _last_msg_text = new_text
        else:
            sent_msg = bot.send_message(message.chat.id, new_text)
            _last_msg_id = sent_msg.message_id
            _last_msg_text = new_text

def create_teacher_buttons(page, pages_count):
    keyboard = types.InlineKeyboardMarkup()
    for teacher in page:
        keyboard.add(types.InlineKeyboardButton(text=teacher, callback_data=f"info:{teacher}"))
    keyboard.add(
        types.InlineKeyboardButton(text="<<", callback_data="prev") if _current_page != 0 else types.InlineKeyboardButton(text=" ", callback_data="none"),
        types.InlineKeyboardButton(text=">", callback_data="next") if _current_page != pages_count - 1  else types.InlineKeyboardButton(text=" ", callback_data="none")
    )
    return keyboard

def send_teachers(message):
    global _current_page
    conn = get_db_connection()

    all_teachers = get_all_teachers(conn)
    teacher_pages = get_teacher_pages(all_teachers)

    if not teacher_pages:  # добавьте эту проверку
        bot.send_message(message.chat.id, "Преподаватели отсутствуют.")
        return

    if _current_page < 0: _current_page = 0
    if _current_page >= len(teacher_pages): _current_page = len(teacher_pages) - 1

    pages_count = len(teacher_pages)
    bot.send_message(message.chat.id, "Вот список преподавателей:", reply_markup=create_teacher_buttons(teacher_pages[_current_page], pages_count))

def edit_teachers(message):
    global _current_page
    conn = get_db_connection()

    all_teachers = get_all_teachers(conn)
    teacher_pages = get_teacher_pages(all_teachers)

    if not teacher_pages:  # add this check
        bot.edit_message_text("Преподаватели отсутствуют.", chat_id=message.chat.id, message_id=message.message_id)
        return

    if _current_page < 0: _current_page = 0
    if _current_page >= len(teacher_pages): _current_page = len(teacher_pages) - 1

    pages_count = len(teacher_pages)
    bot.edit_message_text("Вот список преподавателей:", chat_id=message.chat.id, message_id=message.message_id, reply_markup=create_teacher_buttons(teacher_pages[_current_page], pages_count))

@bot.message_handler(func=lambda message: message.text == "Контактные данные")
def handle_contact_details(message):
    global _current_page
    _current_page = 0 
    send_teachers(message)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    global _current_page, _last_msg_id
    conn = get_db_connection()

    if call.data.startswith('info:'):
        # _last_msg_id = None
        teacher_name = call.data.split(':', 1)[1]
        show_teacher_info(conn, call.message, teacher_name)
    elif call.data == 'next':
        _current_page += 1
        edit_teachers(call.message)
    elif call.data == 'prev':
        _current_page -= 1
        edit_teachers(call.message)

# =========================

bot.polling(none_stop=True)