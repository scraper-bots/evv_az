import pandas as pd
import numpy as np
from datetime import datetime

# Load and clean data
df = pd.read_csv('/Users/ismatsamadov/evv_az/output/evv_az_listings.csv')

# Clean price and area
df['price_clean'] = df['price'].astype(str).str.replace(' ', '').str.replace(',', '')
df['price_clean'] = pd.to_numeric(df['price_clean'], errors='coerce')
df['area_clean'] = df['area'].astype(str).str.extract('(\d+)').astype(float)
df['post_date_clean'] = pd.to_datetime(df['post_date'], format='%d %B %Y', errors='coerce')

print("="*70)
print("AZERBAIJAN REAL ESTATE MARKET - BUSINESS INTELLIGENCE REPORT")
print("="*70)

# 1. MARKET SIZE AND COMPOSITION
print("\n1. MARKET OVERVIEW")
print("-" * 70)
total_listings = len(df)
print(f"   Total Active Listings: {total_listings:,}")
print(f"   Total Market Value: {df['price_clean'].sum()/1e9:.2f}B AZN")
print(f"   Average Listing Price: {df['price_clean'].mean():,.0f} AZN")
print(f"   Median Listing Price: {df['price_clean'].median():,.0f} AZN")

# 2. PROPERTY TYPE BREAKDOWN
print("\n2. PROPERTY TYPE DISTRIBUTION")
print("-" * 70)
prop_type_stats = df.groupby('property_type').agg({
    'listing_id': 'count',
    'price_clean': ['mean', 'median'],
    'views': 'mean'
}).round(0)
prop_type_stats.columns = ['Count', 'Avg Price', 'Median Price', 'Avg Views']
prop_type_stats['Market Share %'] = (prop_type_stats['Count'] / total_listings * 100).round(1)
prop_type_stats = prop_type_stats.sort_values('Count', ascending=False)
print(prop_type_stats.to_string())

# 3. GEOGRAPHIC DISTRIBUTION
print("\n3. TOP 10 MARKETS BY VOLUME")
print("-" * 70)
city_stats = df.groupby('city').agg({
    'listing_id': 'count',
    'price_clean': 'median',
    'views': 'mean'
}).round(0)
city_stats.columns = ['Listings', 'Median Price', 'Avg Views']
city_stats['Market Share %'] = (city_stats['Listings'] / total_listings * 100).round(1)
city_stats = city_stats.sort_values('Listings', ascending=False).head(10)
print(city_stats.to_string())

# 4. PRICE SEGMENTATION
print("\n4. PRICE SEGMENTATION ANALYSIS")
print("-" * 70)
bins = [0, 50000, 100000, 150000, 200000, 300000, 500000, 1000000, float('inf')]
labels = ['Entry (<50K)', 'Budget (50-100K)', 'Mid (100-150K)', 'Mid+ (150-200K)',
          'Premium (200-300K)', 'Luxury (300-500K)', 'Ultra-Lux (500K-1M)', 'Elite (1M+)']
df['price_segment'] = pd.cut(df['price_clean'], bins=bins, labels=labels)
segment_dist = df['price_segment'].value_counts().sort_index()
for segment, count in segment_dist.items():
    pct = count/len(df)*100
    print(f"   {segment:20s}: {count:6,} listings ({pct:5.1f}%)")

# 5. SELLER LANDSCAPE
print("\n5. SELLER COMPOSITION")
print("-" * 70)
seller_stats = df.groupby('seller_type').agg({
    'listing_id': 'count',
    'price_clean': 'median',
    'views': 'mean'
}).round(0)
seller_stats.columns = ['Listings', 'Median Price', 'Avg Views']
seller_stats['Share %'] = (seller_stats['Listings'] / total_listings * 100).round(1)
print(seller_stats.to_string())

# 6. ENGAGEMENT METRICS
print("\n6. USER ENGAGEMENT ANALYSIS")
print("-" * 70)
print(f"   Average Views per Listing: {df['views'].mean():.0f}")
print(f"   Median Views per Listing: {df['views'].median():.0f}")
print(f"   High-Interest Listings (>300 views): {(df['views'] > 300).sum():,} ({(df['views'] > 300).sum()/len(df)*100:.1f}%)")
print(f"   Low-Interest Listings (<100 views): {(df['views'] < 100).sum():,} ({(df['views'] < 100).sum()/len(df)*100:.1f}%)")

# Top performing property types by views
top_engagement = df.groupby('property_type')['views'].mean().sort_values(ascending=False).head(3)
print(f"\n   Top 3 Property Types by Engagement:")
for i, (prop, views) in enumerate(top_engagement.items(), 1):
    print(f"      {i}. {prop}: {views:.0f} avg views")

