from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, CallbackQueryHandler
import sqlite3
import datetime
import random

conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users 
             (user_id INTEGER PRIMARY KEY, username TEXT, points INTEGER DEFAULT 0)''')
conn.commit()
conn.close()

TASKS = [
    "Уменьшите свой углеродный след. Изучите, какие шаги вы можете предпринять, чтобы уменьшить свой вклад в глобальное потепление.",
    "Проведите день без использования пластиковых изделий. Запишите свои наблюдения и ощущения.",
    "Изучите причины глобального потепления и его последствия для окружающей среды и человечества.",
    "Посадите дерево или примите участие в акции по зеленому благоустройству вашего района.",
    "Соберите мусор в своем районе или на берегу реки. Проанализируйте количество и типы мусора.",
    "Сократите использование автомобиля. Изучите альтернативы: общественный транспорт, велосипед, пешие прогулки.",
    "Пересмотрите свою диету в сторону уменьшения потребления мяса и увеличения потребления растительных продуктов.",
    "Изучите возможности использования возобновляемых источников энергии в вашем регионе.",
    "Присоединитесь к общественной организации или инициативе, посвященной проблемам окружающей среды.",
    "Поддержите инициативы по защите и сохранению природных ресурсов вашего региона."
]

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Получить задание", callback_data='task')],
        [InlineKeyboardButton("Лидерборд", callback_data='leaderboard')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Привет! Я бот, который поможет тебе бороться с глобальным потеплением. "
                              "Каждый день я буду отправлять тебе задание, а за его выполнение ты получишь очки. "
                              "Нажми кнопку, чтобы начать.", reply_markup=reply_markup)

def get_task_text() -> str:
    return random.choice(TASKS)

def task(update: Update, context: CallbackContext) -> None:
    keyboard = [[InlineKeyboardButton("Выполнено", callback_data='complete')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Сегодняшнее задание:\n\n" + get_task_text(),
                              reply_markup=reply_markup)

def complete_task(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    if user:
        points = user[2] + random.randint(1, 10)  
        c.execute("UPDATE users SET points=? WHERE user_id=?", (points, user_id))
    else:
        username = update.message.from_user.username
        points = random.randint(1, 10)
        c.execute("INSERT INTO users (user_id, username, points) VALUES (?, ?, ?)", (user_id, username, points))
    conn.commit()
    conn.close()
    update.message.reply_text("Задание выполнено! Ты заработал {} очков.".format(points))

def leaderboard(update: Update, context: CallbackContext) -> None:
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users ORDER BY points DESC LIMIT 10")
    leaders = c.fetchall()
    conn.close()

    leaderboard_text = "🏆 Лидерборд:\n"
    for i, leader in enumerate(leaders, start=1):
        leaderboard_text += "{}. {} - {} очков\n".format(i, leader[1], leader[2])
    
    update.message.reply_text(leaderboard_text)

def main() -> None:
    updater = Updater("7080738841:AAF2UlhQXgk1oSUZWPNuQT6fgdbhRe8_c-0")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
