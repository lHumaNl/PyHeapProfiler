# utils/helpers.py

def format_size(size):
    for unit in ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} ПБ"
