from typing import NamedTuple


class Category(NamedTuple):
    id: int
    name: str
    description: str


class Expense(NamedTuple):
    id: int
    name: str
    category_id: int | None

    def __str__(self) -> str:
        return (
            f"Expense(id={self.id}, name={self.name}, catogory_id={self.category_id})"
        )


def sample_categories():
    return [
        Category(1, "sport", "sporty stuff"),
        Category(2, "clothes", "on the feet?"),
    ]


def sample_expenses():
    return [
        Expense(1, "sport", 1),
        Expense(2, "clothes", 2),
    ]


class Expenses:
    def get_categories(self) -> list[Category]:
        return sample_categories()

    def new_category(self, name: str, description: str) -> Category:
        print("not implemented")
        return Category(-1, name=name, description=description)

    def get_expenses(self) -> list[Expense]:
        return sample_expenses()

    def new_expense(self, name: str, category: int | None) -> Expense:
        print("not implemented")
        return Expense(-1, name=name, category_id=category)

    def update_expense_category(self, expense_id: int, category_id: int) -> Expense:
        print("not implemented")
        return Expense(expense_id, name="unknown", category_id=category_id)
