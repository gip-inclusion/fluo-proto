from sqlmodel import Field, SQLModel


class Prescription(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    beneficiary_id: int = Field(foreign_key="beneficiary.id")
    solution_id: int = Field(foreign_key="solution.id")
    message: str | None = None
    status: str = Field(default="en_attente")
    created_at: str


class Service(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    structure_name: str
    commune: str | None = None
    code_postal: str | None = None
    description: str | None = None
    category: str  # "mobilite", "numerique", "formation", etc.
    category_label: str  # "Mobilité", "Numérique", "Formation", etc.
    thematiques: str | None = None  # original thematiques JSON for reference
    latitude: float | None = None
    longitude: float | None = None
    telephone: str | None = None
    courriel: str | None = None
    contact_nom_prenom: str | None = None
    site_web: str | None = None
    source: str | None = None  # data-inclusion source: "dora", "emplois", etc.
    lien_source: str | None = None  # service page on original source
    lien_mobilisation: str | None = None  # orientation URL (DORA /orienter)


class Solution(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    solution_type: str
    type_label: str
    structure_name: str | None = None
    commune: str | None = None
    code_postal: str | None = None
    description: str | None = None
    conditions_admission: str | None = None
    places_disponibles: int = 0
    age_min: int | None = None
    age_max: int | None = None
    requires_brsa: bool = False
    requires_detld: bool = False
    requires_qpv: bool = False
    requires_rqth: bool = False
    max_diploma_level: int | None = None
    requires_physical: bool = False  # skip if person has health constraint
    requires_autonomy: bool = False  # only for people who are autonomous with a project
    telephone: str | None = None
    courriel: str | None = None
    contact_nom_prenom: str | None = None
    site_web: str | None = None
    rome_code: str | None = None  # main ROME for GEIQ / role matching


class Structure(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    type_acronym: str


class Professional(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    structure_id: int | None = Field(default=None, foreign_key="structure.id")


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
    referent_id: int | None = Field(default=None, foreign_key="professional.id")
    eligibilites: str | None = None
    nb_prescriptions: int = 0
    diagnostic_data: str | None = None
    date_inscription: str
