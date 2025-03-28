import pdfplumber

TEMPLATE_PATH = "1.pdf"

try:
    with pdfplumber.open(TEMPLATE_PATH) as pdf:
        page = pdf.pages[0]  # Берем первую страницу
        words_found = page.extract_words()

        print("Все найденные слова и их координаты:")
        for word_data in words_found:
            print(f"{word_data['text']}: (x={word_data['x0']}, y={word_data['top']})")

except Exception as e:
    print(f"Ошибка при обработке PDF: {e}")
