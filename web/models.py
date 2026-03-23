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
    orientation_id: int | None = Field(default=None, foreign_key="orientation.id")
    beneficiaire_id: int | None = Field(default=None, foreign_key="beneficiaire.id")
    author_name: str
    content: str
    created_at: str


class Beneficiaire(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    person_first_name: str
    person_last_name: str
    person_phone: str | None = None
    person_email: str | None = None
    person_birthdate: str | None = None
    person_address: str | None = None
    date_inscription: str
    modalite_ft: str
    referent_name: str
    diagnostic_data: str | None = None


class SentOrientation(SQLModel, table=True):
    __tablename__ = "sent_orientation"
    id: int | None = Field(default=None, primary_key=True)
    beneficiaire_id: int = Field(foreign_key="beneficiaire.id")
    orientation_id: int | None = Field(default=None, foreign_key="orientation.id")
    structure_name: str
    structure_key: str
    solution_title: str
    poste_titre: str | None = None
    status: str = Field(default="en_attente")
    message: str | None = None
    recipient_name: str | None = None
    response_message: str | None = None
    created_at: str


class PlieBeneficiaire(SQLModel, table=True):
    __tablename__ = "plie_beneficiaire"
    id: int | None = Field(default=None, primary_key=True)
    orientation_id: int | None = Field(default=None, foreign_key="orientation.id")
    person_first_name: str
    person_last_name: str
    person_phone: str | None = None
    person_email: str | None = None
    person_birthdate: str | None = None
    person_address: str | None = None
    accompagnateur: str | None = None
    date_entree: str
    diagnostic_data: str | None = None


class HistoryEvent(SQLModel, table=True):
    __tablename__ = "history_event"
    id: int | None = Field(default=None, primary_key=True)
    orientation_id: int = Field(foreign_key="orientation.id")
    event_type: str
    created_at: str
