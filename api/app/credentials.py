from abc import ABC
from abc import abstractproperty
from typing import Optional
from typing import Set

from pydantic import BaseModel


class CredentialsStatusOut(BaseModel):
    """
    Properties on a BaseModel cannot yet be serialized. Therfore, a ResponseModel class.
    # TODO update when https://github.com/samuelcolvin/pydantic/issues/935 is implemented.
    """

    name: str
    credentials_submitted: bool
    credentials_valid: bool
    credential_fields: Set[str]
    reason: Optional[str] = None


class WalletCredentialsStatus(BaseModel, ABC):
    credentials_submitted: bool = False
    credentials_valid: bool = False

    @abstractproperty
    def name(self) -> str:
        raise NotImplementedError

    @abstractproperty
    def credential_fields(self) -> Set[str]:
        raise NotImplementedError

    def response_model(self) -> CredentialsStatusOut:
        return CredentialsStatusOut(
            name=self.name,
            credentials_submitted=self.credentials_submitted,
            credentials_valid=self.credentials_valid,
            credential_fields=self.credential_fields,
        )
