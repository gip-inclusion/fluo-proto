from sqlmodel import Field, SQLModel


class Orientation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    status: str = Field(default="nouvelle")
    created_at: str
    person_first_name: str
    person_last_name: str
    person_phone: str | None = None
    person_email: str | None = None
    person_birthdate: str | None = None
    person_address: str | None = None
    sender_name: str
    sender_type: str
    sender_organization: str | None = None
    sender_email: str | None = None
    sender_message: str | None = None
    modalite: str | None = None
    diagnostic_data: str | None = None


class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    orientation_id: int = Field(foreign_key="orientation.id")
    author_name: str
    content: str
    created_at: str


class HistoryEvent(SQLModel, table=True):
    __tablename__ = "history_event"
    id: int | None = Field(default=None, primary_key=True)
    orientation_id: int = Field(foreign_key="orientation.id")
    event_type: str
    created_at: str
