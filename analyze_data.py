import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_csv('/Users/ismatsamadov/evv_az/output/evv_az_listings.csv')

# Display basic info
print("Dataset Shape:", df.shape)
print("\nColumn Names:")
print(df.columns.tolist())
print("\nData Types:")
print(df.dtypes)
print("\nFirst few rows:")
print(df.head())
print("\nMissing Values:")
print(df.isnull().sum())
print("\nBasic Statistics:")
print(df.describe())

# Analyze categorical columns
print("\n=== CATEGORICAL ANALYSIS ===")
print("\nProperty Types:")
print(df['property_type'].value_counts())
print("\nCities:")
print(df['city'].value_counts())
print("\nSeller Types:")
print(df['seller_type'].value_counts())
print("\nDocument Types:")
print(df['document'].value_counts())
print("\nMortgage Options:")
print(df['mortgage'].value_counts())

# Price analysis
print("\n=== PRICE ANALYSIS ===")
print("Price Statistics:")
print(df['price'].describe())
print("\nPrice by Property Type:")
print(df.groupby('property_type')['price'].agg(['mean', 'median', 'min', 'max', 'count']))

# Area analysis
print("\n=== AREA ANALYSIS ===")
df['area_numeric'] = df['area'].str.extract('(\d+)').astype(float)
print("Area Statistics:")
print(df['area_numeric'].describe())

# Views analysis
print("\n=== ENGAGEMENT ANALYSIS ===")
print("Views Statistics:")
print(df['views'].describe())
print("\nViews by Property Type:")
print(df.groupby('property_type')['views'].agg(['mean', 'median', 'max']))

# Date analysis
df['post_date'] = pd.to_datetime(df['post_date'], format='%d %B %Y', errors='coerce')
df['update_date'] = pd.to_datetime(df['update_date'], format='%d %B %Y', errors='coerce')
print("\n=== TEMPORAL ANALYSIS ===")
print("Date Range:")
print(f"Earliest post: {df['post_date'].min()}")
print(f"Latest post: {df['post_date'].max()}")
