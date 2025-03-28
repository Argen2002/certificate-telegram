import pdfplumber

print(f"Версия pdfplumber: {pdfplumber.__version__}")

TEMPLATE_PATH = "1.pdf"

try:
    with pdfplumber.open(TEMPLATE_PATH) as pdf:
        page = pdf.pages[0]  # Берем первую страницу
        print(f"Тип объекта page: {type(page)}")

        shapes_found = page.extract_shapes()

        print("Все найденные фигуры и их координаты:")
        for shape_data in shapes_found:
            print(f"Тип: {shape_data.get('type')}")
            if shape_data.get('type') == 'line':
                print(f"  Координаты: (x0={shape_data.get('x0')}, top={shape_data.get('top')}, x1={shape_data.get('x1')}, bottom={shape_data.get('bottom')})")
                print(f"  Цвет обводки (stroke): {shape_data.get('stroke')}")
                print(f"  Толщина линии: {shape_data.get('linewidth')}")
            print("-" * 20)

except Exception as e:
    print(f"Ошибка при обработке PDF: {e}")

# Вы можете удалить строки с выводом версии pdfplumber и типа объекта page,
# если скрипт будет работать корректно.