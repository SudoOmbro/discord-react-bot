import random

from utils.functions import load_words_list


SUBJECTS: list[str] = ["Dio", "Madonna", "Gesu", "Cristo", "Padreterno"]
ADJECTIVES: list[str] = load_words_list("adjectives")
VERBS: list[str] = load_words_list("verbs")


def preprocess_adjectives_list(filename: str):
    result: list[str] = []
    with open(filename + ".txt", "r") as f:
        file_content: str = f.read().lower()
        words: list[str] = file_content.split("\n")
        print(words)
        for word in words:
            if word.endswith("o"):
                result.append(word[:-1] + "@")
            else:
                result.append(word)
    with open(filename + "_processed.txt", "w") as f:
        f.write("\n".join(result))


def generate_bestemmia(subject: str | None = None, iterations: int = 0) -> str:
    if subject is None:
        subject = random.choice(SUBJECTS)
    letter = "o" if subject[-1] not in ["a"] else "a"
    adjective = random.choice(ADJECTIVES)
    if "|" in adjective:
        if letter == "o":
            adjective = adjective.split("|")[0]
        else:
            adjective = adjective.split("|")[1]
    if random.random() < 0.15:
        subject = "cazzo di " + subject
    if iterations > 0:
        second_subject = random.choice(SUBJECTS)
        if random.random() < 0.5:
            conjunction = "della" if second_subject[0] == "M" else "del"
            return f"{subject} {adjective.replace("@", letter)} {conjunction} {generate_bestemmia(subject=second_subject, iterations=iterations-1)}"
        else:
            conjunction = "dalla" if second_subject[0] == "M" else "dal"
            verb = random.choice(VERBS)
            return f"{subject} {adjective.replace("@", letter)} {verb.replace("@", letter)} {conjunction} {generate_bestemmia(subject=second_subject, iterations=iterations-1)}"
    return f"{subject} {adjective.replace("@", letter)}"
