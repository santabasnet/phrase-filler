"""
File: main.py
Author: santa
Project: phrase-filler
Created: 12/31/25 11:50PM
Email: santa.basnet@wiseyak.com
Github: https://github.com/santabasnet
Organization: WiseYak / Integrated ICT
"""

from phrase_replacer import PhraseFiller
from phrase_replacer.core import db_env


def main() -> None:
    # Load phrases
    PhraseFiller.load_phrases(db_env, {
        "machine learning": "मशीन लर्निङ्ग",
        "deep learning": "डीप लर्निंग",
        "new york": "न्यू योर्क",
        "new york city": "न्यू योर्क शहर",
        "learning": "लर्निङ्ग"
    })

    sentence = "I study machine learning in new york city."
    result = PhraseFiller.replace_phrases(sentence, db_env)
    print("Input :", sentence)
    print("Output:", result)


if __name__ == "__main__":
    main()
