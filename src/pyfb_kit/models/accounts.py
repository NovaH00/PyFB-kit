from pydantic import BaseModel, Field

class Account(BaseModel):
    access_token: str = Field(description="The access token needed to do operation using this account")
    id: str = Field(description="The ID of the account")
    name: str = Field(description="The name of the account")
    tasks: list[str] = Field(description="The roles of CURRENT USER for this account")


