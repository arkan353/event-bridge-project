from pdfme import build_pdf

# Cyrillic to Latin transliteration map
CYRILLIC_MAP = {
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
    'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
    'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
    'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
    'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
}


def transliterate(text):
    """Transliterate Cyrillic characters to Latin equivalents.
    The pdfme library only supports WinAnsiEncoding (Latin-1), so
    any non-Latin characters would cause a KeyError in font width lookup.
    """
    return ''.join(CYRILLIC_MAP.get(c, c) for c in text)


def randomize_doc_name():
    import random
    import string

    # Генерируем случайное имя файла из 10 символов
    random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return f'{random_name}.pdf'


def gen_File(name, email, event_name, date, vip=False, seat=None):
    """Generate a PDF ticket file with event information.

    Parameters:
    - name, email, event_name, date: ticket fields
    - vip (bool): if True, use the VIP template
    - seat (str|None): optional seat or pass level
    """
    file_name = randomize_doc_name()

    # Transliterate to avoid KeyError from non-Latin chars in Helvetica font
    name = transliterate(name)
    event_name = transliterate(event_name)
    email = transliterate(email)

    # Build content differently for VIP vs regular tickets
    if vip:
        content = [
            {".": f"{event_name}", "style": {"s": 28, "b": True, "align": "center", "margin_top": 6}},
            {".": "VIP PASS", "style": {"s": 18, "b": True, "c": 0.15, "align": "center", "margin_top": 6}},
            {".": "--------------------------------------------", "style": {"s": 8, "c": 0.8, "align": "center", "margin_top": 8}},
            {".": f"Name: {name}", "style": {"s": 14, "margin_top": 12}},
            {".": f"Email: {email}", "style": {"s": 12, "margin_top": 6, "c": 0.4}},
            {".": f"Seat / Level: {seat or 'VIP Lounge'}", "style": {"s": 14, "margin_top": 10, "b": True}},
            {".": f"Date: {date}", "style": {"s": 14, "margin_top": 10}},
            {".": "", "style": {"s": 6, "margin_top": 8}},
            {".": "ADMIT ONE - VIP", "style": {"s": 10, "align": "center", "c": 0.6, "margin_top": 12}},
            {".": "Present this pass at the VIP entrance.", "style": {"s": 9, "align": "center", "c": 0.5, "margin_top": 8}},
        ]
        # slightly tighter margins for VIP-style card look
        page_style = {"page_size": "a4", "margin": [40, 40]}
    else:
        content = [
            {".": f"Ticket: {event_name}", "style": {"s": 20, "b": True, "c": 0.2}},
            {".": f"Name: {name}", "style": {"s": 14, "margin_top": 20}},
            {".": f"Email: {email}", "style": {"s": 14, "margin_top": 10}},
            {".": f"Date: {date}", "style": {"s": 14, "margin_top": 10}},
        ]
        page_style = {"page_size": "a4", "margin": [50, 50]}

    document = {
        "page_style": page_style,
        "style": {"s": 12, "f": "Helvetica"},
        "sections": [{"content": content}],
    }

    with open(file_name, 'wb') as f:
        build_pdf(document, f)
