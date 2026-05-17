from sqlmodel import SQLModel, create_engine
from pages.helper.data_models import RegisteredCases, PublicSubmissions

# Path to your SQLite DB
sqlite_url = "sqlite:///sqlite_database.db"
engine = create_engine(sqlite_url)

def create_tables():
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    create_tables()
    print("Tables created successfully!")
