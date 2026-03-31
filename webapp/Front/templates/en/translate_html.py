from lxml import etree, html
import json

def translate_with_lxml(input_path, output_path, json_path):
    # Загружаем переводы
    with open(json_path, 'r', encoding='utf-8') as f:
        translations = json.load(f)

    # Загружаем HTML
    parser = html.HTMLParser(remove_blank_text=False)
    tree = html.parse(input_path, parser)

    def translate_text(text):
        for ru, en in translations.items():
            text = text.replace(ru, en)
        return text

    # Переводим текст
    for el in tree.xpath('//text()'):
        if el.strip():
            parent = el.getparent()
            parent.text = translate_text(el)

    # Переводим атрибуты
    for el in tree.xpath('//*[@placeholder or @title or @alt or @value]'):
        for attr in ['placeholder', 'title', 'alt', 'value']:
            if el.get(attr):
                el.set(attr, translate_text(el.get(attr)))

    # Преобразуем HTML в строку
    result = etree.tostring(tree, pretty_print=True, method="html", encoding="unicode")

    # Удаляем %20, заменяем пробелы на табы и убираем пустые строки
    lines = result.splitlines()
    cleaned_lines = [
        line.replace("    ", "\t").replace("%20", "")
        for line in lines if line.strip()
    ]
    cleaned_html = "\n".join(cleaned_lines)

    # Сохраняем
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_html)

# Пример запуска
if __name__ == "__main__":
    translate_with_lxml(
        input_path='botSorting.html',
        json_path='translation_ru_en.json',
        output_path='botSorting_translated.html'
    )
