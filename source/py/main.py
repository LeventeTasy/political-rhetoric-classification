from classifier import predict_bias
from joblib import load

# --- CONFIGURATION ---
MODEL_PATH = '../../models/ensemble_pipeline_id1_0_89.joblib'

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