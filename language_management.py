from aqt import mw
from aqt.qt import *
import aqt.editor
from aqt.editor import Editor
from aqt.addcards import AddCards
from aqt.editcurrent import EditCurrent
from definitions import *
config = mw.addonManager.getConfig(__name__)
LANGUAGES = config['shown_languages']


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