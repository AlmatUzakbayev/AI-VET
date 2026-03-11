from pydantic import BaseModel


class UserProfile(BaseModel):
    user_id: str
    role: str = ""
    animal: str = ""

