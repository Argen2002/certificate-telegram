import old_telegram
from old_telegram.ext import Application, CommandHandler

BOT_TOKEN = '7911022788:AAEQyMM3DK5WPtGBtT3mybgXDQ9vSNqewQk'

async def start(update, context):
    for _ in range(25):
        await update.message.reply_text("Ула напишем заявку")

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    application.run_polling()

if __name__ == '__main__':
    main()