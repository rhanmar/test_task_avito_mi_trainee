from pydantic import BaseModel


class CreateSecret(BaseModel):
    """
    Create the secret.

    """

    secret_value: str
    secret_phrase: str


class ValidateSecretPhrase(BaseModel):
    """
    Validate the passed phrase.

    """

    secret_phrase: str
