import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import pandas as pd
from random import randint
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Состояния разговора
NAME, EMAIL, CARD = range(3)

# Функция старта
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info("Запущена команда /start")
    keyboard = [[InlineKeyboardButton("Начать", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Добро пожаловать! Нажмите 'Начать' для регистрации.", reply_markup=reply_markup)
    return ConversationHandler.END

async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Пожалуйста, введите ваше имя и фамилию (например, Иван Иванов).")
    return NAME

# Функция получения имени и фамилии
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info("Получены имя и фамилия: %s", update.message.text)
    full_name = update.message.text.split()
    if len(full_name) < 2:
        await update.message.reply_text("Пожалуйста, введите ваше полное имя и фамилию (например, Иван Иванов).")
        return NAME
    context.user_data['firstname'] = full_name[0]
    context.user_data['lastname'] = full_name[1]
    await update.message.reply_text("Пожалуйста, введите ваш email.")
    return EMAIL

# Функция получения email
async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info("Получен email: %s", update.message.text)
    context.user_data['email'] = update.message.text
    # Записываем данные в Excel
    df = pd.DataFrame([context.user_data])
    try:
        with pd.ExcelWriter('users.xlsx', mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, index=False, header=writer.sheets['Sheet1'].max_row == 1)
    except FileNotFoundError:
        df.to_excel('users.xlsx', index=False)
    keyboard = [[InlineKeyboardButton("Создать карту", callback_data='create_card')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Спасибо за регистрацию! Нажмите "Создать карту", чтобы получить данные карты.', reply_markup=reply_markup)
    return CARD

# Функция создания карты
async def create_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    card_number = "".join([str(randint(0, 9)) for _ in range(16)])
    expiry_date = (datetime.now() + timedelta(days=365*3)).strftime("%m/%y")
    cvv = "".join([str(randint(0, 9)) for _ in range(3)])
    balance = f"{randint(0, 5000)}.00"
    card_info = (f"Номер карты: {card_number}\n"
                 f"Срок действия: {expiry_date}\n"
                 f"CVV: {cvv}\n"
                 f"Баланс: ${balance}")
    await query.edit_message_text(text=card_info)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Отмена регистрации.')
    return ConversationHandler.END

def main() -> None:
    try:
        application = Application.builder().token("7303534803:AAHaP8kCslxGbMn8GmH-3rwye1EXOJ0TwqA") \
                                 .get_updates_read_timeout(60) \
                                 .get_updates_write_timeout(60) \
                                 .get_updates_pool_timeout(60) \
                                 .build()

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
                EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            per_chat=True,
        )

        application.add_handler(conv_handler)
        application.add_handler(CallbackQueryHandler(start_registration, pattern='start'))
        application.add_handler(CallbackQueryHandler(create_card, pattern='create_card'))

        application.run_polling()

    except Exception as e:
        logging.error("Ошибка при запуске бота: %s", e)

if __name__ == '__main__':
    main()
