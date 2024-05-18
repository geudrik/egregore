from fastapi import Query

from app.models.sequence import DocumentSequence


def get_sequence(sequence: str = Query()) -> DocumentSequence:
    return DocumentSequence(sequence_str=sequence)
