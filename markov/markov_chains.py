import random
from typing import Any


def read_until_eol(file, eol_sequence: str):
    buffer = ""
    while True:
        char = file.read(1)
        if not char:
            break
        buffer += char
        if buffer.endswith(eol_sequence):
            break
    return buffer


class _WeightedCollection:

    _collection: dict[str, int]
    _total_instances: int = 0 

    def __init__(self):
        self._collection = {}

    def add_word(self, word: str) -> None:
        if word in self._collection.keys():
            self._collection[word] += 1
        else:
            self._collection[word] = 1
        self._total_instances += 1
        
    def get_word(self) -> str:
        if not self._collection:
            return ""
        selected_value: int = random.randint(1, self._total_instances)
        sum: int = 0
        for word, value in self._collection.items():
            sum += value
            if sum >= selected_value:
                return word
        return "" 

    def __repr__(self):
        return self.__str__()

    def __str__(self) -> str:
        return f"{self._total_instances} instances | {self._collection}"


class Generator:

    _single_word_lut: dict[str, _WeightedCollection]
    _double_word_lut: dict[tuple[str, str], _WeightedCollection]

    def __init__(self):
        self._single_word_lut = {}
        self._double_word_lut = {}

    def ingest_dataset(self, filename: str, eol_sequence: str = "\n") -> None:
        with open(filename + ".txt", "r") as f:
            while True:
                line: str = read_until_eol(f, eol_sequence)
                # print(f"read line: {line}")
                if not line:
                    break
                line = line.lower()
                split_string: list[str] = line.split()
                # split_string.append("\n")
                if len(split_string) < 2:
                    continue
                _add_to_lut(self._single_word_lut, split_string[0], split_string[1])
                if len(split_string) < 3:
                    continue
                for i in range(2, len(split_string)):
                    word: str = split_string[i]
                    previous_word: str = split_string[i - 1]
                    pre_previous_word: str = split_string[i - 2]
                    _add_to_lut(self._single_word_lut, previous_word, word)
                    _add_to_lut(self._double_word_lut, (pre_previous_word, previous_word), word)

    def get_words_collection(self, words_list: list[str]) -> _WeightedCollection | None:
        if len(words_list) < 2:
            return self._single_word_lut.get(words_list[-1])
        result: _WeightedCollection = self._double_word_lut.get((words_list[-2], words_list[-1]))
        if result:
            return result
        return self._single_word_lut.get(words_list[-1])

    def get_random_word(self):
        return random.choice(list(self._single_word_lut.keys()))

    def generate_next_word(self, words_list: list[str]) -> str:
        collection: _WeightedCollection | None = self.get_words_collection(words_list)
        if collection:
            return collection.get_word()
        return "\n"

    def __repr__(self):
            return self.__str__()

    def __str__(self) -> str:
        return f"1wlut: {self._single_word_lut}\n2wlut: {self._double_word_lut}"


def _add_to_lut(lut: dict[Any, _WeightedCollection], key: Any, word: str) -> None:
    # print(f"adding word \"{word}\" to key \"{key}\"")
    if key not in lut.keys():
        lut[key] = _WeightedCollection()
    lut[key].add_word(word)


if __name__ == "__main__":
    generator: Generator = Generator()
    generator.ingest_dataset("bestemmie_sample")
    words: list[str] = [generator.get_random_word()]
    while True:
        word = generator.generate_next_word(words)
        words.append(word)
        if word == "\n":
            break
    print(" ".join(words))
