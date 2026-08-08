from pathlib import Path

from prompt_toolkit import Application, widgets
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import HSplit, Layout, VerticalAlign
from prompt_toolkit.validation import ValidationError

from budgeteer.app_data import set_user_settings
from budgeteer.entities.user_settings import UserSettings
from budgeteer.prompts.validators.existing_root_dir_validator import (
    ExistingRootDirValidator,
)


def edit_user_settings(
    user_settings_path: Path,
    user_settings: UserSettings | None,
    kb: KeyBindings | None = None,
) -> UserSettings | None:
    kb = KeyBindings() if kb is None else kb

    db_path_prompt = widgets.TextArea(
        multiline=False,
        dont_extend_height=True,
        prompt="Database path (contains expenses, etc): ",
        text=user_settings.db_path.as_posix() if user_settings else "",
    )
    db_path_prompt.buffer.cursor_right(len(db_path_prompt.text))

    backup_dir_prompt = widgets.TextArea(
        multiline=False,
        dont_extend_height=True,
        prompt="Backup directory (automatic backups on exit): ",
        text=user_settings.backup_dir.as_posix()
        if (user_settings and user_settings.backup_dir)
        else "",
    )
    backup_dir_prompt.buffer.cursor_right(len(backup_dir_prompt.text))

    default_status = (
        " Press [Escape] to exit. Press [Up/Down/CTRL+K/CTRL+J] to navigate field"
    )
    status_bar = widgets.Label(default_status)

    prompts = [
        db_path_prompt,
        backup_dir_prompt,
    ]

    layout = Layout(
        HSplit(
            [
                widgets.Frame(body=HSplit(prompts)),
                status_bar,
            ],
            align=VerticalAlign.BOTTOM,
        )
    )

    layout.focus(prompts[0])

    @kb.add("c-j")
    @kb.add("down")
    def focus_up(_: KeyPressEvent):
        for i, p in enumerate(prompts):
            if layout.has_focus(p):
                layout.focus(prompts[(i + 1) % len(prompts)])
                return

    @kb.add("c-k")
    @kb.add("up")
    def focus_down(_: KeyPressEvent):
        for i, p in reversed(tuple(enumerate(prompts))):
            if layout.has_focus(p):
                layout.focus(prompts[(i - 1) % len(prompts)])
                return

    @kb.add("enter")
    def submit(event: KeyPressEvent):
        db_path_str = db_path_prompt.text.strip()
        try:
            ExistingRootDirValidator().validate(Document(db_path_str))
        except ValidationError as e:
            status_bar.text = f"Database path: {e!s}"
            return

        backup_dir_str = backup_dir_prompt.text
        try:
            ExistingRootDirValidator().validate(Document(backup_dir_str))
        except ValidationError as e:
            status_bar.text = f"Backup dir: {e!s}"
            return

        db_path = Path(db_path_str)
        # create db dir if it does not exist already
        db_path.parent.mkdir(parents=True, exist_ok=True)
        backup_dir = Path(backup_dir_str)

        new_settings = UserSettings(db_path=db_path, backup_dir=backup_dir)

        if not new_settings.is_equal(user_settings):
            new_settings = set_user_settings(
                user_settings_path=user_settings_path, settings=new_settings
            )
        else:
            new_settings = user_settings

        event.app.exit(result=new_settings)

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
