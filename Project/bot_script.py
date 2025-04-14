import telegram
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext

BOT_TOKEN = '7911022788:AAEQyMM3DK5WPtGBtT3mybgXDQ9vSNqewQk'
DOCUMENT_PATH = 'zayavka.doc'  # Укажите путь к вашему файлу

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Да", callback_data='send_doc')],
        [InlineKeyboardButton("Нет", callback_data='deny_doc')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Вам скинуть док?", reply_markup=reply_markup)

async def handle_button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()  # Отвечаем на callback query (чтобы убрать "часики")

    if query.data == 'send_doc':
        try:
            with open(DOCUMENT_PATH, 'rb') as doc_file:
                await context.bot.send_document(
                    chat_id=query.message.chat_id,
                    document=InputFile(doc_file, filename='zayavka.doc'),
                    caption="Ваша заявка"
                )
        except FileNotFoundError:
            await context.bot.send_message(chat_id=query.message.chat_id, text="Файл заявки не найден.")
        except Exception as e:
            await context.bot.send_message(chat_id=query.message.chat_id, text=f"Произошла ошибка при отправке файла: {e}")
    elif query.data == 'deny_doc':
        await context.bot.send_message(chat_id=query.message.chat_id, text="Пиши заявку сам ула")

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    start_handler = CommandHandler('start', start)
    button_handler = CallbackQueryHandler(handle_button)

    application.add_handler(start_handler)
    application.add_handler(button_handler)

    application.run_polling()

if __name__ == '__main__':
    main()