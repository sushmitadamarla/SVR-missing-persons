import os
import json
import pickle
import traceback
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.impute import SimpleImputer
from pages.helper import db_queries


def get_train_data(submitted_by: str):
    """
    Fetch InsightFace embeddings for all registered cases.
    """
    try:
        result = db_queries.get_training_data(submitted_by)

        # Expect columns: label, embedding
        d1 = pd.DataFrame(result, columns=["label", "embedding"])
        d1["embedding"] = d1["embedding"].apply(lambda x: json.loads(x))

        # Convert list of embeddings into numeric columns
        d2 = pd.DataFrame(d1.pop("embedding").values.tolist(), index=d1.index)
        df = d1.join(d2)

        # Handle missing or NaN values safely
        df = df.dropna()

        return df["label"], df.drop("label", axis=1)

    except Exception as e:
        traceback.print_exc()
        raise e


def train(submitted_by: str):
    """
    Train a KNN model using InsightFace embeddings.
    """
    model_name = "classifier.pkl"
    if os.path.isfile(model_name):
        os.remove(model_name)

    try:
        labels, embeddings = get_train_data(submitted_by)
        if len(labels) == 0:
            return {"status": False, "message": "No cases submitted by this user"}

        # Impute any remaining NaNs
        imputer = SimpleImputer(strategy="mean")
        embeddings = imputer.fit_transform(embeddings)

        # Encode labels
        le = LabelEncoder()
        encoded_labels = le.fit_transform(labels)

        # Train KNN classifier
        classifier = KNeighborsClassifier(
            n_neighbors=min(3, len(labels)), algorithm="auto", weights="distance"
        )
        classifier.fit(embeddings, encoded_labels)

        with open(model_name, "wb") as file:
            pickle.dump((le, classifier), file)

        return {"status": True, "message": "Model trained successfully"}

    except Exception as e:
        traceback.print_exc()
        return {"status": False, "message": str(e)}


if __name__ == "__main__":
    result = train("admin")
    print(result)
