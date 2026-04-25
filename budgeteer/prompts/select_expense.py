from prompt_toolkit import Application, widgets
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import HSplit, Layout

from budgeteer.database import Database
from budgeteer.entities.expense import Expense
from budgeteer.prompts.validators.int_validator import IntValidator
from budgeteer.widgets.expenses_table import expenses_table


def select_expense(db: Database, expenses: list[Expense], prompt: str) -> int | None:
    kb = KeyBindings()

    def str_or_empty(num: int | None) -> str:
        return f"{num}" if num else ""

    prompt_window = widgets.TextArea(
        multiline=False,
        dont_extend_height=True,
        prompt=prompt,
    )

    default_status = " Select an expense from the table by entering its number"
    status_bar = widgets.Label(default_status)

    categories = db.get_categories()
    category_map = {c.id: c for c in categories}

    layout = Layout(
        HSplit(
            [
                expenses_table(expenses, category_map, indexed=True, kb=kb),
                widgets.Frame(body=prompt_window),
                status_bar,
            ]
        )
    )

    @kb.add("enter")
    def submit(event: KeyPressEvent):
        try:
            IntValidator().validate(Document(prompt_window.text))
        except Exception as e:
            status_bar.text = str(e)
            return

        index = int(prompt_window.text) - 1
        if index not in range(len(expenses)):
            status_bar.text = f"Index {index + 1} out of range"
            return

        event.app.exit(result=index)

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
    def number(event: KeyPressEvent):
        prompt_window.text += event.data
        prompt_window.buffer.cursor_right(len(prompt_window.text))
        status_bar.text = default_status

    @kb.add("backspace")
    def erase(event: KeyPressEvent):
        prompt_window.text = prompt_window.text[:-1]
        prompt_window.buffer.cursor_right(len(prompt_window.text))
        status_bar.text = default_status

    @kb.add("up")
    @kb.add("k")
    def up(event: KeyPressEvent):
        if not prompt_window.text:
            prompt_window.text = "1"
            prompt_window.buffer.cursor_right(len(prompt_window.text))
            return

        num = int(prompt_window.text)
        if num >= 31:
            num = 1
        else:
            num += 1

        prompt_window.text = str(num)
        prompt_window.buffer.cursor_right(len(prompt_window.text))
        status_bar.text = default_status

    @kb.add("down")
    @kb.add("j")
    def down(event: KeyPressEvent):
        if not prompt_window.text:
            prompt_window.text = "31"
            prompt_window.buffer.cursor_right(len(prompt_window.text))
            return

        num = int(prompt_window.text)
        if num <= 1:
            num = 31
        else:
            num -= 1

        prompt_window.text = str(num)
        prompt_window.buffer.cursor_right(len(prompt_window.text))
        status_bar.text = default_status

    @kb.add("<any>")
    def swallow_keypress(event: KeyPressEvent):
        pass

    app = Application(
        full_screen=True, key_bindings=kb, layout=layout, mouse_support=True
    )

    return app.run()
