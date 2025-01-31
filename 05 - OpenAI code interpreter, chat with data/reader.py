import pandas as pd
import matplotlib.pyplot as plt

# Load CSV file
df = pd.read_csv("data/dataset.csv")

# Select a numeric column for histogram (replace with actual column name)
column_name = "price"
plt.hist(df[column_name], bins=20, edgecolor="black")

# Labels and title
plt.xlabel(column_name)
plt.ylabel("Frequency")
plt.title(f"Histogram of {column_name}")

# Save the plot
plt.savefig("images/histogram_from_csv.png")
plt.show()