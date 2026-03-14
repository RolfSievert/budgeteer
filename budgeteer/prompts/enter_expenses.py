from datetime import date, datetime
from typing import NamedTuple

from prompt_toolkit import Application, widgets
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import Container, HSplit, Layout

from budgeteer.database import Database
from budgeteer.entities.category import Category
from budgeteer.entities.expense import Expense
from budgeteer.prompts.validators.date_validator import DateValidator
from budgeteer.prompts.validators.non_empty_validator import NonEmptyValidator
from budgeteer.prompts.validators.price_validator import PriceValidator
from budgeteer.str_utils import str_to_date
from budgeteer.widgets.expenses_table import expenses_table


def prompt_category(
    database: Database, default: int | None, summary: Container
) -> Category | None:
    kb = KeyBindings()

    categories = database.get_categories()
    default_category = next((x.name for x in categories if x.id == default), "")
    prompt_window = widgets.TextArea(
        multiline=False,
        dont_extend_height=True,
        prompt="Expense category: ",
        completer=WordCompleter([x.name for x in categories]),
        text=default_category,
    )
    prompt_window.buffer.cursor_right(len(prompt_window.text))

    default_status = " Use [Tab] for completion. Press [Escape] to exit."
    status_bar = widgets.Label(default_status)

    layout = Layout(
        HSplit(
            [
                summary,
                widgets.Frame(body=prompt_window),
                status_bar,
            ]
        )
    )

    @kb.add("enter")
    def submit(event: KeyPressEvent):
        text = prompt_window.text.strip() if prompt_window.text.strip() else None
        if text is None:
            event.app.exit(result=None)
            return

        category = next((x for x in categories if x.name == text), None)
        if category is None:
            category = database.new_category(
                Category(name=text, description="", created_at=datetime.now())
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


def prompt_day(year: int, month: int, day: int, summary: Container) -> date:
    kb = KeyBindings()

    def str_or_empty(num: int | None) -> str:
        return f"{num}" if num else ""

    prompt_window = widgets.TextArea(
        multiline=False,
        dont_extend_height=True,
        prompt=f"Date: {year}-{month}-",
        text=str_or_empty(day),
    )
    prompt_window.buffer.cursor_right(len(prompt_window.text))

    default_status = " Enter a price"
    status_bar = widgets.Label(default_status)

    layout = Layout(
        HSplit(
            [
                summary,
                widgets.Frame(body=prompt_window),
                status_bar,
            ]
        )
    )

    @kb.add("enter")
    def submit(event: KeyPressEvent):
        text = f"{year}-{month}-{prompt_window.text}"
        try:
            DateValidator().validate(Document(text))
        except Exception as e:
            status_bar.text = str(e)

        event.app.exit(result=str_to_date(text))

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

    app = Application(full_screen=True, key_bindings=kb, layout=layout)

    return app.run()


def prompt_price(summary: Container) -> float | int:
    kb = KeyBindings()

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
                summary,
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


class ExpenseNameResult(NamedTuple):
    name: str
    description: str | None
    category_id: int | None


def prompt_expense_name(
    expenses: list[Expense], summary: Container
) -> ExpenseNameResult | None:
    kb = KeyBindings()

    expense_names = list({expense.name for expense in expenses})
    name_prompt = widgets.TextArea(
        multiline=False,
        dont_extend_height=True,
        prompt="Expense name: ",
        completer=WordCompleter(expense_names),
    )
    description_prompt = widgets.TextArea(
        multiline=False,
        dont_extend_height=True,
        prompt="Description: ",
        completer=WordCompleter(expense_names),
    )
    default_status = " Use [Tab] for completion. Press [Escape] to exit. Press [Up/Down/CTRL+K/CTRL+J] to enter description"
    status_bar = widgets.Label(default_status)

    layout = Layout(
        HSplit(
            [
                summary,
                widgets.Frame(body=HSplit([name_prompt, description_prompt])),
                status_bar,
            ]
        )
    )

    layout.focus(name_prompt)

    @kb.add("c-j")
    @kb.add("c-k")
    @kb.add("up")
    @kb.add("down")
    def change_focus(event: KeyPressEvent):
        if layout.has_focus(description_prompt):
            layout.focus(name_prompt)
        elif layout.has_focus(name_prompt):
            layout.focus(description_prompt)

    @kb.add("enter")
    def submit(event: KeyPressEvent):
        try:
            NonEmptyValidator().validate(Document(name_prompt.text))
        except Exception as e:
            status_bar.text = str(e)
            return

        matches = [x for x in expenses if x.name == name_prompt.text]
        latest_expense = max(
            matches,
            key=lambda e: e.created_at,
            default=None,
        )
        category = latest_expense.category_id if latest_expense else None
        description = (
            description_prompt.text.strip() if description_prompt.text.strip() else None
        )

        event.app.exit(
            result=ExpenseNameResult(
                name=name_prompt.text,
                description=description,
                category_id=category,
            )
        )

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
        all_expenses = database.get_expenses()
        expenses = [e for e in all_expenses if e.year == year and e.month == month]
        expenses = sorted(expenses, key=lambda e: e.date())
        categories = database.get_categories()
        category_map = {c.id: c for c in categories}

        summary = expenses_table(expenses, category_map)
        expense = prompt_expense_name(all_expenses, summary=summary)
        # exit if expense name was None
        if not expense:
            return

        expense_price = prompt_price(summary=summary)
        expense_date = prompt_day(year=year, month=month, day=day, summary=summary)
        expense_category = prompt_category(
            database, default=expense.category_id, summary=summary
        )

        database.new_expense(
            Expense(
                name=expense.name,
                price=expense_price,
                year=expense_date.year,
                month=expense_date.month,
                day=expense_date.day,
                category_id=expense_category.id
                if expense_category is not None
                else None,
                created_at=datetime.now(),
                description=expense.description,
            )
        )
        day = expense_date.day
