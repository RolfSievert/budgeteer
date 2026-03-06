from datetime import date, datetime

from prompt_toolkit import Application, widgets
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import HSplit, Layout

from budgeteer.database import Database
from budgeteer.models.category import Category
from budgeteer.models.expense import Expense
from budgeteer.prompts.validators.date_validator import DateValidator
from budgeteer.prompts.validators.non_empty_validator import NonEmptyValidator
from budgeteer.prompts.validators.price_validator import PriceValidator
from budgeteer.str_utils import str_to_date


def expenses_summary(database: Database, year: int, month: int) -> str:
    expenses = database.get_expenses()
    expenses = (e for e in expenses if e.year == year and e.month == month)
    expenses = sorted(expenses, key=lambda e: e.date())
    return "\n".join(str(e) for e in expenses)


def summary_window(summary: str) -> widgets.Label:
    return widgets.Label(summary, dont_extend_height=False)


def prompt_expense_category(
    database: Database, default: int | None, summary: str
) -> Category | None:
    kb = KeyBindings()

    big_window = summary_window(summary)

    categories = database.get_categories()
    default_category = next((x.name for x in categories if x.id == default), "")
    prompt_window = widgets.TextArea(
        multiline=False,
        dont_extend_height=True,
        prompt="Expense category: ",
        completer=WordCompleter([x.name for x in categories]),
        text=default_category,
    )
    default_status = " Use [Tab] for completion. Press [Escape] to exit."
    status_bar = widgets.Label(default_status)

    layout = Layout(
        HSplit(
            [
                big_window,
                widgets.Frame(body=prompt_window),
                status_bar,
            ]
        )
    )

    @kb.add("enter")
    def submit(event: KeyPressEvent):
        try:
            NonEmptyValidator().validate(Document(prompt_window.text))
        except Exception as e:
            status_bar.text = str(e)
            return

        category = next((x for x in categories if x.name == prompt_window.text), None)
        if category is None:
            category = database.new_category(
                Category(
                    name=prompt_window.text, description="", created_at=datetime.now()
                )
            )
        event.app.exit(result=category)

    @kb.add("escape")
    @kb.add("c-c")
    @kb.add("c-d")
    @kb.add("c-q")
    def quit(event: KeyPressEvent):
        event.app.exit(result=None)

    app = Application(full_screen=True, key_bindings=kb, layout=layout)

    return app.run()


def prompt_expense_date(year: int, month: int, day: int, summary: str) -> date:
    kb = KeyBindings()

    big_window = summary_window(summary)

    def str_or_empty(num: int | None) -> str:
        return f"{num}" if num else ""

    prompt_window = widgets.TextArea(
        multiline=False,
        dont_extend_height=True,
        prompt="Date: ",
        text=f"{(f'{year}-{month}-{str_or_empty(day)}' if month else f'{year}-') if year else ''}",
    )
    default_status = " Enter a price"
    status_bar = widgets.Label(default_status)

    layout = Layout(
        HSplit(
            [
                big_window,
                widgets.Frame(body=prompt_window),
                status_bar,
            ]
        )
    )

    @kb.add("enter")
    def submit(event: KeyPressEvent):
        try:
            DateValidator().validate(Document(prompt_window.text))
        except Exception as e:
            status_bar.text = str(e)

        event.app.exit(result=str_to_date(prompt_window.text))

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

    app = Application(full_screen=True, key_bindings=kb, layout=layout)

    return app.run()


def prompt_expense_price(summary: str) -> float | int:
    kb = KeyBindings()

    big_window = summary_window(summary)

    prompt_window = widgets.TextArea(
        multiline=False,
        dont_extend_height=True,
        prompt="Price: ",
    )
    default_status = " Enter a price"
    status_bar = widgets.Label(default_status)

    layout = Layout(
        HSplit(
            [
                big_window,
                widgets.Frame(body=prompt_window),
                status_bar,
            ]
        )
    )

    @kb.add("enter")
    def submit(event: KeyPressEvent):
        try:
            PriceValidator().validate(Document(prompt_window.text))
            event.app.exit(result=prompt_window.text)
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
    @kb.add(".")
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

    app = Application(full_screen=True, key_bindings=kb, layout=layout)

    return app.run()


def prompt_expense_name(
    database: Database, summary: str
) -> tuple[str, int | None] | None:
    kb = KeyBindings()

    big_window = summary_window(summary)

    expenses = database.get_expenses()
    expense_names = list({expense.name for expense in expenses})
    prompt_window = widgets.TextArea(
        multiline=False,
        dont_extend_height=True,
        prompt="Expense name: ",
        completer=WordCompleter(expense_names),
    )
    default_status = " Use [Tab] for completion. Press [Escape] to exit."
    status_bar = widgets.Label(default_status)

    layout = Layout(
        HSplit(
            [
                big_window,
                widgets.Frame(body=prompt_window),
                status_bar,
            ]
        )
    )

    @kb.add("enter")
    def submit(event: KeyPressEvent):
        try:
            NonEmptyValidator().validate(Document(prompt_window.text))
        except Exception as e:
            status_bar.text = str(e)
            return

        matches = [x for x in expenses if x.name == prompt_window.text]
        latest_expense = max(
            matches,
            key=lambda e: e.created_at,
            default=None,
        )
        category = latest_expense.category_id if latest_expense else None

        event.app.exit(result=(prompt_window.text, category))

    @kb.add("escape")
    @kb.add("c-c")
    @kb.add("c-d")
    @kb.add("c-q")
    def quit(event: KeyPressEvent):
        event.app.exit(result=None)

    app = Application(full_screen=True, key_bindings=kb, layout=layout)

    return app.run()


def enter_expenses(database: Database, year: int, month: int) -> None:
    day = 0

    while True:
        summary = expenses_summary(database, year=year, month=month)
        expense_category = prompt_expense_name(database, summary=summary)
        # exit if expense name was None
        if not expense_category:
            return

        expense_name = expense_category[0]
        category_id = expense_category[1]

        expense_price = prompt_expense_price(summary=summary)
        expense_date = prompt_expense_date(
            year=year, month=month, day=day, summary=summary
        )
        expense_category = prompt_expense_category(
            database, default=category_id, summary=summary
        )

        database.new_expense(
            Expense(
                name=expense_name,
                price=expense_price,
                year=expense_date.year,
                month=expense_date.month,
                day=expense_date.day,
                category_id=expense_category.id
                if expense_category is not None
                else None,
                created_at=datetime.now(),
            )
        )
        day = expense_date.day
