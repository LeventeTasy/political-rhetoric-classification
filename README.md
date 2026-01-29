# Political Rhetoric Classification

## Description
This project is a machine learning pipeline designed to classify Hungarian-language news articles according to the presence of political rhetoric that could be considered manipulative or propagandistic. It combines a **LinearSVC** and a **GradientBoostingClassifier** in an ensemble to improve classification accuracy. 

The dataset was collected from **December 2025 to January 2026** and focuses on contemporary Hungarian political topics. The model outputs both:
- a binary label (`Neutral rhetoric` / `Propagandistic rhetoric`)  
- a probability score indicating the likelihood of manipulative content.

## Features
- **Text preprocessing:** Hungarian stopwords removal, TF-IDF vectorization.  
- **Ensemble classification:** Voting ensemble of SVC and Gradient Boosting for improved robustness.  
- **Output:** Probability score and predicted class label for each article.

## Usage
```python
from classifier import predict_bias
from joblib import load

url = "https://example.com/article"

loaded_model = load('../../models/ensemble_pipeline_id1_0_89.joblib')

result = predict_bias(loaded_model, url)
print(result)
```
