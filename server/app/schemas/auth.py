from pydantic import BaseModel


class SocialLoginRequest(BaseModel):
    code: str  # authorization_code from client SDK


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str
