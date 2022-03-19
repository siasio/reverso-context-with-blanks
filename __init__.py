from aqt import gui_hooks
# import all of the Qt GUI library
#from anki import hooks
from anki.hooks import addHook
import os, sys

libfolder = os.path.dirname(__file__)
sys.path.insert(0, libfolder)
from imports import *
from card_template import add_reverso_notetype
from language_management import setup_lang_buttons
from focus_lost import onFocusLost

addHook('editFocusLost', onFocusLost)
gui_hooks.main_window_did_init.append(add_reverso_notetype)
gui_hooks.editor_did_load_note.append(setup_lang_buttons)
