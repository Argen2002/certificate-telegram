import pandas as pd
import fitz  # PyMuPDF
import os

# Настройки
EXCEL_FILE = "certificates_data.xlsx"  # Замените на имя вашего Excel файла
TEMPLATE_PATH = "1.pdf"  # Замените на имя вашего PDF шаблона
OUTPUT_FOLDER = "generated_certificates"
OUTPUT_PDF = "all_certificates.pdf"
LATO_BOLD_FONT = "Lato-Bold.ttf"  # Убедитесь, что файл существует
LATO_REGULAR_FONT = "Lato-Regular.ttf"  # Убедитесь, что файл существует

# Координаты для размещения текста
COURSE_DATE_POSITION = (int(259.60796504832 + 100), int(404.35723852800004))  # Course dates:
CERTIFICATE_NUMBER_POSITION = (int(259.132936272384 + 100), int(420.36335692800003))  # Certificate №:
NAME_POSITION = (int(279.04052936447994), int(267.16556134400003))  # Имя на awarded: (опустил Y)

NAME_FONT_SIZE = 48  # Увеличил размер шрифта
DATE_NUMBER_FONT_SIZE = 13.34

def generate_certificate(data, template_path, output_folder, lato_bold_path, lato_regular_path):
    """Генерирует один сертификат на основе данных."""
    name = data['Name'].upper()
    certificate_number = str(data['Certificate№'])
    date = pd.to_datetime(data['Date']).strftime('%d-%m-%Y') # Форматируем дату

    try:
        pdf_document = fitz.open(template_path)
        page = pdf_document[0]

        # Добавляем шрифт, если он еще не добавлен
        try:
            font_name_bold = "Lato-Bold"
            font_name_regular = "Lato-Regular"
            page.insert_font(fontname=font_name_bold, fontfile=lato_bold_path)
            page.insert_font(fontname=font_name_regular, fontfile=lato_regular_path)

        except Exception as e:
            print(f"Ошибка при добавлении шрифта: {e}")

        # Размещаем имя
        name_rect = fitz.Rect(NAME_POSITION[0] - 300, NAME_POSITION[1], NAME_POSITION[0] + 600, NAME_POSITION[1] + 50) # Широкая область для центрирования
        page.insert_textbox(name_rect, name, fontsize=NAME_FONT_SIZE, fontname="Lato-Bold", color=(0, 0, 0), align=fitz.TEXT_ALIGN_CENTER)

        # Размещаем дату курса
        date_text = pd.to_datetime(data['Date']).strftime('%d-%m-%Y')
        date_rect = fitz.Rect(COURSE_DATE_POSITION[0], COURSE_DATE_POSITION[1], COURSE_DATE_POSITION[0] + 200, COURSE_DATE_POSITION[1] + 20)
        page.insert_textbox(date_rect, date_text, fontsize=DATE_NUMBER_FONT_SIZE, fontname=font_name_regular, color=(0, 0, 0), align=fitz.TEXT_ALIGN_LEFT)

        # Размещаем номер сертификата
        number_text = str(data['Certificate№'])
        number_rect = fitz.Rect(CERTIFICATE_NUMBER_POSITION[0], CERTIFICATE_NUMBER_POSITION[1], CERTIFICATE_NUMBER_POSITION[0] + 250, CERTIFICATE_NUMBER_POSITION[1] + 20)
        page.insert_textbox(number_rect, number_text, fontsize=DATE_NUMBER_FONT_SIZE, fontname=font_name_regular, color=(0, 0, 0), align=fitz.TEXT_ALIGN_LEFT)

        output_path = os.path.join(output_folder, f"certificate_{certificate_number}.pdf")
        pdf_document.save(output_path)
        pdf_document.close()
        return output_path

    except FileNotFoundError:
        print(f"Ошибка: Файл '{template_path}' не найден.")
        return None
    except Exception as e:
        print(f"Произошла ошибка при обработке сертификата для {name}: {e}")
        return None

def merge_pdfs(pdf_files, output_path):
    """Объединяет несколько PDF файлов в один."""
    if not pdf_files:
        return

    merger = fitz.open()
    for pdf_file in pdf_files:
        try:
            doc = fitz.open(pdf_file)
            merger.insert_pdf(doc)
            doc.close()
        except Exception as e:
            print(f"Ошибка при добавлении файла {pdf_file} для объединения: {e}")

    merger.save(output_path)
    merger.close()
    print(f"Все сертификаты объединены в файл: {output_path}")

def main():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    try:
        df = pd.read_excel(EXCEL_FILE)
        print("Содержимое DataFrame:")
        print(df)
    except FileNotFoundError:
        print(f"Ошибка: Файл '{EXCEL_FILE}' не найден.")
        return

    generated_certificate_paths = []

    for index, row in df.iterrows():
        certificate_path = generate_certificate(row, TEMPLATE_PATH, OUTPUT_FOLDER, LATO_BOLD_FONT, LATO_REGULAR_FONT)
        if certificate_path:
            generated_certificate_paths.append(certificate_path)

    if generated_certificate_paths:
        merge_pdfs(generated_certificate_paths, OUTPUT_PDF)
        # Очистка временных файлов
        for path in generated_certificate_paths:
            os.remove(path)
        os.rmdir(OUTPUT_FOLDER)

if __name__ == "__main__":
    main()


file_path = "certificates_data.xlsx"  # Убедитесь, что файл в нужной директории
df = pd.read_excel(file_path)

# Вывод списка столбцов
print(df.columns.tolist())