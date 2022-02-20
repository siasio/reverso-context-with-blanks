# reverso-context-with-blanks
 Anki add-on for getting sentences from reverso

When adding new cards, you will get an option to automatically fetch a fixed number of sample sentences from the Reverso website (https://context.reverso.net/). To do so, just create a new card type with the word "reverso" in the type name, and fields "Word" and "Context". For such a card type, when you enter a word you are interested in in the "Word" field, and then click anywhere else (stop the mouse focus on this field), the sentences will automatically appear in the "Context" field.

To get nice cards out of this, you need to adjust the card template. You can find the html that you should include in the template in the folder of the add-on. The folder is located in the Anki2/addon21 directory (perhaps, something like "C:\Users\User\AppData\Roaming\Anki2\addons21\reverso-context-with-blanks"). Please, go to that folder and open the "front_template.html", "back_template.html", and "card_style.css" with any text editor, for example with Notepad.

When creating new reverso cards, in the "add card" window, press on the button "Cards.." in the upper-left corner. Copy the templates and the card style into the corresponding fields. Thanks to this template, when studying a card, you will always be presented with a cloze task made out of a random sentence. You will also see a button "Check native language" to see a translation of the sentence.

At the bottom of the "add card" window, you can adjust the language which you are learning and your native language.

You can adjust the number of sentences fetched from Reverso and the languages icons shown in the list of languages in the add-on's config. The config can be accessed from the add-on window which appears when you press on Tools->Add-ons

This is my first add-on. I hope it will help you learning languages by providing you with more versatile tasks than usual anki cards. Please, report any problems you encounter with the add-on.
