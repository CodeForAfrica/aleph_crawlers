import re


def clean(text):
    if text is None:
        return text
    if hasattr(text, 'text_content'):
        text = text.text_content()
    text = re.sub('\s+', ' ', text)
    return text.strip()
