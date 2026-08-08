from prompt_toolkit import Application, widgets
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import HSplit, Layout
from prompt_toolkit.validation import ValidationError

from budgeteer.database import Database
from budgeteer.entities.metadata import Metadata
from budgeteer.prompts.validators.non_whitespace_validator import NonWhitespaceValidator


def edit_start_page_note(
    database: Database,
    kb: KeyBindings | None = None,
) -> str | None:
    kb = KeyBindings() if kb is None else kb

    old_note = database.get_metadata().start_page_note

    note_prompt = widgets.TextArea(
        multiline=True,
        dont_extend_height=False,
        prompt="",
        text=old_note or "",
    )
    newline_count = len(note_prompt.text.splitlines())
    if newline_count > 1:
        note_prompt.buffer.cursor_down(newline_count)

    lines = note_prompt.text.splitlines()
    last_line_length = len(lines[-1]) if len(lines) > 0 else 0
    if last_line_length:
        note_prompt.buffer.cursor_right(last_line_length)
    default_status = " Enter start page note. Press [Escape] to exit, [CTRL+J] to add newlines, and [UP, DOWN] to move line."
    status_bar = widgets.Label(default_status)

    layout = Layout(
        HSplit(
            [
                widgets.Frame(body=note_prompt),
                status_bar,
            ]
        )
    )

    layout.focus(note_prompt)

    @kb.add("c-j")
    def add_newline(_: KeyPressEvent):
        note_prompt.buffer.insert_line_below()

    @kb.add("enter")
    def submit(event: KeyPressEvent):
        try:
            NonWhitespaceValidator().validate(Document(note_prompt.text))
        except ValidationError as e:
            status_bar.text = str(e)
            return

        result = note_prompt.text or None

        if result != old_note:
            database.update_metadata(Metadata(start_page_note=result))

        event.app.exit(result=result)

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
