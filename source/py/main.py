import numpy as np
from joblib import load
from newspaper import Article

# --- CONFIGURATION ---
MODEL_PATH = '../../models/ensemble_pipeline_id1_0_89.joblib'
LABELS = {0: "Independent", 1: "Propaganda"}


def fetch_article_content(url):
    """Downloads and parses the article text from a URL."""
    try:
        article = Article(url)
        article.download()
        article.parse()

        if not article.text:
            return None

        # Combine title and text for better accuracy
        return f"{article.title} {article.text}"
    except Exception as e:
        print(f"Error downloading article: {e}")
        return None


def _calculate_manual_confidence(model, text, predicted_class):
    """
    Fallback method for 'Hard Voting' classifiers that don't support predict_proba().
    It digs into the pipeline to get probability estimates from the underlying estimators.
    """
    try:
        # Assuming the pipeline structure is [Vectorizer, ..., Classifier]
        vectorizer = model.steps[0][1]
        classifier = model.steps[-1][1]

        # Transform text to vector
        X_vec = vectorizer.transform([text])

        internal_probs = []
        if hasattr(classifier, 'estimators_'):
            for estimator in classifier.estimators_:
                try:
                    # Ask each internal estimator for its probability
                    prob = estimator.predict_proba(X_vec)[0][predicted_class]
                    internal_probs.append(prob)
                except AttributeError:
                    continue  # Skip estimators that don't support probability

        if internal_probs:
            return np.mean(internal_probs)

    except Exception as e:
        print(f"Warning: Could not calculate manual confidence: {e}")

    return 1.0  # Default to 100% confidence if calculation fails


def predict_bias(model, input_data):
    """
    Main function to predict if text is Independent or Propaganda.
    Handles both raw text and URLs.
    """
    is_url = "http" in input_data
    text_content = input_data

    # 1. Get Text (if URL)
    if is_url:
        text_content = fetch_article_content(input_data)
        if not text_content:
            return "Error: Could not extract text from URL."

    try:
        # 2. Predict (0 or 1)
        # Note: We pass [text_content] as a list because sklearn expects an iterable
        prediction_idx = model.predict([text_content])[0]

        # 3. Calculate Confidence (Probability)
        confidence = 0.0
        try:
            # Try the standard way (Soft Voting)
            probs = model.predict_proba([text_content])[0]
            confidence = probs[prediction_idx]
        except AttributeError:
            # Fallback to manual calculation (Hard Voting)
            confidence = _calculate_manual_confidence(model, text_content, prediction_idx)

        # 4. Calculate "Propaganda Score" (0.0 - 1.0)
        # If class is 1 (Propaganda), score is confidence.
        # If class is 0 (Independent), score is 1 - confidence.
        propaganda_score = confidence if prediction_idx == 1 else (1 - confidence)

        # 5. Format Output
        label = LABELS.get(prediction_idx, "Unknown")
        score_percent = round(propaganda_score * 100, 2)

        # Add a warning if it's flagged as Propaganda but confidence is low (<50% essentially means the model is split)
        # Note: In binary classification, if confidence for class 1 is < 0.5, it would usually be class 0.
        # But depending on how confidence is calculated above, we might want this check.
        result_msg = f"{label}, {score_percent}% chance of being propaganda"

        if label == "Propaganda" and propaganda_score < 0.5:
            result_msg = f"Suspicious (Uncertain), {score_percent}% chance of being propaganda"

        if is_url:
            result_msg += f" | URL: {input_data}"

        return result_msg

    except Exception as e:
        return f"Prediction Error: {e}"


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print(f"Loading model from {MODEL_PATH}...")
    try:
        loaded_model = load(MODEL_PATH)
        print("Model loaded successfully. Type 'stop' to exit.")

        while True:
            user_input = input("\nEnter text or URL: ")
            if user_input.strip().lower() == "stop":
                break

            result = predict_bias(loaded_model, user_input)
            print(result)
            print("-" * 30)

    except FileNotFoundError:
        print(f"Critical Error: Model file not found at {MODEL_PATH}")
    except Exception as e:
        print(f"Critical Error: {e}")