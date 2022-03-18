# import the main window object (mw) from aqt
from aqt import mw, gui_hooks
# import all of the Qt GUI library
from aqt.qt import *
import aqt.editor
from aqt.editor import Editor
from aqt.addcards import AddCards
from aqt.editcurrent import EditCurrent
from anki import hooks
from anki.hooks import addHook

libfolder = os.path.dirname(__file__)
sys.path.insert(0, libfolder)
from reverso_connect import fetch_context_data
from card_template import add_reverso_notetype
config = mw.addonManager.getConfig(__name__)


SEPARATOR = '<br>----<br>'
CONTEXT = 'Context'
WORD = 'Word'
LANGUAGES = config['shown_languages']
LANG_NAMES = {
    'ar': 'Arabic',
    'de': 'German',
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'il': 'Hebrew',
    'it': 'Italian',
    'ja': 'Japanese',
    'nl': 'Dutch',
    'pl': 'Polish',
    'pt': 'Portuguese',
    'ro': 'Romanian',
    'ru': 'Russian',
    'sv': 'Swedish',
    'tr': 'Turkish',
    'zh': 'Chinese'
}
LEARNED_LANG = "learned_language"
NATIVE_LANG = "native_language"


def update_lang(lang, button, key) -> None:
    button.setIcon(QIcon(QPixmap(os.path.join(libfolder, f'flags/{lang}.png'))))
    config[key] = lang
    mw.addonManager.writeConfig(__name__, config)


def setup_lang_buttons(editor: Editor):
    if hasattr(editor, "parentWindow") and isinstance(editor.parentWindow, AddCards):
        win = aqt.dialogs._dialogs["AddCards"][1]
    elif hasattr(editor, "parentWindow") and isinstance(editor.parentWindow, EditCurrent):
        win = aqt.dialogs._dialogs["EditCurrent"][1]
    else:
        win = aqt.dialogs._dialogs["AddCards"][1]

    if win is None:
        return

    box = win.form.buttonBox

    # check if buttons have been already added
    if hasattr(box, "lang_btn") and box.lang_btn is not None:
        return
    if hasattr(box, "nat_btn") and box.nat_btn is not None:
        return

    # Add menu for the learned language
    lang_label = QLabel('Language:')
    lang_button = QPushButton(' ')
    lang_menu = QMenu()
    for lang in LANGUAGES:
        lang_path = os.path.join(libfolder, f'flags/{lang}.png')
        action = QAction(QIcon(lang_path), LANG_NAMES[lang].capitalize(), win)
        action.triggered.connect(lambda chk, lang=lang, win=win: update_lang(lang, lang_button, LEARNED_LANG))
        lang_menu.addAction(action)
    box.layout().insertWidget(0, lang_label)
    box.layout().insertWidget(1, lang_button)
    lang_button.setMenu(lang_menu)
    learned_lang_path = os.path.join(libfolder, f'flags/{config[LEARNED_LANG]}.png')
    lang_button.setIcon(QIcon(QPixmap(learned_lang_path)))
    box.lang_btn = lang_button

    # Add menu for the native language
    nat_label = QLabel('Native:')
    nat_button = QPushButton(' ')
    nat_menu = QMenu()
    for lang in LANGUAGES:
        lang_path = os.path.join(libfolder, f'flags/{lang}.png')
        action = QAction(QIcon(lang_path), LANG_NAMES[lang].capitalize(), win)
        action.triggered.connect(lambda chk, lang=lang, win=win: update_lang(lang, nat_button, NATIVE_LANG))
        nat_menu.addAction(action)
    box.layout().insertWidget(2, nat_label)
    box.layout().insertWidget(3, nat_button)
    nat_button.setMenu(nat_menu)
    nat_lang_path = os.path.join(libfolder, f'flags/{config[NATIVE_LANG]}.png')
    nat_button.setIcon(QIcon(QPixmap(nat_lang_path)))
    box.nat_btn = nat_button

    win.update()


def is_reverso_card(n):
    return "reverso" in n.model()['name'].lower()


def locate_reverso_fields(mw, n):
    srcFields = [WORD]
    dstFields = [CONTEXT]
    src, srcIdx, dst = None, None, None
    for c, name in enumerate(mw.col.models.fieldNames(n.model())):
        for f in srcFields:
            if name == f:
                src = f
                srcIdx = c
        for f in dstFields:
            if name == f:
                dst = f
    return src, srcIdx, dst


def onFocusLost(flag, n, fidx):
    from aqt import mw
    if not is_reverso_card(n):
        return flag
    src, srcIdx, dst = locate_reverso_fields(mw, n)
    if not src or not dst:
        return flag
    # event coming from src field?
    if fidx != srcIdx:
        return flag
    srcTxt = n[src]  # mw.col.media.strip(n[src])?
    if not srcTxt:
        return flag
    learned_lang = config[LEARNED_LANG]
    native_lang = config[NATIVE_LANG]
    if learned_lang == native_lang:
        feedback_text = f'Chosen te same learned language and native language ({LANG_NAMES[learned_lang]})<br>' \
                        f'Change at least one of them'
    else:
        context_data, counter = fetch_context_data(n[src], learned_lang, native_lang, config["sample_phrases_number"], SEPARATOR)
        success = counter != 0
        feedback_text = f"Found {counter} sentences{SEPARATOR}{context_data}" if success else\
            f"Word not found in the {LANG_NAMES[learned_lang]} dictionary!<br>" \
            f"Check your speelling and make sure that you chose correct languages<br>" \
            f"For some pairs of languages Reverso doesn't provide good examples." \
            f"In such case, try adjusting the native language, e.g. change it to English."
    n[dst] = feedback_text
    return True


addHook('editFocusLost', onFocusLost)
gui_hooks.main_window_did_init.append(add_reverso_notetype)
gui_hooks.editor_did_load_note.append(setup_lang_buttons)
