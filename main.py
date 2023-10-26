# pip install pyTelegramBotAPI
from settings import *
import telebot
from telebot import types
import sqlite3

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
        bot.register_next_step_handler(message, process_password, login, mode)

def process_password(message, login, mode):
    password = message.text

    if mode == 'reg':
        DBMS_Connection("INSERT INTO users (chat_id, login, password, role) VALUES (?, ?, ?, ?)",
                        (message.chat.id, login, password, 'student')
                        )
        bot.send_message(message.chat.id, "Вы успешно зарегистрированы")
    elif mode == 'log':
        stored_password = DBMS_Connection("SELECT password FROM users WHERE login = ?", (login,))[0]
        
        if stored_password == password:
            update_session_and_notify(message.chat.id, login)
            # DBMS_Connection("UPDATE users SET chat_id = ? WHERE login = ?", (message.chat.id, login))

            bot.send_message(message.chat.id, "Вы успешно авторизовались")
        else:
            bot.send_message(message.chat.id, "Неверный пароль")

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

# =========================
# Обработка команды start
@bot.message_handler(commands=['start'])
def start_handler(message):
    login, role = check_auth(message.chat.id)

    if login:
        if role == 'student':
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('Студенческая кнопка 1', 'Студенческая кнопка 2')
            bot.send_message(message.chat.id, f"Здравствуйте, {login}. Вы вошли как студент.", reply_markup=markup)
        elif role == 'teacher':
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('Учителю кнопка 1', 'Учителю кнопка 2')
            bot.send_message(message.chat.id, f"Здравствуйте, {login}. Вы вошли как преподаватель.", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Здравствуйте\nЕсли у Вас уже есть аккаунт, введите /login. \nЕсли нет - /register")

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
    bot.send_message(message.chat.id, "Вы успешно вышли из аккаунта.")


bot.polling(none_stop=True)