
def load_words_list(filename: str) -> list[str]:
    with open(filename + ".txt") as f:
        return f.read().split("\n")
