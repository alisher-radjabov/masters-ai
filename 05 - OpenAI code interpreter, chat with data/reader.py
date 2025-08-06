import pandas as pd
import matplotlib.pyplot as plt
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_histogram(csv_path="data/dataset.csv", 
                    column_name="price", 
                    bins=20, 
                    output_path="images/histogram_from_csv.png"):
    """
    Create and save a histogram from a CSV file column.
    
    Args:
        csv_path (str): Path to the CSV file
        column_name (str): Name of the column to plot
        bins (int): Number of histogram bins
        output_path (str): Path to save the histogram
    """
    try:
        # Verify CSV file exists
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found at: {csv_path}")

        # Load CSV file
        logger.info(f"Loading CSV file from {csv_path}")
        df = pd.read_csv(csv_path)

        # Verify column exists and is numeric
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in CSV")
        if not pd.api.types.is_numeric_dtype(df[column_name]):
            raise ValueError(f"Column '{column_name}' is not numeric")

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Create figure with specified size
        plt.figure(figsize=(10, 6))
        
        # Create histogram with additional styling
        plt.hist(df[column_name], 
                bins=bins, 
                edgecolor="black", 
                alpha=0.7,
                color='skyblue')

        # Customize labels and title
        plt.xlabel(column_name.capitalize(), fontsize=12)
        plt.ylabel("Frequency", fontsize=12)
        plt.title(f"Histogram of {column_name.capitalize()}", fontsize=14, pad=15)

        # Add grid
        plt.grid(True, alpha=0.3)

        # Save the plot
        logger.info(f"Saving histogram to {output_path}")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.show()
        plt.close()

        logger.info("Histogram created successfully")
        
    except Exception as e:
        logger.error(f"Error creating histogram: {str(e)}")
        raise

if __name__ == "__main__":
    create_histogram()