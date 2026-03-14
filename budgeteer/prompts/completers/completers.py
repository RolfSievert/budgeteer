from prompt_toolkit.completion import Completer, FuzzyCompleter, WordCompleter


def fuzzy_sentence_completer(sentences: list[str]) -> Completer:
    return FuzzyCompleter(WordCompleter(sentences, sentence=True))
