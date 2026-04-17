import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier

# Load dataset
data = pd.read_csv("data.csv")

# Encode categorical columns
le_transport = LabelEncoder()
le_diet = LabelEncoder()

data['transport'] = le_transport.fit_transform(data['transport'])
data['diet'] = le_diet.fit_transform(data['diet'])

# Features & target
X = data[['distance', 'transport', 'electricity', 'diet']]
y = data['category']

# Train model
model = DecisionTreeClassifier()
model.fit(X, y)

# Prediction function
def predict_category(distance, transport, electricity, diet):
    transport = le_transport.transform([transport])[0]
    diet = le_diet.transform([diet])[0]
    return model.predict([[distance, transport, electricity, diet]])[0]