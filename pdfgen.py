from pdfme import build_pdf




class Document:
    def __init__(self, title, name, email, event_name, date):
        self.title = title
        self.__content = {
            'name': name,
            'email': email,
            'event_name': event_name,
            'date': date
        }
        return build_pdf(self.__content, self.title)

    
    

def randomize_doc_name():
    import random
    import string

    # Генерируем случайное имя файла из 10 символов
    random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return f'{random_name}.pdf'

def gen_File(name, name, email, event_name, date):
    file_name = randomize_doc_name()
    with open(file_name, 'wb') as f:
        f.write(Document(name, email, event_name, date))