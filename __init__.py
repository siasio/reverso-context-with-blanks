from aqt import gui_hooks
# import all of the Qt GUI library
#from anki import hooks
from anki.hooks import addHook
#import os, sys

#libfolder = os.path.dirname(__file__)
#sys.path.insert(0, libfolder)
from . import card_template, language_management, focus_lost

addHook('editFocusLost', focus_lost.onFocusLost)
gui_hooks.main_window_did_init.append(card_template.add_reverso_notetype)
gui_hooks.editor_did_load_note.append(language_management.setup_lang_buttons)
