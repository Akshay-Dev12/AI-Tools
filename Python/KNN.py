from sklearn.neighbors import KNeighborsClassifier
import numpy as np

# features - x - hours studied
x = np.array([[1], [2], [3], [4], [5]])

# y - Labels - passed or fail
y= np.array([0, 0, 1, 1, 1])

# create KNN model, first 3 neigh using eucledean algo. = sqrt of x^2 - y^2
knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(x, y)

# Predict for 3.5 hours
print(knn.predict([[3.5]]))


# Naive bayce
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

# Sample data
texts = [
    "buy cheap meds",      # spam
    "cheap pills",         # spam
    "hello friend",        # not spam
    "let's catch up soon"  # not spam
]

labels = ["spam", "spam", "not spam", "not spam"]

# Create model pipeline: CountVectorizer + Naive Bayes
model = make_pipeline(CountVectorizer(), MultinomialNB())

# Train the model
model.fit(texts, labels)

# Test new message
test_message = ["Hwllo friend"]

# Predict
predicted_label = model.predict(test_message)
print(f"Prediction: {predicted_label[0]}")




