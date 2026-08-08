from prompt_toolkit.validation import ValidationError, Validator


class NonWhitespaceValidator(Validator):
    def validate(self, document):
        text = document.text

        if len(text) and not len(text.strip()):
            raise ValidationError(message="Entry cannot be only whitespace")
