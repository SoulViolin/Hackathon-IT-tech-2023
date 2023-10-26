# pip install pyTelegramBotAPI
# pip install cryptography
from settings import *
import telebot
from telebot import types
from cryptography.fernet import Fernet
import sqlite3
import json

bot = telebot.TeleBot(token, parse_mode=None)

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
    button3 = types.KeyboardButton('Материалы')
    button4 = types.KeyboardButton('Контакты')
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
    button4 = types.KeyboardButton('Контакты')
    button5 = types.KeyboardButton('Выход', )

    # Добавление кнопок на клавиатуру
    markup.row(button1, button2)
    markup.row(button3)
    markup.row(button4, button5)

    return markup

def get_admin_keyboard():
    markup = get_student_keyboard()
    return markup

def get_unauthorized_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('/login')
    button2 = types.KeyboardButton('/register')

    # Добавление кнопок на клавиатуру
    markup.row(button1, button2)

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
        bot.send_message(message.chat.id, "Здравствуйте\nЕсли у Вас уже есть аккаунт, введите /login. \nЕсли нет - /register", reply_markup=get_unauthorized_keyboard())

# =========================
# Обработка команд регистрация и авторизация
@bot.message_handler(commands=['register', 'login'])
def reg_log_handler(message):
    mode = 'reg' if message.text == '/register' else 'log'
    
    bot.send_message(message.chat.id, "Введите логин:")
    bot.register_next_step_handler(message, process_reg_log, mode)

# =========================
# Обработка команды logout
@bot.message_handler(commands=['logout'])
def logout_handler(message):
    logout(message.chat.id)
    start_handler(message)
    bot.send_message(message.chat.id, "Вы успешно вышли из аккаунта.")


bot.polling(none_stop=True)