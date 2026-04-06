from sqlmodel import Field, SQLModel


class Structure(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    type_acronym: str


class Beneficiary(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    person_first_name: str
    person_last_name: str
    person_phone: str | None = None
    person_email: str | None = None
    person_birthdate: str | None = None
    person_address: str | None = None
    modalite: str | None = None
    structure_referente_id: int | None = Field(default=None, foreign_key="structure.id")
    eligibilites: str | None = None
    nb_prescriptions: int = 0
    diagnostic_data: str | None = None
    date_inscription: str
