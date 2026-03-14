from datetime import datetime

from prompt_toolkit import Application, widgets
from prompt_toolkit.completion import FuzzyCompleter, WordCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import Container, HSplit, Layout

from budgeteer.database import Database
from budgeteer.entities.category import Category
from budgeteer.entities.expense import Expense
from budgeteer.prompts.validators.date_validator import DateValidator
from budgeteer.prompts.validators.int_validator import IntValidator
from budgeteer.prompts.validators.non_empty_validator import NonEmptyValidator
from budgeteer.prompts.validators.price_validator import PriceValidator
from budgeteer.str_utils import date_to_str, str_to_date
from budgeteer.widgets.expenses_table import expenses_table


def select_expense(db: Database, expenses: list[Expense]) -> int | None:
    kb = KeyBindings()

    def str_or_empty(num: int | None) -> str:
        return f"{num}" if num else ""

    prompt_window = widgets.TextArea(
        multiline=False,
        dont_extend_height=True,
        prompt="Select a NUMBER to edit: ",
    )

    default_status = " Select an expense from the table by entering its number"
    status_bar = widgets.Label(default_status)

    categories = db.get_categories()
    category_map = {c.id: c for c in categories}

    layout = Layout(
        HSplit(
            [
                expenses_table(expenses, category_map, indexed=True),
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

    app = Application(full_screen=True, key_bindings=kb, layout=layout)

    return app.run()


def edit_expense(
    database: Database,
    expense: Expense,
    all_expenses: list[Expense],
    categories: list[Category],
    summary: Container,
) -> Expense | None:
    kb = KeyBindings()

    expense_names = list({expense.name for expense in all_expenses})
    name_prompt = widgets.TextArea(
        multiline=False,
        dont_extend_height=True,
        prompt="Expense name: ",
        completer=FuzzyCompleter(WordCompleter(expense_names, sentence=True)),
        text=expense.name,
    )
    name_prompt.buffer.cursor_right(len(name_prompt.text))
    description_prompt = widgets.TextArea(
        multiline=False,
        dont_extend_height=True,
        prompt="Description: ",
        text=expense.description if expense.description else "",
    )
    description_prompt.buffer.cursor_right(len(description_prompt.text))
    price_prompt = widgets.TextArea(
        multiline=False,
        dont_extend_height=True,
        prompt="Price: ",
        text=str(expense.price),
    )
    price_prompt.buffer.cursor_right(len(price_prompt.text))
    date_prompt = widgets.TextArea(
        multiline=False,
        dont_extend_height=True,
        prompt="Date: ",
        text=date_to_str(expense.date()),
    )
    date_prompt.buffer.cursor_right(len(date_prompt.text))
    category_prompt = widgets.TextArea(
        multiline=False,
        dont_extend_height=True,
        prompt="Category: ",
        completer=WordCompleter([c.name for c in categories]),
        text=next((c.name for c in categories if c.id == expense.category_id), ""),
    )
    category_prompt.buffer.cursor_right(len(category_prompt.text))

    default_status = " Use [Tab] for completion. Press [Escape] to exit. Press [Up/Down/CTRL+K/CTRL+J] to navigate field"
    status_bar = widgets.Label(default_status)

    prompts = [
        name_prompt,
        description_prompt,
        price_prompt,
        date_prompt,
        category_prompt,
    ]

    layout = Layout(
        HSplit(
            [
                summary,
                widgets.Frame(body=HSplit(prompts)),
                status_bar,
            ]
        )
    )

    layout.focus(name_prompt)

    @kb.add("c-j")
    @kb.add("down")
    def focus_up(event: KeyPressEvent):
        for i, p in enumerate(prompts):
            if layout.has_focus(p):
                layout.focus(prompts[(i + 1) % len(prompts)])
                return

    @kb.add("c-k")
    @kb.add("up")
    def focus_down(event: KeyPressEvent):
        for i, p in reversed(tuple(enumerate(prompts))):
            if layout.has_focus(p):
                layout.focus(prompts[(i - 1) % len(prompts)])
                return

    @kb.add("enter")
    def submit(event: KeyPressEvent):
        name = name_prompt.text.strip()
        try:
            NonEmptyValidator().validate(Document(name))
        except Exception as e:
            status_bar.text = str(e)
            return

        description = (
            description_prompt.text.strip() if description_prompt.text.strip() else None
        )

        price = price_prompt.text
        try:
            PriceValidator().validate(Document(price))
        except Exception as e:
            status_bar.text = str(e)
            return

        date_str = date_prompt.text
        try:
            DateValidator().validate(Document(date_str))
        except Exception as e:
            status_bar.text = str(e)
            return

        category_str = category_prompt.text.strip()

        if category_str:
            category_match = next(
                (x for x in categories if x.name == category_str), None
            )
            category_id: int
            if category_match is None:
                category = database.new_category(
                    Category(
                        name=category_str, description="", created_at=datetime.now()
                    )
                )
                category_id = category.id
            else:
                category_id = category_match.id

        date = str_to_date(date_str)
        if not date:
            raise RuntimeError(f"Could not parse {date_str} as date")

        event.app.exit(
            result=Expense(
                id=expense.id,
                name=name,
                description=description,
                price=float(price),
                year=date.year,
                month=date.month,
                day=date.day,
                category_id=category_id,
                created_at=expense.created_at,
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


def edit_expenses(db: Database, year: int, month: int):
    all_expenses: list[Expense] = []
    expenses: list[Expense] = []

    def refresh_expenses():
        nonlocal all_expenses, expenses
        all_expenses = db.get_expenses()
        expenses = sorted(
            [e for e in all_expenses if e.year == year and e.month == month],
            key=lambda e: e.date(),
        )

    refresh_expenses()
    expense_index = select_expense(db, expenses)
    while expense_index is not None:
        categories = db.get_categories()
        category_map = {c.id: c for c in categories}

        updated_expense = edit_expense(
            db,
            expense=expenses[expense_index],
            all_expenses=all_expenses,
            categories=categories,
            summary=expenses_table(expenses=expenses, categories=category_map),
        )
        if updated_expense:
            db.update_expense(updated_expense)
            refresh_expenses()

        expense_index = select_expense(db, expenses)
