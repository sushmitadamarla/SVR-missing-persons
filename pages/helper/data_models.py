from uuid import uuid4
from datetime import datetime
from sqlmodel import Field, create_engine, SQLModel
from typing import Optional

class RegisteredCases(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: str = Field(default=None, primary_key=True)
    submitted_by: str
    name: str
    fathers_name: str
    age: int
    complainant_mobile: str
    complainant_name: str
    adhaar_card: Optional[str] = None
    birth_marks: Optional[str] = None
    address: Optional[str] = None
    last_seen: Optional[str] = None
    description: Optional[str] = None
    face_mesh: Optional[str] = None
    embedding: Optional[str] = None   # ✅ NEW — stores InsightFace embedding
    status: str = "NF"
    matched_with: Optional[str] = None


class PublicSubmissions(SQLModel, table=True):
    __table_args__ = {"extend_existing": True} 
    id: str = Field(default=None, primary_key=True)
    submitted_by: Optional[str] = None
    mobile: Optional[str] = None
    location: Optional[str] = None
    birth_marks: Optional[str] = None
    face_mesh: Optional[str] = None
    embedding: Optional[str] = None   # ✅ NEW — stores embedding
    status: str = "NF"
    submitted_on: datetime = Field(default_factory=datetime.now)


if __name__ == "__main__":
    sqlite_url = "sqlite:///example.db"
    engine = create_engine(sqlite_url)

    RegisteredCases.__table__.create(engine)
    PublicSubmissions.__table__.create(engine)
