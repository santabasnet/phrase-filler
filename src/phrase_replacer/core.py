"""
File: utils.py
Author: santa
Project: phrase-filler
Created: 12/31/25 11:40PM
Email: santa.basnet@wiseyak.com
Github: https://github.com/santabasnet
Organization: WiseYak / Integrated ICT
"""

import re
import lmdb
from functools import lru_cache
from typing import List

from phrase_replacer.config import DB_NAME
from phrase_replacer.utils import SPACE


class PhraseFiller:
    _WORD_RE = re.compile(r"\w+")

    @staticmethod
    def open_db(path: str, map_size: int = 1 << 30) -> lmdb.Environment:
        return lmdb.open(path, map_size=map_size, max_dbs=1, create=True)

    @staticmethod
    def load_phrases(env: lmdb.Environment, phrases: dict[str, str]) -> None:
        with env.begin(write=True) as transaction:
            for k, v in phrases.items():
                transaction.put(k.lower().encode(), v.encode())

    @staticmethod
    @lru_cache(maxsize=1000)
    def _get(transaction: lmdb.Transaction, key: str) -> bytes | None:
        return transaction.get(key.encode())

    @staticmethod
    def _replace_tail(tokens: List[str], keys: List[str],
                      transaction: lmdb.Transaction,
                      max_phrase_len: int, accumulator: List[str]) -> List[str]:
        if not tokens:
            return accumulator

        # Collect word tokens (skip punctuation)
        word_tokens = [t for t in tokens if PhraseFiller._WORD_RE.match(t)]
        max_len = min(max_phrase_len, len(word_tokens))

        # Find the longest matching phrase.
        match = next(
            (
                (size, transaction.get(SPACE.join(word_tokens[:size]).lower().encode()))
                for size in range(max_len, 0, -1)
                if size == 1 or any(
                k.startswith(SPACE.join(word_tokens[:size]).lower()) for k in
                keys)
                if
            transaction.get(SPACE.join(word_tokens[:size]).lower().encode())
            ),
            None
        )

        if match:
            size, value = match
            accumulator.append(value.decode())
            return PhraseFiller._replace_tail(tokens[size:], keys,
                                                transaction,
                                                max_phrase_len, accumulator)
        else:
            accumulator.append(tokens[0])
            return PhraseFiller._replace_tail(tokens[1:], keys, transaction,
                                                max_phrase_len, accumulator)

    @staticmethod
    def replace_phrases(sentence: str, env: lmdb.Environment,
                        max_phrase_len: int = 6) -> str:
        # Split sentence into words and punctuation
        tokens = re.findall(r"\w+|[^\w\s]", sentence, re.UNICODE)
        with env.begin(write=False) as transaction:
            keys = [k.decode() for k, _ in transaction.cursor()]
            replaced = PhraseFiller._replace_tail(tokens, keys, transaction,
                                                    max_phrase_len, [])
        return SPACE.join(
            [SPACE + t if re.match(r"\w", t) and i > 0 and re.match(r"\w",
                                                                    replaced[
                                                                        i - 1]) else t
             for i, t in enumerate(replaced)]
        )


# Initialize db environment.
db_env = PhraseFiller.open_db(DB_NAME)
