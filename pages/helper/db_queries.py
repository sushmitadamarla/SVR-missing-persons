import json
import sqlite3
from sqlmodel import create_engine, Session, select

from pages.helper.data_models import RegisteredCases, PublicSubmissions

# ✅ SQLite database engine (this points to your local file)
sqlite_url = "sqlite:///sqlite_database.db"
engine = create_engine(sqlite_url, echo=False)


# -------------------- Database Setup --------------------
def create_db():
    """Create tables if they don't exist."""
    try:
        RegisteredCases.__table__.create(engine, checkfirst=True)
        PublicSubmissions.__table__.create(engine, checkfirst=True)
    except Exception as e:
        print(f"[DB INIT ERROR] {e}")


# -------------------- Case Registration --------------------
def register_new_case(case_details: RegisteredCases):
    """Register a new case in the database."""
    with Session(engine) as session:
        session.add(case_details)
        session.commit()

def new_public_case(public_case_details: PublicSubmissions):
    """Register a new public submission (spotted face)."""
    with Session(engine) as session:
        session.add(public_case_details)
        session.commit()

# -------------------- Fetch Registered Cases --------------------
def fetch_registered_cases(submitted_by: str = None, status: str = "NF", train_data: bool = False):
    """
    Fetch registered cases. 
    If train_data=True, returns only IDs and embeddings for model training.
    """
    with Session(engine) as session:
        if train_data:
            result = session.exec(
                select(RegisteredCases.id, RegisteredCases.embedding)
                .where(RegisteredCases.status == status)
            ).all()
            return result

        # Normal query (for viewing in Streamlit)
        if status == "All":
            statuses = ["F", "NF"]
        elif status == "Found":
            statuses = ["F"]
        else:
            statuses = ["NF"]

        query = select(
            RegisteredCases.id,
            RegisteredCases.name,
            RegisteredCases.age,
            RegisteredCases.status,
            RegisteredCases.last_seen,
            RegisteredCases.matched_with,
        ).where(RegisteredCases.status.in_(statuses))

        if submitted_by:
            query = query.where(RegisteredCases.submitted_by == submitted_by)

        result = session.exec(query).all()
        return result


# -------------------- Fetch Public Cases --------------------
def fetch_public_cases(train_data: bool = False, status: str = "NF"):
    """Fetch public cases or embeddings for training."""
    with Session(engine) as session:
        if train_data:
            result = session.exec(
                select(PublicSubmissions.id, PublicSubmissions.embedding)
                .where(PublicSubmissions.status == status)
            ).all()
            return result

        result = session.exec(
            select(
                PublicSubmissions.id,
                PublicSubmissions.status,
                PublicSubmissions.location,
                PublicSubmissions.mobile,
                PublicSubmissions.birth_marks,
                PublicSubmissions.submitted_on,
                PublicSubmissions.submitted_by,
            )
        ).all()
        return result


# -------------------- Details and Updates --------------------
def get_registered_case_detail(case_id: str):
    """Fetch details of a registered case by ID."""
    with Session(engine) as session:
        result = session.exec(
            select(
                RegisteredCases.name,
                RegisteredCases.complainant_mobile,
                RegisteredCases.age,
                RegisteredCases.last_seen,
                RegisteredCases.birth_marks,
            ).where(RegisteredCases.id == case_id)
        ).all()
        return result


def get_public_case_detail(case_id: str):
    """Fetch details of a public case by ID."""
    with Session(engine) as session:
        result = session.exec(
            select(
                PublicSubmissions.location,
                PublicSubmissions.submitted_by,
                PublicSubmissions.mobile,
                PublicSubmissions.birth_marks,
            ).where(PublicSubmissions.id == case_id)
        ).all()
        return result


def update_found_status(register_case_id: str, public_case_id: str):
    """Mark both cases as found."""
    with Session(engine) as session:
        reg_case = session.exec(
            select(RegisteredCases).where(RegisteredCases.id == str(register_case_id))
        ).one()
        pub_case = session.exec(
            select(PublicSubmissions).where(PublicSubmissions.id == str(public_case_id))
        ).one()

        reg_case.status = "F"
        reg_case.matched_with = str(public_case_id)
        pub_case.status = "F"

        session.add(reg_case)
        session.add(pub_case)
        session.commit()


# -------------------- Embedding Access --------------------
def get_embedding_for_case(case_id: str):
    """Return the embedding JSON string for a registered case."""
    with Session(engine) as session:
        result = session.exec(
            select(RegisteredCases.embedding).where(RegisteredCases.id == case_id)
        ).first()
        return result


def get_embedding_for_public_case(case_id: str):
    """Return the embedding JSON string for a public case."""
    with Session(engine) as session:
        result = session.exec(
            select(PublicSubmissions.embedding).where(PublicSubmissions.id == case_id)
        ).first()
        return result


# -------------------- Delete Utilities --------------------
def delete_registered_case(case_id: str):
    with Session(engine) as session:
        case_to_delete = session.get(RegisteredCases, case_id)
        if case_to_delete:
            session.delete(case_to_delete)
            session.commit()


def delete_public_case(case_id: str):
    with Session(engine) as session:
        case_to_delete = session.get(PublicSubmissions, case_id)
        if case_to_delete:
            session.delete(case_to_delete)
            session.commit()

def get_registered_cases_count(submitted_by: str, status: str):
    """Return all registered cases for a given user and status."""
    from sqlmodel import Session, select
    with Session(engine) as session:
        result = session.exec(
            select(RegisteredCases)
            .where(RegisteredCases.submitted_by == submitted_by)
            .where(RegisteredCases.status == status)
        ).all()
        return result


# -------------------- Main Test --------------------
if __name__ == "__main__":
    create_db()
    r = fetch_registered_cases(train_data=True)
    print(r)
