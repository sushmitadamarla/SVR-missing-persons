from pages.helper.data_models import RegisteredCases, PublicSubmissions
from sqlmodel import create_engine

engine = create_engine("sqlite:///sqlite_database.db")
RegisteredCases.__table__.create(engine, checkfirst=True)
PublicSubmissions.__table__.create(engine, checkfirst=True)
print("✅ Tables recreated successfully.")
exit()
