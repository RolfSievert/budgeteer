from prompt_toolkit import Application, widgets
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import HSplit, Layout

from budgeteer.database import Database
from budgeteer.prompts.main_menu_options import MainMenuOptions
from budgeteer.widgets.yearly_summary import yearly_summary


def main_menu(db: Database) -> MainMenuOptions | None:
    add_expenses_option = (MainMenuOptions.add_expenses, "add expenses")
    edit_month_option = (MainMenuOptions.edit_month, "view/edit month")
    quit_option = (MainMenuOptions.quit, "quit")

    descriptions = {
        MainMenuOptions.add_expenses: "Select a month to add expenses to",
        MainMenuOptions.edit_month: "Select a month to edit",
        MainMenuOptions.quit: "Exit the application",
    }

    kb = KeyBindings()

    options = [add_expenses_option, edit_month_option, quit_option]
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

    layout = Layout(
        HSplit(
            [
                yearly_summary(
                    expenses=db.get_expenses(),
                    category_map=db.get_category_map(),
                ),
                widgets.Frame(body=prompt_window),
                status_bar,
            ]
        )
    )

    app = Application(full_screen=True, key_bindings=kb, layout=layout)

    result = app.run()

    return result
