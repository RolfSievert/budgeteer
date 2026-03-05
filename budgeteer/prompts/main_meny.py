from prompt_toolkit import Application, widgets
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import HSplit, Layout

from budgeteer.database import Database
from budgeteer.prompts.main_menu_options import MainMenuOptions


def main_menu(db: Database) -> MainMenuOptions | None:
    add_expenses_option = (MainMenuOptions.add_expenses, "add expenses")
    quit_option = (MainMenuOptions.quit, "quit")

    kb = KeyBindings()

    big_window = widgets.Label("hello", dont_extend_height=False)
    prompt_window = widgets.RadioList(
        [add_expenses_option, quit_option],
        select_on_focus=True,
        open_character="",
        close_character="",
        select_character=">>",
        show_cursor=False,
    )
    status_bar = widgets.Label("bar")

    # RadioList swallows events, eager takes the events first
    @kb.add("enter", eager=True)
    def submit(event: KeyPressEvent):
        event.app.exit(result=prompt_window.current_value)

    @kb.add("c-c")
    @kb.add("c-d")
    @kb.add("c-q")
    def quit(event: KeyPressEvent):
        event.app.exit(result=None)

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

    if result == add_expenses_option[0]:
        return MainMenuOptions.add_expenses
    elif result == quit_option[0]:
        return MainMenuOptions.quit
    elif result is None:
        return None
    else:
        raise RuntimeError(f"Option {result} is not implemented")
