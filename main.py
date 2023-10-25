# pip install pyTelegramBotAPI
from settings import *
import telebot
import sqlite3

bot = telebot.TeleBot(token, parse_mode=None)

def DBMS_Connection(command, values=''):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute(command, values)
    result = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return result

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
    msg = bot.send_message(message.chat.id, "Здравствуйте")
    msg = bot.send_message(message.chat.id, "Если у Вас уже есть аккаунт, введите /login. \nЕсли нет - /register")

# =========================
@bot.message_handler(commands=['register'])
def register_handler(message):
    msg = bot.send_message(message.chat.id, "Введите логин")
    bot.register_next_step_handler(msg, process_username_step)

# Обработчик ввода логина
def process_username_step(message):
    try:
        username = message.text

        result = DBMS_Connection('SELECT * FROM users WHERE username = ?', (username))

        if result is not None:
            msg = bot.send_message(message.chat.id, f'Пользователь с логином {username} уже существует')
        else:
            # Запрашиваем пароль
            msg = bot.send_message(message.chat.id, "Введите пароль:")
            bot.register_next_step_handler(msg, process_password_step, username)
    except Exception as e:
        print(e)
        bot.reply_to(message, 'Ошибка, повторите попытку.')

# Обработчик ввода пароля
def process_password_step(message, username):
    try:
        password = message.text

    except Exception as e:
        bot.reply_to(message, 'Ошибка, повторите попытку.')
    try:
        DBMS_Connection(f"""
        INSERT INTO users (chat_id, username, password, role) VALUES (?, ?, ?, ?)""",
        (message.chat.id, username, password, 'student')
        )
        msg = bot.send_message(message.chat.id, "Вы успешно зарегистрированы")
    except Exception as e:
        bot.reply_to(message, 'Ошибка, повторите попытку.')
    
# =========================
@bot.message_handler(commands=['login'])
def login_handler(message):
    msg = bot.send_message(message.chat.id, "Введите логин")

bot.polling(none_stop=True)