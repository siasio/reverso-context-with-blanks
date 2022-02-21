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
from reverso_api import ReversoContextAPI


config = mw.addonManager.getConfig(__name__)
SEPARATOR = '<br>----<br>'
CONTEXT = 'Context'
WORD = 'Word'
LANGUAGES = config['shown_languages']
LANG_NAMES = {
    'ar': 'Arabic',
    'cn': 'Chinese',
    'de': 'German',
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'il': 'Hebrew',
    'it': 'Italian',
    'jp': 'Japanese',
    'nl': 'Dutch',
    'pl': 'Polish',
    'pt': 'Portuguese',
    'ro': 'Romanian',
    'ru': 'Russian',
    'tr': 'Turkish'
}
LEARNED_LANG = "learned_language"
NATIVE_LANG = "native_language"


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


def fetch_context_data(cur_word, target_lang, native_lang):
    api = ReversoContextAPI(cur_word, "", target_lang, native_lang)
    translations = ''
    natives = ''
    counter = 0
    for source, target in api.get_examples():
        translations += f'{highlight_example(source.text, source.highlighted)},,'
        natives += f'{highlight_example(target.text, target.highlighted)},,'
        counter += 1
        if counter == config["sample_phrases_number"]:
            break
    translations = translations[:-2]
    natives = natives[:-2]
    context_data = translations + SEPARATOR + natives
    return context_data, counter


def add_reverso_notetype() -> None:
    from aqt import mw
    nt = mw.col.models.new('Cloze-reverso')
    mw.col.models.addField(nt, WORD)
    mw.col.models.addField(nt, CONTEXT)
    mw.col.models.addTemplate(nt, """{{#Context}}
	<span id="context">{{Context}}</span>
	<br><br>
	<div id="hint" class="hidden">
		<p class="trigger">Check native language</p>
		<p class="payload" id="hintpayload"></p>
	</div>
	<script type="text/javascript">
		function highlightText(text, highlighter) {
			textParts = text.split(highlighter);
			return textParts[0] + '<span style="background-color:#dff5c4;">' + textParts[1] + "</span>" + textParts[2];
		}
		function occludeText(text, highlighter) {
			textParts = text.split(highlighter);
			return textParts[0] + '<span style="background-color:#fae7b5;">&lt;...&gt;</span>' + textParts[2];
		}
		var langData = document.getElementById("context").innerHTML.split("<br>----<br>");
		var phrases = langData[1].split(",,");
		var nativePhrases = langData[2].split(",,");
		window.randomIndex = Math.floor(Math.random() * phrases.length);
		window.randomPhrase = phrases[window.randomIndex];
		document.getElementById("context").innerHTML = occludeText(window.randomPhrase, "**");
		var natRandomPhrase = nativePhrases[window.randomIndex];
		hint.addEventListener('click', function() { this.setAttribute('class', 'shown'); this.innerHTML = highlightText(natRandomPhrase, '**');});
	</script>
{{/Context}}

{{#Word}}
	<div id="answer">{{Word}}</div>
	<script>
		var occluded = document.getElementById("answer").innerHTML
		document.getElementById("answer").innerHTML = highlightText(window.randomPhrase, '**')
	</script>
{{/Word}}

.card {
 font-family: arial;
 font-size: 20px;
 text-align: center;
 color: black;
 background-color: white;
}

#hint { background: #f2fbe7; border: 1px solid #dff5c4; border-radius: 6px; color: #7a876b; }

#hint.hidden:hover { background: #dff5c4; color: #000; cursor: pointer; }
#hint.hidden .payload { display: none; }

#hint.shown { background: #fff; color: #000; }
#hint.shown .trigger { display: none; }
#hint.shown .payload { display: block; }""")


def update_lang(lang, button, key) -> None:
    button.setIcon(QIcon(QPixmap(os.path.join(libfolder, f'flags/{lang}.png'))))
    config[key] = lang
    mw.addonManager.writeConfig(__name__, config)


def setup_switch_btn(editor: Editor):
    """ Add a button to switch the layout to the bottom of the AddCards dialog. """

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


def onFocusLost(flag, n, fidx):
    from aqt import mw
    if "reverso" not in n.model()['name'].lower():
        return flag
    srcFields = [WORD]
    dstFields = [CONTEXT]
    for c, name in enumerate(mw.col.models.fieldNames(n.model())):
        for f in srcFields:
            if name == f:
                src = f
                srcIdx = c
        for f in dstFields:
            if name == f:
                dst = f
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
        context_data, counter = fetch_context_data(n[src], learned_lang, native_lang)
        success = counter != 0
        feedback_text = f"Found {counter} sentences{SEPARATOR}{context_data}" if success else\
            f"Word not found in the {LANG_NAMES[learned_lang]} dictionary!<br>" \
            f"Check your speelling and make sure that you chose correct languages<br>" \
            f"For some pairs of languages Reverso doesn't provide good examples." \
            f"In such case, try adjusting the native language, e.g. change it to English."
    n[dst] = feedback_text
    return True


add_reverso_notetype()
addHook('editFocusLost', onFocusLost)
gui_hooks.editor_did_load_note.append(setup_switch_btn)
