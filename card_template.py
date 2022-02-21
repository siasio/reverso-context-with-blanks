import os

CONTEXT = 'Context'
WORD = 'Word'

REVERSO_NOTETYPE = "Cloze reverso"
BASIC_NOTETYPE = 'Basic'
# key names used by Anki
_anki_css = "css"
_anki_templates = "tmpls"
_anki_name = "name"
_anki_front = "qfmt"
_anki_back = "afmt"
libfolder = os.path.dirname(__file__)


def add_reverso_notetype() -> None:
    from aqt import mw
    if mw.col.models.byName(REVERSO_NOTETYPE):
        return
    nt = mw.col.models.copy(mw.col.models.get(mw.col.models.id_for_name(BASIC_NOTETYPE)))
    nt[_anki_name] = REVERSO_NOTETYPE
    fields = mw.col.models.fieldMap(nt)
    field_names = mw.col.models.fieldNames(nt)
    mw.col.models.rename_field(nt, fields[field_names[0]][1], WORD)
    mw.col.models.rename_field(nt, fields[field_names[1]][1], CONTEXT)
    tmpl = nt['tmpls'][0]
    front_html = os.path.join(libfolder, 'front_template.html')
    back_html = os.path.join(libfolder, 'back_template.html')
    card_css = os.path.join(libfolder, 'card_style.css')
    with open(front_html, "r", encoding="utf-8") as f:
        tmpl[_anki_front] = f.read()
    with open(back_html, "r", encoding="utf-8") as f:
        tmpl[_anki_back] = f.read()
    with open(card_css, "r", encoding="utf-8") as f:
        nt[_anki_css] = f.read()
    mw.col.models.save(nt)

