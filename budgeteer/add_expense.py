from database import Category
from database import Expense
from prompt_toolkit.validation import Validator, ValidationError
from database import Expenses
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import prompt


class NonEmptyValidator(Validator):
    def validate(self, document):
        text = document.text

        if not len(text):
            raise ValidationError(message="Entry cannot be empty")

        if not len(text.strip()):
            raise ValidationError(message="Entry cannot be only whitespace")

        if len(text.lstrip()) != len(text):
            raise ValidationError(message="Entry cannot have leading whitespace")

        if len(text.rstrip()) != len(text):
            raise ValidationError(message="Entry cannot have trailing whitespace")


def select_category(database: Expenses, default: int | None = None) -> Category:
    categories = database.get_categories()
    completer = WordCompleter([x.name for x in categories])
    default_category = next((x.name for x in categories if x.id == default), "")
    result = prompt(
        message="Enter a category: ",
        completer=completer,
        default=default_category,
        validator=NonEmptyValidator(),
    )

    category = next((x for x in categories if x.name == result), None)

    if category is None:
        category = database.new_category(result, "")

    return category


def create_expense(database: Expenses) -> Expense:
    expenses = database.get_expenses()
    completer = WordCompleter([expense.name for expense in expenses])
    result = prompt(
        message="Enter an expense: ", completer=completer, validator=NonEmptyValidator()
    )

    expense = next((x for x in expenses if x.name == result), None)
    category = expense.category_id if expense is not None else None

    new_expense = database.new_expense(result, category)

    return new_expense


def add_expenses(database: Expenses) -> None:
    expense = create_expense(database)
    category = select_category(database, default=expense.category_id)

    if expense.category_id != category.id:
        expense = database.update_expense_category(expense.id, category.id)

    print("Done!")
    print(f"Entered {expense}")
