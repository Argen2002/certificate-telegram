import telebot
from telebot import types
import pandas as pd
import os
from PIL import Image, ImageDraw, ImageFont
import fitz  # Импортируем PyMuPDF

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
BOT_TOKEN = '7911022788:AAEQyMM3DK5WPtGBtT3mybgXDQ9vSNqewQk'
bot = telebot.TeleBot(BOT_TOKEN)

# Настройки (можно вынести в отдельный файл конфигурации)
TEMPLATE_PATH = "template.pdf"
OUTPUT_FOLDER = "cards_temp"  # Временная папка для изображений (если нужно)
OUTPUT_PDF_FOLDER = "pdf_temp" # Временная папка для PDF
FONT_PATH = "arialbd.ttf"
CARD_SIZE = (1655, 2340)
PHOTO_POSITION = (630, 200)
PHOTO_SIZE = (400, 400)

FIELD_SETTINGS = {
    "Оценка_Потенциал": {"position": (200, 100), "font_size": 61.4, "color": "black"},
    "Имя": {"position": (CARD_SIZE[0]//2, 1200), "font_size": 56.1, "color": "blue", "align": "center"},
    "Фамилия": {"position": (CARD_SIZE[0]//2, 1280), "font_size": 56.1, "color": "blue", "align": "center"},
    "Дата_Квартал": {"position": (CARD_SIZE[0]//2, 1360), "font_size": 56.1, "color": "blue", "align": "center"},
    "Клуб": {"position": (CARD_SIZE[0]//2, 1440), "font_size": 40, "color": "red", "align": "center"},
    "Рабочая нога": {"position": (800, 1800), "font_size": 50, "color": "black"},
    "Позиция": {"position": (800, 1890), "font_size": 50, "color": "black"}
}

def generate_cards(excel_file_path, output_pdf_path):
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    if not os.path.exists(OUTPUT_PDF_FOLDER):
        os.makedirs(OUTPUT_PDF_FOLDER)

    generated_images = []

    try:
        pdf_document = fitz.open(TEMPLATE_PATH)
        template_page = pdf_document[0]
        initial_pix = template_page.get_pixmap()
        matrix = fitz.Matrix(CARD_SIZE[0] / initial_pix.width, CARD_SIZE[1] / initial_pix.height)
        pix = template_page.get_pixmap(matrix=matrix)
        template_image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        template_image = template_image.convert("RGBA")

        data = pd.read_excel(excel_file_path)
        data.columns = data.columns.str.strip()

        try:
            font_bold = ImageFont.truetype(FONT_PATH, size=1)
        except IOError:
            print(f"Ошибка: Не найден жирный шрифт по пути '{FONT_PATH}'. Пожалуйста, убедитесь, что файл существует.")
            return None

        for index, row in data.iterrows():
            img = template_image.copy()
            draw = ImageDraw.Draw(img)

            photo_path = row.get("Фото")
            if isinstance(photo_path, str) and os.path.exists(photo_path):
                try:
                    player_photo = Image.open(photo_path).convert("RGBA")
                    player_photo = player_photo.resize(PHOTO_SIZE)
                    img.paste(player_photo, PHOTO_POSITION)
                except Exception as e:
                    print(f"Ошибка при обработке фото '{photo_path}': {e}")
            elif pd.isna(photo_path):
                print(f"Предупреждение: Для '{row['Фамилия']} {row['Имя']}' не указан путь к фото.")
            elif not isinstance(photo_path, str):
                print(f"Предупреждение: Некорректный формат пути к фото для '{row['Фамилия']} {row['Имя']}'. Ожидается строка, получено: {type(photo_path)} - {photo_path}")
            else:
                print(f"Предупреждение: Фото для '{row['Фамилия']} {row['Имя']}' не найдено по пути: '{photo_path}'.")

            for field, settings in FIELD_SETTINGS.items():
                text = str(row.get(field, ''))
                font = ImageFont.truetype(FONT_PATH, size=settings['font_size'])
                x, y = settings['position']
                fill = settings['color']
                align = settings.get('align')

                if field in ['Имя', 'Фамилия', 'Дата_Квартал', 'Клуб'] and align == 'center':
                    bbox = draw.textbbox((x, y), text, font=font)
                    x = x - (bbox[2] - bbox[0]) // 2
                draw.text((x, y), text, font=font, fill=fill)

            generated_images.append(img)
            print(f"Обработано: {row['Фамилия']} {row['Имя']}")

        if generated_images:
            generated_images[0].save(
                output_pdf_path,
                "PDF",
                resolution=100.0,
                save_all=True,
                append_images=generated_images[1:]
            )
            print(f"Все карточки объединены в файл: {output_pdf_path}")
            return output_pdf_path
        else:
            print("Не было создано ни одной карточки.")
            return None

        pdf_document.close()

    except FileNotFoundError as e:
        print(f"Ошибка: Файл не найден - {e}")
        return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне Excel-файл, и я создам PDF с карточками игроков.")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    try:
        chat_id = message.chat.id
        document = message.document

        if not document.file_name.endswith(('.xlsx', '.xls')):
            bot.reply_to(message, "Пожалуйста, отправьте файл в формате .xlsx или .xls.")
            return

        file_info = bot.get_file(document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        excel_file_name = f"temp_{chat_id}.xlsx"
        output_pdf_name = os.path.join(OUTPUT_PDF_FOLDER, f"cards_{chat_id}.pdf")

        with open(excel_file_name, 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.reply_to(message, "Файл получен, начинаю обработку...")

        pdf_file_path = generate_cards(excel_file_name, output_pdf_name)

        if pdf_file_path:
            with open(pdf_file_path, 'rb') as pdf_file:
                bot.send_document(chat_id, pdf_file, caption="Готово! Ваши карточки:")
            os.remove(excel_file_name)
            os.remove(pdf_file_path) # Удаляем временный PDF
        else:
            bot.reply_to(message, "Произошла ошибка при создании PDF файла.")
            os.remove(excel_file_name)

    except Exception as e:
        bot.reply_to(message, f"Произошла непредвиденная ошибка: {e}")

if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling(none_stop=True)