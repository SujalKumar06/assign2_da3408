import argparse

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

MODEL_VERSION = "v1"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="spam_dataset.csv")
    parser.add_argument("--out", default="model.joblib")
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    X = df["text"]
    y = df["label"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_state, stratify=y
    )

    model = Pipeline([("tfidf", TfidfVectorizer()), ("nb", MultinomialNB())])
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print(f"accuracy={accuracy_score(y_test, preds):.4f}  f1={f1_score(y_test, preds, pos_label='spam'):.4f}")
    print(f"{len(df)} rows, {df['text'].nunique()} unique texts - duplicates span the split, so this is optimistic")

    joblib.dump({"model": model, "labels": sorted(y.unique().tolist()), "model_version": MODEL_VERSION}, args.out)
    print(f"Saved model bundle to {args.out}")


if __name__ == "__main__":
    main()
