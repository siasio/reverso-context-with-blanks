import os, sys

libfolder = os.path.dirname(__file__)
sys.path.insert(0, libfolder)
from aqt import mw
from definitions import *
from reverso_connect import fetch_context_data
config = mw.addonManager.getConfig(reverso_anki_addon_name)


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
        feedback_text = f"Found {counter} sentences{SEPARATOR}{context_data}" if success else \
            f"Word not found in the {LANG_NAMES[learned_lang]} dictionary!<br>" \
            f"Check your speelling and make sure that you chose correct languages<br>" \
            f"For some pairs of languages Reverso doesn't provide good examples." \
            f"In such case, try adjusting the native language, e.g. change it to English."
    n[dst] = feedback_text
    return True
