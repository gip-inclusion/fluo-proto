from sqlmodel import Field, SQLModel


class Structure(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    type: str
    address: str
    city: str
    # Structure-level contact means. A professional may still expose their own.
    phone: str | None = None
    email: str | None = None
    has_form: bool = False
    has_agenda: bool = False


class Professional(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    role: str
    structure_id: int = Field(foreign_key="structure.id")
    phone: str | None = None
    email: str | None = None
    has_form: bool = False
    has_agenda: bool = False
