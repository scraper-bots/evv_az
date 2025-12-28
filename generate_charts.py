import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style for professional business charts
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# Load the dataset
df = pd.read_csv('/Users/ismatsamadov/evv_az/output/evv_az_listings.csv')

# Data Cleaning
# Clean price column - remove spaces and convert to numeric
df['price_clean'] = df['price'].astype(str).str.replace(' ', '').str.replace(',', '')
df['price_clean'] = pd.to_numeric(df['price_clean'], errors='coerce')

# Clean area column
df['area_clean'] = df['area'].astype(str).str.extract('(\d+)').astype(float)

# Parse dates
df['post_date_clean'] = pd.to_datetime(df['post_date'], format='%d %B %Y', errors='coerce')
df['update_date_clean'] = pd.to_datetime(df['update_date'], format='%d %B %Y', errors='coerce')

# Extract month and year for time series
df['post_month'] = df['post_date_clean'].dt.to_period('M')

print("Data loaded and cleaned successfully!")
print(f"Total listings: {len(df):,}")
print(f"Price range: {df['price_clean'].min():,.0f} - {df['price_clean'].max():,.0f} AZN")

# ============================================
# CHART 1: Property Type Distribution
# ============================================
plt.figure(figsize=(12, 6))
property_counts = df['property_type'].value_counts().head(7)
colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#BC4B51', '#8E7DBE']
bars = plt.barh(range(len(property_counts)), property_counts.values, color=colors)
plt.yticks(range(len(property_counts)), property_counts.index)
plt.xlabel('Number of Listings', fontsize=12, fontweight='bold')
plt.title('Market Distribution by Property Type', fontsize=14, fontweight='bold', pad=20)
plt.gca().invert_yaxis()

