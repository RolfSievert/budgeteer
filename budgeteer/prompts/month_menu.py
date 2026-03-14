from prompt_toolkit import Application, widgets
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import HSplit, Layout

from budgeteer.database import Database
from budgeteer.prompts.month_menu_options import MonthMenuOptions
from budgeteer.widgets.expenses_table import expenses_table


def month_menu(db: Database, year: int, month: int) -> MonthMenuOptions | None:
    add_expenses_option = (MonthMenuOptions.add_expenses, "add expenses")
    edit_expenses_option = (MonthMenuOptions.edit_expenses, "edit expenses")
    exit_menu_option = (MonthMenuOptions.exit_menu, "exit menu")

    descriptions = {
        MonthMenuOptions.add_expenses: "Add expenses to this month",
        MonthMenuOptions.edit_expenses: "Edit this months expenses",
        MonthMenuOptions.exit_menu: "Exit menu",
    }

    kb = KeyBindings()

    options = [add_expenses_option, edit_expenses_option, exit_menu_option]
    prompt_window = widgets.RadioList(
        options,
        select_on_focus=True,
        open_character="",
        close_character="",
        select_character=">>",
        show_cursor=False,
    )
    status_bar = widgets.Label(" " + descriptions[options[0][0]])

    # RadioList swallows events, eager takes the events first
    @kb.add("enter", eager=True)
    def submit(event: KeyPressEvent):
        event.app.exit(result=prompt_window.current_value)

    @kb.add("escape")
    @kb.add("c-c")
    @kb.add("c-d")
    @kb.add("c-q")
    def quit(event: KeyPressEvent):
        event.app.exit(result=None)

    @kb.add("up", eager=True)
    @kb.add("k", eager=True)
    def cursor_up(event: KeyPressEvent):
        i = next(
            i
            for i, x in enumerate(prompt_window.values)
            if x[0] == prompt_window.current_value
        )
        prompt_window.current_value = prompt_window.values[i - 1 if i > 0 else 0][0]
        status_bar.text = " " + descriptions[prompt_window.current_value]
        return True

    @kb.add("down", eager=True)
    @kb.add("j", eager=True)
    def cursor_down(event: KeyPressEvent):
        i = next(
            i
            for i, x in enumerate(prompt_window.values)
            if x[0] == prompt_window.current_value
        )
        values_max = len(prompt_window.values) - 1
        prompt_window.current_value = prompt_window.values[
            i + 1 if i < values_max else values_max
        ][0]
        status_bar.text = " " + descriptions[prompt_window.current_value]
        return True

    expenses = [e for e in db.get_expenses() if e.year == year and e.month == month]
    categories = {c.id: c for c in db.get_categories()}
    layout = Layout(
        HSplit(
            [
                expenses_table(expenses=expenses, categories=categories, kb=kb),
                widgets.Frame(body=prompt_window),
                status_bar,
            ]
        )
    )

    app = Application(
        full_screen=True, key_bindings=kb, layout=layout, mouse_support=True
    )

    result = app.run()

    return result
