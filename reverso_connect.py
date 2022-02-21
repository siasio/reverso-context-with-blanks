import os, sys
libfolder = os.path.dirname(__file__)
sys.path.insert(0, libfolder)
from reverso_api import ReversoContextAPI


def highlight_example(text, highlighted, left_highlighter="**", right_highlighter="**"):

    def insert_char(string, index, char):
        return string[:index] + char + string[index:]

    def highlight_once(string, start, end, shift):
        s = insert_char(string, start + shift, left_highlighter)
        s = insert_char(s, end + shift + len(left_highlighter), right_highlighter)
        return s

    shift = 0
    for start, end in highlighted:
        text = highlight_once(text, start, end, shift)
        shift += len(left_highlighter) + len(right_highlighter)
    return text


def fetch_context_data(cur_word, target_lang, native_lang, phrases_num, separator):
    api = ReversoContextAPI(cur_word, "", target_lang, native_lang)
    translations = ''
    natives = ''
    counter = 0
    for source, target in api.get_examples():
        translations += f'{highlight_example(source.text, source.highlighted)},,'
        natives += f'{highlight_example(target.text, target.highlighted)},,'
        counter += 1
        if counter == phrases_num:
            break
    translations = translations[:-2]
    natives = natives[:-2]
    context_data = translations + separator + natives
    return context_data, counter
