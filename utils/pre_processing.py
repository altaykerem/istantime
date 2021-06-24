lower_map = {ord("I"): "ı", ord("İ"): "i"}
upper_map = {ord("i"): "İ", ord("ı"): "I"}


def turkish_lower(s: str):
    return s.translate(lower_map).lower()


def turkish_upper(s: str):
    return s.translate(upper_map).upper()