# Add value labels
for i, (idx, val) in enumerate(property_counts.items()):
    plt.text(val + 50, i, f'{val:,} ({val/len(df)*100:.1f}%)',
             va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/01_property_type_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 1: Property Type Distribution")

# ============================================
# CHART 2: Average Price by Property Type
# ============================================
plt.figure(figsize=(12, 6))
price_by_type = df.groupby('property_type')['price_clean'].agg(['mean', 'count']).sort_values('mean', ascending=False)
price_by_type = price_by_type[price_by_type['count'] >= 50]  # Filter out types with few listings

colors_price = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#BC4B51', '#8E7DBE']
bars = plt.barh(range(len(price_by_type)), price_by_type['mean'].values, color=colors_price[:len(price_by_type)])
plt.yticks(range(len(price_by_type)), price_by_type.index)
plt.xlabel('Average Price (AZN)', fontsize=12, fontweight='bold')
plt.title('Average Price by Property Type', fontsize=14, fontweight='bold', pad=20)
plt.gca().invert_yaxis()

# Add value labels
for i, (idx, row) in enumerate(price_by_type.iterrows()):
    plt.text(row['mean'] + 5000, i, f'{row["mean"]:,.0f} AZN',
             va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/02_average_price_by_type.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 2: Average Price by Property Type")

# ============================================
# CHART 3: Top 10 Cities by Listing Volume
# ============================================
plt.figure(figsize=(12, 6))
top_cities = df['city'].value_counts().head(10)
colors_city = ['#2E86AB', '#3A9EBF', '#52B6D3', '#6ACED7', '#82E6DB',
               '#A8C686', '#C4A661', '#E0863C', '#F26419', '#D94423']
bars = plt.barh(range(len(top_cities)), top_cities.values, color=colors_city)
plt.yticks(range(len(top_cities)), top_cities.index)
plt.xlabel('Number of Listings', fontsize=12, fontweight='bold')
plt.title('Top 10 Markets by Listing Volume', fontsize=14, fontweight='bold', pad=20)
plt.gca().invert_yaxis()

# Add value labels and percentage
for i, (city, count) in enumerate(top_cities.items()):
    pct = count/len(df)*100
    plt.text(count + 50, i, f'{count:,} ({pct:.1f}%)',
             va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/03_top_cities_by_volume.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 3: Top 10 Cities by Listing Volume")

# ============================================
# CHART 4: Seller Type Comparison
# ============================================
plt.figure(figsize=(10, 6))
seller_counts = df['seller_type'].value_counts()
colors_seller = ['#2E86AB', '#F18F01']
bars = plt.bar(range(len(seller_counts)), seller_counts.values, color=colors_seller, width=0.6)
plt.xticks(range(len(seller_counts)), seller_counts.index, rotation=15, ha='right')
plt.ylabel('Number of Listings', fontsize=12, fontweight='bold')
plt.title('Market Share: Owner vs Agency Listings', fontsize=14, fontweight='bold', pad=20)

# Add value labels and percentage
for i, (seller, count) in enumerate(seller_counts.items()):
    pct = count/len(df)*100
    plt.text(i, count + 200, f'{count:,}\n({pct:.1f}%)',
             ha='center', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/04_seller_type_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 4: Seller Type Distribution")

# ============================================
# CHART 5: Price Range Distribution
# ============================================
plt.figure(figsize=(12, 6))
# Create price bins
bins = [0, 50000, 100000, 150000, 200000, 300000, 500000, 1000000, float('inf')]
labels = ['0-50K', '50-100K', '100-150K', '150-200K', '200-300K', '300-500K', '500K-1M', '1M+']
df['price_range'] = pd.cut(df['price_clean'], bins=bins, labels=labels)

price_range_counts = df['price_range'].value_counts().sort_index()
colors_range = ['#2E86AB', '#3A9EBF', '#52B6D3', '#6ACED7', '#82E6DB', '#A8C686', '#C4A661', '#E0863C']
bars = plt.bar(range(len(price_range_counts)), price_range_counts.values, color=colors_range)
plt.xticks(range(len(price_range_counts)), price_range_counts.index, rotation=45, ha='right')
plt.ylabel('Number of Listings', fontsize=12, fontweight='bold')
plt.xlabel('Price Range (AZN)', fontsize=12, fontweight='bold')
plt.title('Listing Distribution by Price Range', fontsize=14, fontweight='bold', pad=20)

# Add value labels
for i, (price_range, count) in enumerate(price_range_counts.items()):
    if pd.notna(count):
        plt.text(i, count + 50, f'{int(count):,}',
                 ha='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/05_price_range_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 5: Price Range Distribution")

# ============================================
# CHART 6: Average Views by Property Type
# ============================================
plt.figure(figsize=(12, 6))
views_by_type = df.groupby('property_type')['views'].mean().sort_values(ascending=False)
colors_views = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#BC4B51', '#8E7DBE']
bars = plt.barh(range(len(views_by_type)), views_by_type.values, color=colors_views)
plt.yticks(range(len(views_by_type)), views_by_type.index)
plt.xlabel('Average Views per Listing', fontsize=12, fontweight='bold')
plt.title('Average User Engagement by Property Type', fontsize=14, fontweight='bold', pad=20)
plt.gca().invert_yaxis()

# Add value labels
for i, (prop_type, views) in enumerate(views_by_type.items()):
    plt.text(views + 5, i, f'{views:.0f}',
             va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/06_average_views_by_type.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 6: Average Views by Property Type")

# ============================================
# CHART 7: Market Activity Over Time
# ============================================
plt.figure(figsize=(14, 6))
# Group by month and count listings
monthly_posts = df.groupby('post_month').size()
monthly_posts = monthly_posts.sort_index()

# Convert period to timestamp for plotting
x_values = [pd.Timestamp(period.to_timestamp()) for period in monthly_posts.index]
plt.plot(x_values, monthly_posts.values, marker='o', linewidth=2.5,
         markersize=6, color='#2E86AB', markerfacecolor='#F18F01')
plt.xlabel('Month', fontsize=12, fontweight='bold')
plt.ylabel('Number of New Listings', fontsize=12, fontweight='bold')
plt.title('Market Activity Trend: New Listings Over Time', fontsize=14, fontweight='bold', pad=20)
plt.xticks(rotation=45, ha='right')
plt.grid(True, alpha=0.3)

# Add trend annotation
recent_avg = monthly_posts.tail(3).mean()
plt.axhline(y=recent_avg, color='red', linestyle='--', alpha=0.5, linewidth=1.5)
plt.text(x_values[-1], recent_avg + 20, f'Recent Avg: {recent_avg:.0f}',
         fontsize=10, color='red', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/07_market_activity_trend.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 7: Market Activity Trend")

# ============================================
# CHART 8: Document Type Distribution
# ============================================
plt.figure(figsize=(10, 6))
doc_counts = df['document'].value_counts()
colors_doc = ['#2E86AB', '#F18F01', '#A23B72', '#6A994E']
bars = plt.bar(range(len(doc_counts)), doc_counts.values, color=colors_doc[:len(doc_counts)], width=0.6)
plt.xticks(range(len(doc_counts)), doc_counts.index, rotation=15, ha='right')
plt.ylabel('Number of Listings', fontsize=12, fontweight='bold')
plt.title('Property Documentation Status', fontsize=14, fontweight='bold', pad=20)

# Add value labels and percentage
for i, (doc, count) in enumerate(doc_counts.items()):
    pct = count/doc_counts.sum()*100
    plt.text(i, count + 100, f'{count:,}\n({pct:.1f}%)',
             ha='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/08_document_type_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 8: Document Type Distribution")

# ============================================
# CHART 9: Mortgage Availability
# ============================================
plt.figure(figsize=(10, 6))
# Count listings with mortgage info
mortgage_available = df[df['mortgage'].notna()]['mortgage'].value_counts()
no_mortgage = len(df[df['mortgage'].isna()])
mortgage_data = pd.concat([mortgage_available, pd.Series({'Qeyd edilməyib': no_mortgage})])

colors_mortgage = ['#2E86AB', '#F18F01', '#A8C686']
bars = plt.bar(range(len(mortgage_data)), mortgage_data.values, color=colors_mortgage, width=0.6)
plt.xticks(range(len(mortgage_data)), mortgage_data.index, rotation=15, ha='right')
plt.ylabel('Number of Listings', fontsize=12, fontweight='bold')
plt.title('Mortgage/Financing Options Availability', fontsize=14, fontweight='bold', pad=20)

# Add value labels and percentage
for i, (option, count) in enumerate(mortgage_data.items()):
    pct = count/len(df)*100
    plt.text(i, count + 200, f'{count:,}\n({pct:.1f}%)',
             ha='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/09_mortgage_availability.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 9: Mortgage Availability")

# ============================================
# CHART 10: Price vs Area Comparison by Type
# ============================================
plt.figure(figsize=(12, 6))
# Calculate price per sqm for main property types
main_types = ['Yeni tikili', 'Köhnə tikili', 'Həyət evi / Villa']
price_per_sqm_data = []

for prop_type in main_types:
    subset = df[(df['property_type'] == prop_type) &
                (df['price_clean'].notna()) &
                (df['area_clean'].notna()) &
                (df['area_clean'] > 0)]
    subset['price_per_sqm'] = subset['price_clean'] / subset['area_clean']
    avg_price_per_sqm = subset['price_per_sqm'].median()
    price_per_sqm_data.append(avg_price_per_sqm)

colors_sqm = ['#2E86AB', '#F18F01', '#A23B72']
bars = plt.bar(range(len(main_types)), price_per_sqm_data, color=colors_sqm, width=0.6)
plt.xticks(range(len(main_types)), main_types, rotation=15, ha='right')
plt.ylabel('Median Price per Square Meter (AZN)', fontsize=12, fontweight='bold')
plt.title('Price Efficiency: Cost per Square Meter by Property Type', fontsize=14, fontweight='bold', pad=20)

# Add value labels
for i, price in enumerate(price_per_sqm_data):
    plt.text(i, price + 20, f'{price:,.0f} AZN/m²',
             ha='center', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/10_price_per_sqm_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 10: Price per Square Meter Comparison")

# ============================================
# CHART 11: Top 5 Cities - Average Price Comparison
# ============================================
plt.figure(figsize=(12, 6))
top_5_cities = df['city'].value_counts().head(5).index
city_price_data = df[df['city'].isin(top_5_cities)].groupby('city')['price_clean'].median().sort_values(ascending=False)

colors_city_price = ['#2E86AB', '#3A9EBF', '#52B6D3', '#6ACED7', '#82E6DB']
bars = plt.barh(range(len(city_price_data)), city_price_data.values, color=colors_city_price)
plt.yticks(range(len(city_price_data)), city_price_data.index)
plt.xlabel('Median Price (AZN)', fontsize=12, fontweight='bold')
plt.title('Price Comparison: Top 5 Markets', fontsize=14, fontweight='bold', pad=20)
plt.gca().invert_yaxis()

# Add value labels
for i, (city, price) in enumerate(city_price_data.items()):
    plt.text(price + 5000, i, f'{price:,.0f} AZN',
             va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/11_top_cities_price_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 11: Top Cities Price Comparison")

# ============================================
# CHART 12: Furnished vs Unfurnished Market
# ============================================
plt.figure(figsize=(10, 6))
furnished_counts = df['furnished'].value_counts()
not_specified = len(df[df['furnished'].isna()])
furnished_data = pd.concat([furnished_counts, pd.Series({'Qeyd edilməyib': not_specified})])

# Create labels based on actual data
labels = list(furnished_data.index)
colors_furnished = ['#2E86AB', '#F18F01', '#A8C686']
bars = plt.bar(range(len(furnished_data)), furnished_data.values, color=colors_furnished[:len(furnished_data)], width=0.6)
plt.xticks(range(len(furnished_data)), labels, rotation=15, ha='right')
plt.ylabel('Number of Listings', fontsize=12, fontweight='bold')
plt.title('Furnished Property Availability', fontsize=14, fontweight='bold', pad=20)

# Add value labels and percentage
for i, count in enumerate(furnished_data.values):
    pct = count/len(df)*100
    plt.text(i, count + 200, f'{count:,}\n({pct:.1f}%)',
             ha='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/12_furnished_availability.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 12: Furnished Property Availability")

print("\n" + "="*60)
print("ALL CHARTS GENERATED SUCCESSFULLY!")
print("="*60)
print(f"\nTotal charts created: 12")
print(f"Output directory: charts/")
print("\nBusiness insights extracted:")
print(f"  • Total market size: {len(df):,} listings")
print(f"  • Average listing views: {df['views'].mean():.0f}")
print(f"  • Median price: {df['price_clean'].median():,.0f} AZN")
print(f"  • Price range: {df['price_clean'].min():,.0f} - {df['price_clean'].max():,.0f} AZN")
print(f"  • Owner listings: {(df['seller_type']=='Sahibindən').sum()/len(df)*100:.1f}%")
print(f"  • Mortgage-ready: {df['mortgage'].notna().sum()/len(df)*100:.1f}%")
