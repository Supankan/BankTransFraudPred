import os
import numpy as np
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
import random
from collections import defaultdict
from scipy.stats import skewnorm

# Set working directory to script location
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
except NameError:
    # This will run in interactive environments (like Jupyter)
    print("Running in an interactive environment. Using current working directory.")
    script_dir = os.getcwd()


def generate_transaction_dataset_optimized(num_rows):
    """
    Generates a highly optimized synthetic transaction dataset using vectorized operations.
    """
    print("Initializing constants and customer profiles...")
    fake = Faker()

    # Predefined constants
    # Using a smaller, fixed set of customers for more realistic repeat patterns
    CUSTOMERS = [fake.unique.uuid4()[:8] for _ in range(5000)]
    CITIES = [fake.city() for _ in range(100)]
    COUNTRIES = ['US', 'UK', 'CA', 'AU', 'DE', 'FR', 'JP', 'SG', 'BR', 'IN']

    RISK_CATEGORIES = {
        'electronics': 0.35, 'travel': 0.30, 'gaming': 0.25, 'digital_services': 0.20,
        'dining': 0.15, 'entertainment': 0.12, 'health': 0.10, 'clothing': 0.08,
        'groceries': 0.05, 'gas': 0.03, 'utilities': 0.02, 'education': 0.01
    }

    COUNTRY_RISK = {
        'BR': 1.5, 'IN': 1.4, 'SG': 1.3, 'US': 1.0, 'UK': 1.0, 'CA': 1.0,
        'AU': 0.9, 'DE': 0.8, 'FR': 0.8, 'JP': 0.7
    }

    # Initialize customer profiles
    customer_profiles = {}
    for cid in CUSTOMERS:
        age = int(max(18, min(80, skewnorm.rvs(5, loc=35, scale=15, size=1)[0])))
        country = random.choice(COUNTRIES)
        customer_profiles[cid] = {
            'age': age,
            'country': country,
            'risk_factor': max(0.1, min(2.0, np.random.lognormal(0, 0.3))),
            'country_risk': COUNTRY_RISK.get(country, 1.0),
            'initial_balance': max(100, np.random.lognormal(7, 0.5))
        }

    print(f"Generating {num_rows} transactions using vectorized methods...")

    # === 1. Vectorized Core Feature Generation ===
    
    # Assign customers to each transaction
    customer_ids = np.random.choice(CUSTOMERS, size=num_rows)
    df = pd.DataFrame({'customer_id': customer_ids})

    # Map customer profile data efficiently
    profiles_df = pd.DataFrame.from_dict(customer_profiles, orient='index')
    df = df.join(profiles_df, on='customer_id')

    # Generate amounts using a vectorized conditional choice
    is_large_txn = np.random.rand(num_rows) < 0.05
    small_amounts = np.abs(np.random.lognormal(3, 0.5, size=num_rows))
    large_amounts = np.abs(np.random.lognormal(6, 0.8, size=num_rows))
    df['amount'] = np.where(is_large_txn, large_amounts, small_amounts).round(2)

    # Generate categories with weighted probabilities
    categories_list = list(RISK_CATEGORIES.keys())
    category_weights = np.array(list(RISK_CATEGORIES.values()))
    category_weights /= category_weights.sum()  # Ensure weights sum to 1
    df['category'] = np.random.choice(categories_list, size=num_rows, p=category_weights)
    
    # Generate other simple features
    df['gender'] = np.random.choice(['M', 'F'], size=num_rows)
    df['transaction_type'] = np.random.choice(['online', 'POS', 'ATM'], size=num_rows)

    # === 2. Handle Sequential & Location-Based Features ===

    # To handle sequential data, we must establish a chronological order per customer
    df['temp_order'] = np.random.rand(num_rows)
    df.sort_values(['customer_id', 'temp_order'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Generate timestamps sequentially
    time_deltas = pd.Series(pd.to_timedelta(np.random.exponential(scale=48, size=num_rows), unit='hours'))
    # Use groupby().cumsum() to create sequential timestamps for each customer
    cumulative_deltas = df.groupby('customer_id')['temp_order'].transform(lambda x: time_deltas.loc[x.index].cumsum())
    # Create a random start date for each customer's first transaction
    start_dates = df.groupby('customer_id')['customer_id'].transform(
        lambda x: fake.date_time_between(start_date='-1y', end_date='-6m')
    )
    df['timestamp'] = start_dates + cumulative_deltas

    # Generate balance updates
    df['cumulative_spend'] = df.groupby('customer_id')['amount'].cumsum()
    df['new_balance'] = df['initial_balance'] - df['cumulative_spend']
    df['old_balance'] = df.groupby('customer_id')['new_balance'].shift(1).fillna(df['initial_balance'])

    # Generate merchants and locations
    base_merchants = [fake.company() for _ in range(num_rows)]
    df['merchant'] = base_merchants
    df.loc[df['category'] == 'electronics', 'merchant'] += ' Electronics'
    df.loc[df['category'] == 'travel', 'merchant'] += ' Travel'
    
    # Allow for cross-border transactions
    is_cross_border = np.random.rand(num_rows) < 0.1
    txn_countries = df['country'].values.copy()
    cross_border_indices = np.where(is_cross_border)[0]
    
    for i in cross_border_indices:
        home_country = txn_countries[i]
        possible_countries = [c for c in COUNTRIES if c != home_country]
        if possible_countries:
            txn_countries[i] = random.choice(possible_countries)
            
    df['txn_country'] = txn_countries
    df['location'] = [f"{fake.city()}, {country}" for country in df['txn_country']]

    # === 3. Vectorized Fraud Scoring ===
    
    score = pd.Series(np.zeros(num_rows), index=df.index)
    
    # 1. Base category risk
    category_risk_map = {k: v * 2.5 for k, v in RISK_CATEGORIES.items()}
    score += df['category'].map(category_risk_map)
    
    # 2. Amount risk
    score += (df['amount'] / 1000).clip(upper=2.0)
    score += ((df['amount'] - 5000) / 10000).clip(lower=0)
    
    # 3. Time patterns
    hour = df['timestamp'].dt.hour
    score += np.where((hour < 5) | (hour > 22), 0.8, 0)
    score += np.where((hour >= 12) & (hour <= 14), 0.4, 0)
    score += np.where((hour >= 17) & (hour <= 19), 0.3, 0)
    
    # 4. Customer behavior (OPTIMIZED): Time since last transaction for the same customer
    time_since_last_txn_hours = df.groupby('customer_id')['timestamp'].diff().dt.total_seconds() / 3600
    score += np.select(
        [time_since_last_txn_hours < 0.1, time_since_last_txn_hours < 1],
        [1.5, 0.8], default=0
    )
    
    # 5. Balance patterns
    score += np.where(df['amount'] > df['old_balance'] * 1.05, 1.5, 0)
    score += np.where(df['new_balance'] < 50, 0.7, 0)
    
    # 6. Geographic & Customer Risk
    score += df['country_risk'] * 0.8
    score += df['risk_factor'] * 1.2
    
    # 7. New customer pattern
    txn_freq = df.groupby('customer_id').cumcount() + 1
    is_new_customer_txn = txn_freq <= 5
    score += (1.0 - (txn_freq * 0.15)).clip(lower=0) * is_new_customer_txn
    
    # 8. Cross-border transaction
    score += np.where(df['country'] != df['txn_country'], 0.9, 0)
    
    # 9. Add noise
    score += np.random.normal(0, 0.3, size=num_rows)
    
    # === 4. Finalizing the DataFrame ===
    
    # Dynamic fraud threshold
    threshold = np.percentile(score.dropna(), 95)
    df['is_fraud'] = (score >= threshold).astype(int)
    
    # Select and reorder columns to match original output
    final_columns = [
        'customer_id', 'timestamp', 'amount', 'old_balance', 'new_balance',
        'merchant', 'category', 'location', 'age', 'gender', 'transaction_type', 'is_fraud'
    ]
    df = df[final_columns]
    
    # Verify fraud distribution
    fraud_rates = df.groupby('category')['is_fraud'].mean().sort_values(ascending=False)
    print("\nFraud rate by category:")
    print(fraud_rates)

    # Save to CSV
    os.makedirs("datasets", exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(script_dir, "datasets", f"transactions_{num_rows}_{timestamp_str}.csv")
    df.to_csv(filename, index=False, date_format='%Y-%m-%d %H:%M:%S')
    
    print(f"\nDataset generated with {len(df)} rows | Fraud rate: {df['is_fraud'].mean():.2%}")
    print(f"Saved to: {filename}")
    return filename

if __name__ == "__main__":
    # Initialize Faker and set seeds for reproducibility
    np.random.seed(42)
    random.seed(42)
    
    while True:
        try:
            num_rows_input = input("Enter number of rows to generate: ")
            if not num_rows_input: continue
            num_rows = int(num_rows_input)
            break
        except ValueError:
            print("Invalid input. Please enter an integer.")

    generate_transaction_dataset_optimized(num_rows)

