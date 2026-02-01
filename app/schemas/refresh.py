from pydantic import BaseModel
from uuid import UUID

class RefreshRequest(BaseModel):
    user_id: UUID
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
