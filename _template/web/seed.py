from sqlmodel import Session

from .database import engine, init_db
from .models import Item


def seed() -> None:
    init_db()
    with Session(engine) as session:
        session.add(Item(name="hello"))
        session.commit()


if __name__ == "__main__":
    seed()
    print("Seeded.")
