def int_or_none(value):
    return str(int(value)) if value is not None else '0'


def float_or_none(value):
    return f"{float(value):.2f}" if value is not None else '0.00'


def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"
