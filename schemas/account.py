from pydantic import BaseModel

class AccountRead(BaseModel):
    id: int
    device_id: int
    username: str
    vault_path: str
    vault_key: str
    is_enabled: bool

    class Config:
        from_attributes = True

class AccountCreate(BaseModel):
    device_id: int
    username: str
    vault_path: str
    vault_key: str
