from base64 import b64encode, b64decode

from pydantic import BaseModel, computed_field, model_serializer

from app.lib.exceptions import ClientError


class DocumentSequence(BaseModel):
    seq_no: int
    primary_term: int

    def __init__(self, *args, sequence_str: str = None, seq_no: int = None, primary_term: int = None, **kwargs):
        if sequence_str:
            try:
                seq, term = b64decode(sequence_str).decode("ascii").split(",")
            except Exception:
                raise ClientError("Invalid sequence string provided. Decoding failed.")

            kwargs["seq_no"] = int(seq)
            kwargs["primary_term"] = int(term)

        elif isinstance(seq_no, int) and isinstance(primary_term, int):
            kwargs["seq_no"] = seq_no
            kwargs["primary_term"] = primary_term

        else:
            raise ClientError("Sequence initialization missing required arguments.")

        super().__init__(**kwargs)

    @computed_field(return_type=str)
    @property
    def string(self):
        return f"{self.seq_no},{self.primary_term}"

    @computed_field(return_type=str)
    @property
    def encoded_string(self):
        return b64encode(self.string.encode())

    @model_serializer()
    def serialize_model(self):
        return self.encoded_string
