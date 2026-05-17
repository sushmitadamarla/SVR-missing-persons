from pages.helper import db_queries
import json

# Fetch one registered and one public case
reg = db_queries.fetch_registered_cases(train_data=True)
pub = db_queries.fetch_public_cases(train_data=True)

print("\n--- REGISTERED CASE ---")
if reg:
    print("ID:", reg[0][0])
    emb = json.loads(reg[0][1])
    print("Embedding length:", len(emb))
    print("First 5 values:", emb[:5])
else:
    print("No registered cases found.")

print("\n--- PUBLIC CASE ---")
if pub:
    print("ID:", pub[0][0])
    emb = json.loads(pub[0][1])
    print("Embedding length:", len(emb))
    print("First 5 values:", emb[:5])
else:
    print("No public cases found.")
