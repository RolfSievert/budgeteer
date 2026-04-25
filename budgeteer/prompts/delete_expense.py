from prompt_toolkit import Application, widgets
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import Container, HSplit, Layout

from budgeteer.database import Database
from budgeteer.entities.category import Category
from budgeteer.entities.expense import Expense
from budgeteer.prompts.select_expense import select_expense
from budgeteer.prompts.validators.yes_no_validator import YesNoValidator
from budgeteer.str_utils import date_to_str
from budgeteer.widgets.expenses_table import expenses_table


def delete_expense(
    database: Database,
    expense: Expense,
    categories: list[Category],
    summary: Container,
    kb: KeyBindings | None = None,
) -> tuple[bool, Expense] | None:
    kb = KeyBindings() if kb is None else kb

    expense_summary = f"""Expense name: {expense.name}
Description: {expense.description if expense.description else ""}
Price: {str(expense.price)}
Date: {date_to_str(expense.date())}
Category: {next((c.name for c in categories if c.id == expense.category_id), "")}"""
    delete_prompt = widgets.TextArea(
        multiline=False,
        dont_extend_height=True,
        prompt="Permanently delete this entry? [yes]/[no]: ",
    )

    default_status = " Press [Escape] to exit."
    status_bar = widgets.Label(default_status)

    layout = Layout(
        HSplit(
            [
                summary,
                widgets.Frame(widgets.Label(expense_summary)),
                widgets.Frame(delete_prompt),
                status_bar,
            ]
        )
    )

    @kb.add("enter")
    def submit(event: KeyPressEvent):
        delete_entry = delete_prompt.text.strip()
        try:
            YesNoValidator().validate(Document(delete_entry))
        except Exception as e:
            status_bar.text = str(e)
            return

        should_delete = YesNoValidator.try_parse_bool(delete_entry)

        if should_delete:
            database.delete_expense(expense.id)

        event.app.exit(result=(should_delete, expense))

    @kb.add("escape")
    @kb.add("c-c")
    @kb.add("c-d")
    @kb.add("c-q")
    def quit(event: KeyPressEvent):
        event.app.exit(result=None)

    app = Application(
        full_screen=True, key_bindings=kb, layout=layout, mouse_support=True
    )

    return app.run()


def delete_expenses(db: Database, year: int, month: int):
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
    delete_prompt_text = "Select a NUMBER to delete: "
    expense_index = select_expense(db, expenses, prompt=delete_prompt_text)
    while expense_index is not None:
        categories = db.get_categories()
        category_map = {c.id: c for c in categories}

        kb = KeyBindings()
        was_deleted = delete_expense(
            db,
            expense=expenses[expense_index],
            categories=categories,
            summary=expenses_table(expenses=expenses, categories=category_map, kb=kb),
            kb=kb,
        )
        if was_deleted:
            refresh_expenses()

        expense_index = select_expense(db, expenses, prompt=delete_prompt_text)
