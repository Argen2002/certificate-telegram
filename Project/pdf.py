from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import fitz  # Импортируем PyMuPDF

# Настройки
EXCEL_FILE = "players_data.xlsx"
TEMPLATE_PATH = "template.pdf"  # Теперь PDF
OUTPUT_FOLDER = "cards"
OUTPUT_PDF_FOLDER = "pdf"  # Название папки для PDF
OUTPUT_PDF = os.path.join(OUTPUT_PDF_FOLDER, "all_cards.pdf")
FONT_PATH = "arialbd.ttf"  # Попытка использовать жирный шрифт
CARD_SIZE = (1655, 2340)

# Координаты и размер для фото (нужно проверить и настроить!)
PHOTO_POSITION = (630, 200)
PHOTO_SIZE = (400, 400)

# Обновленные координаты и параметры
FIELD_SETTINGS = {
    # Оценка и потенциал (левый верхний угол)
    "Оценка_Потенциал": {
        "position": (200, 100),
        "font_size": 61.4,
        "color": "black"
    },

    # Центральная часть (имя, фамилия, дата/квартал)
    "Имя": {
        "position": (CARD_SIZE[0]//2, 1200),
        "font_size": 56.1,
        "color": "blue",
        "align": "center"
    },
    "Фамилия": {
        "position": (CARD_SIZE[0]//2, 1280),
        "font_size": 56.1,
        "color": "blue",
        "align": "center"
    },
    "Дата_Квартал": {
        "position": (CARD_SIZE[0]//2, 1360),
        "font_size": 56.1,
        "color": "blue",
        "align": "center"
    },
    "Клуб": {
        "position": (CARD_SIZE[0]//2, 1440),
        "font_size": 40,
        "color": "red",
        "align": "center"
    },

    # Правая часть (рабочая нога и позиция)
    "Рабочая нога": {
        "position": (800, 1800),
        "font_size": 50,
        "color": "black"
    },
    "Позиция": {
        "position": (800, 1890),
        "font_size": 50,
        "color": "black"
    }
}

def generate_cards():
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

        data = pd.read_excel(EXCEL_FILE)
        data.columns = data.columns.str.strip()

        try:
            font_bold = ImageFont.truetype(FONT_PATH, size=1) # Загрузка шрифта для проверки
        except IOError:
            print(f"Ошибка: Не найден жирный шрифт по пути '{FONT_PATH}'. Пожалуйста, убедитесь, что файл существует.")
            return

        for index, row in data.iterrows():
            img = template_image.copy() # Копируем изображение шаблона для каждой карточки
            draw = ImageDraw.Draw(img)

            # Вставка фото
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

            # Оценка и потенциал
            eval_text = f"{row['Оценка']}{row['Потенциал']}"
            font = ImageFont.truetype(FONT_PATH, size=FIELD_SETTINGS['Оценка_Потенциал']['font_size'])
            draw.text(
                FIELD_SETTINGS['Оценка_Потенциал']['position'],
                eval_text,
                font=font,
                fill=FIELD_SETTINGS['Оценка_Потенциал']['color']
            )

            # Центральный блок
            for field in ['Имя', 'Фамилия']:
                text = str(row[field])
                font = ImageFont.truetype(FONT_PATH, size=FIELD_SETTINGS[field]['font_size'])
                x, y = FIELD_SETTINGS[field]['position']
                if FIELD_SETTINGS[field].get('align') == 'center':
                    bbox = draw.textbbox((x, y), text, font=font)
                    x = x - (bbox[2] - bbox[0])//2
                draw.text((x, y), text, font=font, fill=FIELD_SETTINGS[field]['color'])

            # Дата + Квартал
            date_text = f"{row['дата рождения'].strftime('%d.%m.%Y')}\\{row['Квартал']}"
            font = ImageFont.truetype(FONT_PATH, size=FIELD_SETTINGS['Дата_Квартал']['font_size'])
            x, y = FIELD_SETTINGS['Дата_Квартал']['position']
            bbox = draw.textbbox((x, y), date_text, font=font)
            x = x - (bbox[2] - bbox[0])//2
            draw.text((x, y), date_text, font=font, fill=FIELD_SETTINGS['Дата_Квартал']['color'])

            # Клуб
            font = ImageFont.truetype(FONT_PATH, size=FIELD_SETTINGS['Клуб']['font_size'])
            x, y = FIELD_SETTINGS['Клуб']['position']
            bbox = draw.textbbox((x, y), row['Клуб'], font=font)
            x = x - (bbox[2] - bbox[0])//2
            draw.text((x, y), row['Клуб'], font=font, fill=FIELD_SETTINGS['Клуб']['color'])

            # Правая часть
            for field in ['Рабочая нога', 'Позиция']:
                text = str(row[field]).upper()
                font = ImageFont.truetype(FONT_PATH, size=FIELD_SETTINGS[field]['font_size'])
                draw.text(
                    FIELD_SETTINGS[field]['position'],
                    text,
                    font=font,
                    fill=FIELD_SETTINGS[field]['color']
                )

            generated_images.append(img)
            print(f"Обработано: {row['Фамилия']} {row['Имя']}")

        # Объединение изображений в PDF
        if generated_images:
            generated_images[0].save(
                OUTPUT_PDF,
                "PDF",
                resolution=100.0,
                save_all=True,
                append_images=generated_images[1:]
            )
            print(f"Все карточки объединены в файл: {OUTPUT_PDF}")
        else:
            print("Не было создано ни одной карточки.")

        pdf_document.close()

    except FileNotFoundError as e:
        print(f"Ошибка: Файл не найден - {e}")
    except Exception as e:
        print(f"Ошибка: {e}")

generate_cards()