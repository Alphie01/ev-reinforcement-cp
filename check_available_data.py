# Data Analysis
import pandas as pd

# Modelling
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Set pandas options
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option('display.precision', 4)
pd.set_option('display.float_format', lambda x: '%.30f' % x)
pd.set_option("display.expand_frame_repr", False)

df = pd.read_json("data/data.json")
df_cars = pd.read_json("data/cars.json")

# Create new features from doluluk column
df["occupied_spots"] = df["doluluk"].apply(lambda x: x.split("/")[0]).astype("int8")
df["max_spots"] = df["doluluk"].apply(lambda x: x.split("/")[1]).astype("int8")

# Take a peak at the charging station data
df.head()
df.describe()

df_cars["average_consumption"] = df_cars['energy_consumption'].apply(lambda x: x['average_consumption'])
df_cars.head()
df_cars.describe()

print(df_cars[df_cars["usable_battery_size"] > 100])
print(df_cars[df_cars["average_consumption"] > 100])

"""
Below; Linear Regression to find the best formula for charging rate
Right now there is not enough data to train a model,
But we can use the following code to train a model when we have more data.
"""

# Drop unnecessary columns
df = df[["occupied_spots", "max_spots", "all_time_kw", "current_kw"]]
df.head()
df.shape

# Step 1: Prepare the data
X = df[["occupied_spots", "max_spots", "all_time_kw"]]  # Features
y = df["current_kw"]  # Target variable

# Step 2: Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

# Step 3: Train the model
model = LinearRegression()
model.fit(X_train, y_train)
print("Training complete.")

# Step 4: Predict and evaluate the model
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse}")

# To build the formula, we can use the coefficients and the intercept
print(f"Coefficients: {model.coef_}")
print(f"Intercept: {model.intercept_}")
