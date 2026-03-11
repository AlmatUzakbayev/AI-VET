from pydantic import BaseModel, Field


class UserInput(BaseModel):
    user_text: str
    user_id: str


class AppState(BaseModel):
    user_statuses: dict[str, dict] = Field(default_factory=dict)
    conversations: dict[str, dict] = Field(default_factory=dict)