# 7. MORTGAGE & FINANCING
print("\n7. FINANCING READINESS")
print("-" * 70)
mortgage_available = df['mortgage'].notna().sum()
mortgage_ready = (df['mortgage'] == 'İpotekaya yararlı').sum()
mortgage_active = (df['mortgage'] == 'Hazır ipoteka').sum()
print(f"   Listings with Mortgage Options: {mortgage_available:,} ({mortgage_available/total_listings*100:.1f}%)")
print(f"   - Mortgage-Ready: {mortgage_ready:,}")
print(f"   - Active Mortgage: {mortgage_active:,}")
print(f"   No Mortgage Info: {total_listings - mortgage_available:,} ({(total_listings - mortgage_available)/total_listings*100:.1f}%)")

# 8. DOCUMENTATION STATUS
print("\n8. LEGAL DOCUMENTATION STATUS")
print("-" * 70)
doc_dist = df['document'].value_counts()
total_with_doc = doc_dist.sum()
print(f"   Listings with Clear Documentation: {total_with_doc:,} ({total_with_doc/total_listings*100:.1f}%)")
for doc_type, count in doc_dist.items():
    print(f"   - {doc_type}: {count:,} ({count/total_listings*100:.1f}%)")

# 9. INVENTORY FRESHNESS
print("\n9. MARKET ACTIVITY & FRESHNESS")
print("-" * 70)
recent_listings = df[df['post_date_clean'] >= pd.Timestamp.now() - pd.Timedelta(days=30)]
print(f"   New Listings (Last 30 Days): {len(recent_listings):,} ({len(recent_listings)/total_listings*100:.1f}%)")

# Monthly trend
monthly_counts = df.groupby(df['post_date_clean'].dt.to_period('M')).size()
if len(monthly_counts) >= 3:
    recent_3mo_avg = monthly_counts.tail(3).mean()
    print(f"   3-Month Average New Listings: {recent_3mo_avg:.0f} per month")

# 10. PRICE EFFICIENCY METRICS
print("\n10. PRICE EFFICIENCY (PRICE PER SQM)")
print("-" * 70)
df_with_area = df[(df['area_clean'].notna()) & (df['area_clean'] > 0) & (df['price_clean'].notna())]
df_with_area['price_per_sqm'] = df_with_area['price_clean'] / df_with_area['area_clean']

main_types = ['Yeni tikili', 'Köhnə tikili', 'Həyət evi / Villa']
for prop_type in main_types:
    subset = df_with_area[df_with_area['property_type'] == prop_type]
    if len(subset) > 0:
        median_psm = subset['price_per_sqm'].median()
        mean_area = subset['area_clean'].mean()
        print(f"   {prop_type:20s}: {median_psm:,.0f} AZN/m² (avg size: {mean_area:.0f}m²)")

# 11. KEY INSIGHTS SUMMARY
print("\n" + "="*70)
print("KEY BUSINESS INSIGHTS")
print("="*70)

# Market concentration
top_3_cities_pct = (df['city'].value_counts().head(3).sum() / total_listings * 100)
print(f"\n• Market Concentration: Top 3 cities control {top_3_cities_pct:.1f}% of inventory")

# Ownership pattern
owner_pct = (df['seller_type'] == 'Sahibindən').sum() / total_listings * 100
print(f"• Direct Ownership: {owner_pct:.1f}% of listings are owner-direct (disintermediated)")

# Premium segment
premium_segment = df[df['price_clean'] >= 200000]
premium_pct = len(premium_segment) / total_listings * 100
print(f"• Premium Market: {premium_pct:.1f}% of listings priced above 200K AZN")

# Engagement gap
high_views = df['views'].quantile(0.75)
low_views = df['views'].quantile(0.25)
print(f"• Engagement Disparity: Top 25% get {high_views:.0f}+ views, bottom 25% get <{low_views:.0f} views")

# Mortgage opportunity
no_mortgage_pct = (df['mortgage'].isna().sum() / total_listings * 100)
print(f"• Financing Gap: {no_mortgage_pct:.1f}% of listings lack mortgage information")

# Property mix
villas_pct = (df['property_type'] == 'Həyət evi / Villa').sum() / total_listings * 100
new_construction_pct = (df['property_type'] == 'Yeni tikili').sum() / total_listings * 100
print(f"• Property Mix: {villas_pct:.1f}% villas, {new_construction_pct:.1f}% new construction")

print("\n" + "="*70)
