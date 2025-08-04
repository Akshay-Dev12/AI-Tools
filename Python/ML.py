import pandas as pd
import numpy as np

# create Dataframe
data = {'Name': ['A', 'B', 'C'], 'Score': [90, 98, 70]}
df = pd.DataFrame(data)
print(df.describe())

# Numpy arrays
arr = np.array([[1, 2], [3, 4]])
print(arr.T) # transpose

df = pd.read_csv('https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv')
print(df.head())

# Analyze survival Rate by Gender

surv_by_gender = df.groupby('Sex')['Survived'].mean()
print(surv_by_gender)

import seaborn as sns
import matplotlib.pyplot as plt

# Plot age distribution
sns.histplot(data=df, x='Age', bins=30, kde=True)
plt.title('Age Distribution of Titanic Passengers')
plt.xlabel('Age')
plt.ylabel('Count')
plt.show()

# Create age bins
df['AgeGroup'] = pd.cut(df['Age'], bins=[0, 12, 20, 40, 60, 80], 
                        labels=['Child', 'Teen', 'Adult', 'Middle-aged', 'Senior'])

# Count passengers by age group
age_group_counts = df['AgeGroup'].value_counts().sort_index()
print(age_group_counts)

# Plot
age_group_counts.plot(kind='bar', title='Passenger Count by Age Group')
plt.xlabel("Age Group")
plt.ylabel("Count")
plt.show()


from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# Sample data
X = df[['Age']].fillna(df['Age'].mean())
y = df['Fare']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = LinearRegression()
model.fit(X_train, y_train)

print("Score:", model.score(X_test, y_test))

