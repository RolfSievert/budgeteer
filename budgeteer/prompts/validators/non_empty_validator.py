from prompt_toolkit.validation import ValidationError, Validator


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
