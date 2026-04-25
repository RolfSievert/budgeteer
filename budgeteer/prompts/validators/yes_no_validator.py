from prompt_toolkit.validation import ValidationError, Validator


class YesNoValidator(Validator):
    def validate(self, document):
        text: str = document.text

        if not len(text):
            raise ValidationError(message="Entry cannot be empty")

        if not len(text.strip()):
            raise ValidationError(message="Entry cannot be only whitespace")

        if len(text.lstrip()) != len(text):
            raise ValidationError(message="Entry cannot have leading whitespace")

        if len(text.rstrip()) != len(text):
            raise ValidationError(message="Entry cannot have trailing whitespace")

        if not (text.lower() in "no" or text.lower() in "yes"):
            raise ValidationError(message="Entry has to be either [no] or [yes]")

    def try_parse_bool(text: str) -> bool | None:
        if text.lower() in "no":
            return False
        elif text.lower() in "yes":
            return True
        else:
            return None
