from datetime import date

from prompt_toolkit import Application, widgets
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import HSplit, Layout

from budgeteer.database import Database
from budgeteer.prompts.validators.month_validator import MonthValidator


def month_selection(db: Database) -> date | None:
    """
    Which month was selected and if it is a new month
    """
    months = list({f"{e.year}-{e.month}" for e in db.get_expenses()})
    months = sorted(months)

    kb = KeyBindings()

    newline = "\n"
    months_summary = "Previous months:\n - " + (newline + " - ").join(months)

    big_window = widgets.Label(months_summary, dont_extend_height=False)
    prompt_window = widgets.TextArea(
        multiline=False,
        dont_extend_height=True,
        prompt="Enter a month: ",
        completer=WordCompleter(months),
    )
    default_status = " Select an existing month or enter a new month 'year-month'"
    status_bar = widgets.Label(default_status)

    @kb.add("enter")
    def submit(event: KeyPressEvent):
        try:
            MonthValidator().validate(Document(prompt_window.text))
            month = date.strptime(prompt_window.text, "%Y-%m")  # ty:ignore[unresolved-attribute]
            event.app.exit(result=month)
        except Exception as e:
            status_bar.text = str(e)

    @kb.add("escape")
    @kb.add("c-c")
    @kb.add("c-d")
    @kb.add("c-q")
    def quit(event: KeyPressEvent):
        event.app.exit(result=None)

    @kb.add("0")
    @kb.add("1")
    @kb.add("2")
    @kb.add("3")
    @kb.add("4")
    @kb.add("5")
    @kb.add("6")
    @kb.add("7")
    @kb.add("8")
    @kb.add("9")
    @kb.add("-")
    def number(event: KeyPressEvent):
        prompt_window.text += event.data
        prompt_window.buffer.cursor_right(len(prompt_window.text))
        status_bar.text = default_status

    @kb.add("backspace")
    def erase(event: KeyPressEvent):
        prompt_window.text = prompt_window.text[:-1]
        prompt_window.buffer.cursor_right(len(prompt_window.text))
        status_bar.text = default_status

    @kb.add("<any>")
    def swallow_keypress(event: KeyPressEvent):
        pass

    layout = Layout(
        HSplit(
            [
                big_window,
                widgets.Frame(body=prompt_window),
                status_bar,
            ]
        )
    )

    app = Application(full_screen=True, key_bindings=kb, layout=layout)

    result = app.run()

    return result
