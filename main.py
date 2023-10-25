# pip install pyTelegramBotAPI
from settings import *
import telebot
import sqlite3

bot = telebot.TeleBot(token, parse_mode=None)

def DBMS_Connection(query, values=''):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute(query, values)
    result = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return result

# Объединенная функция регистрации и авторизации
def RegAuth(message, mode):
    bot.send_message(message.chat.id, "Введите логин:")
    bot.register_next_step_handler(message, process_name_reg_auth, mode)

def process_name_reg_auth(message, mode):
    login = message.text
    result = DBMS_Connection('SELECT * FROM users WHERE username = ?', (login,))
    
    if mode == 'reg':    
        if result is not None:
            msg = bot.send_message(message.chat.id, f'Пользователь с логином {login} уже существует')
        else:
            bot.send_message(message.chat.id, "Введите пароль:")
            bot.register_next_step_handler(message, process_password_reg_auth, login, mode)
    elif mode == 'log':
        if result is None:
            msg = bot.send_message(message.chat.id, f'Пользователя с таким логином {login} не существует')
        else:
            bot.send_message(message.chat.id, "Введите пароль:")
            bot.register_next_step_handler(message, process_password_reg_auth, login, mode)

def process_password_reg_auth(message, login, mode):
    password = message.text

    if mode == 'reg':
        DBMS_Connection(f"""
            INSERT INTO users (chat_id, username, password, role) VALUES (?, ?, ?, ?)""",
            (message.chat.id, login, password, 'student')
            )
        bot.send_message(message.chat.id, "Вы успешно зарегистрированы")
    elif mode == 'log':
        stored_password = DBMS_Connection("SELECT password FROM users WHERE username = ?", (login,))[0]
        
        if stored_password == password:
            bot.send_message(message.chat.id, "Вы успешно авторизовались")
        else:
            bot.send_message(message.chat.id, "Неверный пароль")

DBMS_Connection("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        username TEXT,
        password TEXT,
        role TEXT
    )
""")

# =========================
@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, "Здравствуйте\nЕсли у Вас уже есть аккаунт, введите /login. \nЕсли нет - /register")

# =========================
# Обработка команды регестрации
@bot.message_handler(commands=['register'])
def register_handler(message):
    RegAuth(message, 'reg')

# =========================
# Обработка команды авторизации
@bot.message_handler(commands=['login'])
def login_handler(message):
    RegAuth(message, 'log')

# =========================

bot.polling(none_stop=True)