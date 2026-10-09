import pandas as pd
from src.preprocess import prepare_text
from transformers import pipeline


def load_sentiment_model():
    classifier = pipeline(
        "text-classification",
        model="oliverguhr/german-sentiment-bert",
        top_k=None
    )
    return classifier

def classify_texts(classifier, texts):

    # batch_size is set to 8 to avoid memory issues with large datasets
    predictions = classifier(texts, batch_size=8)
    rows = []

    for prediction in predictions:
        scores = {
            item["label"]: item["score"]
            for item in prediction
        }

        rows.append({
            "sentiment": max(scores, key=scores.get),
            "p_positive": scores["positive"],
            "p_neutral": scores["neutral"],
            "p_negative": scores["negative"],
            "sentiment_score": scores["positive"] - scores["negative"]
        })

    return rows

def classify_dataframe(df, classifier):
    df = df.copy()

    df["text_clean"] = df["text"].apply(prepare_text)

    predictions = classify_texts(
        classifier,
        df["text_clean"].tolist()
    )

    result_df = pd.DataFrame(predictions, index=df.index)

    return df.join(result_df)