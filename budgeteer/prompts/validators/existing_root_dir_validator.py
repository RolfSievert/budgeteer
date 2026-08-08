from pathlib import Path

from prompt_toolkit.validation import ValidationError, Validator


class ExistingRootDirValidator(Validator):
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

        path = Path(text)

        if path.is_absolute() and not Path(path.root).exists():
            raise ValidationError(message="Root of absolute path does not exist")

        if path.is_absolute() and not Path(path.root).is_dir():
            raise ValidationError(message="Root of absolute path is not a directory")
