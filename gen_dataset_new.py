import os
import numpy as np
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
import random
from collections import defaultdict
from scipy.stats import skewnorm  # For skewed normal distribution

# Set working directory to script location
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

def generate_transaction_dataset(num_rows):
    # Predefined constants
    CUSTOMERS = [fake.unique.uuid4()[:8] for _ in range(5000)]  # Larger customer pool
    CITIES = [fake.city() for _ in range(100)]  # More cities
    COUNTRIES = ['US', 'UK', 'CA', 'AU', 'DE', 'FR', 'JP', 'SG', 'BR', 'IN']
    
    # Enhanced risk profiles
    RISK_CATEGORIES = {
        'electronics': 0.35,
        'travel': 0.30,
        'gaming': 0.25,  # New high-risk category
        'digital_services': 0.20,
        'dining': 0.15,
        'entertainment': 0.12,
        'health': 0.10,
        'clothing': 0.08,
        'groceries': 0.05,
        'gas': 0.03,
        'utilities': 0.02,
        'education': 0.01
    }
    
    # Country risk factors
    COUNTRY_RISK = {
        'BR': 1.5, 'IN': 1.4, 'SG': 1.3,  # High-risk countries
        'US': 1.0, 'UK': 1.0, 'CA': 1.0,  # Medium-risk
        'AU': 0.9, 'DE': 0.8, 'FR': 0.8, 'JP': 0.7  # Low-risk
    }
    
    # Initialize customer profiles with persistent risk factors
    customer_profiles = {}
    for cid in CUSTOMERS:
        # Age follows a skewed normal distribution (slightly younger population)
        age = int(skewnorm.rvs(5, loc=35, scale=15, size=1)[0])
        age = max(18, min(80, age))
        
        # Customer risk factor (some customers are inherently riskier)
        risk_factor = max(0.1, min(2.0, np.random.lognormal(0, 0.3)))
        
        # Country risk
        country = random.choice(COUNTRIES)
        country_risk = COUNTRY_RISK.get(country, 1.0)
        
        customer_profiles[cid] = {
            'age': age,
            'country': country,
            'risk_factor': risk_factor,
            'country_risk': country_risk,
            'balance': max(100, np.random.lognormal(7, 0.5))
        }
    
    # Create datasets folder
    os.makedirs("datasets", exist_ok=True)
    
    # Initialize data lists
    data = []
    fraud_scores = []
    
    # Customer transaction counters
    customer_txn_counts = defaultdict(int)
    customer_last_txn = {}
    
    # Generate transactions
    for i in range(num_rows):
        # Core transaction features
        customer_id = random.choice(list(customer_profiles.keys()))
        profile = customer_profiles[customer_id]
        
        # Time progression (transactions become more frequent over time)
        if customer_id in customer_last_txn:
            last_txn = customer_last_txn[customer_id]
            time_delta = timedelta(hours=np.random.exponential(48))
        else:
            last_txn = fake.date_time_between(start_date='-1y', end_date='-6m')
            time_delta = timedelta(days=np.random.randint(0, 30))
        
        timestamp = last_txn + time_delta
        customer_last_txn[customer_id] = timestamp
        
        # Amount follows power-law distribution (many small, few large)
        if random.random() < 0.95:  # 95% of transactions are small
            amount = abs(np.random.lognormal(3, 0.5))
        else:  # 5% are large transactions
            amount = abs(np.random.lognormal(6, 0.8))
        
        # Select category with risk weighting
        category = random.choices(
            list(RISK_CATEGORIES.keys()),
            weights=list(RISK_CATEGORIES.values()),
            k=1
        )[0]
        
        # Merchant type based on category
        if category == 'electronics':
            merchant = fake.company() + ' Electronics'
        elif category == 'travel':
            merchant = fake.company() + ' Travel'
        else:
            merchant = fake.company()
            
        # Location based on customer country
        location = random.choice(CITIES) + f", {profile['country']}"
        
        # Customer features
        age = profile['age']
        gender = random.choice(['M', 'F'])
        transaction_type = random.choice(['online', 'POS', 'ATM'])
        
        # Balance features
        old_balance = profile['balance']
        new_balance = old_balance - amount
        profile['balance'] = new_balance  # Update balance
        
        # Update transaction count
        customer_txn_counts[customer_id] += 1
        txn_freq = customer_txn_counts[customer_id]
        
        # Complex fraud scoring
        score = 0
        
        # 1. Base category risk
        score += RISK_CATEGORIES[category] * 2.5
        
        # 2. Amount risk (non-linear scaling)
        amount_risk = min(amount / 1000, 2.0)  # Cap at 2.0
        amount_risk += max(0, (amount - 5000) / 10000)  # Extra risk for large amounts
        score += amount_risk
        
        # 3. Time patterns (multiple risk periods)
        hour = timestamp.hour
        if hour < 5 or hour > 22:  # Late night
            score += 0.8
        elif 12 <= hour <= 14:  # Lunch time
            score += 0.4
        elif 17 <= hour <= 19:  # Evening commute
            score += 0.3
            
        # 4. Customer behavior patterns
        # Recent transaction burst (last 10 transactions in <24 hours)
        recent_txns = 0
        for other_id, last_time in customer_last_txn.items():
            if other_id == customer_id:
                continue
            if (timestamp - last_time) < timedelta(hours=24):
                recent_txns += 1
        score += min(recent_txns * 0.2, 1.5)
        
        # 5. Balance patterns
        # Overdraft pattern
        if amount > old_balance * 1.05:  # 5% over balance
            score += 1.5
        # Low balance pattern
        if new_balance < 50:
            score += 0.7
            
        # 6. Geographic risk
        score += profile['country_risk'] * 0.8
        
        # 7. Customer risk factor (inherent riskiness)
        score += profile['risk_factor'] * 1.2
        
        # 8. New customer pattern (first 5 transactions)
        if txn_freq <= 5:
            score += 1.0 - (txn_freq * 0.15)
            
        # 9. Cross-border transactions
        if "US" not in location and profile['country'] == 'US':
            score += 0.9
            
        # Add noise to make detection harder
        score += random.gauss(0, 0.3)
        
        fraud_scores.append(score)
        data.append([
            customer_id, timestamp, amount, old_balance, new_balance,
            merchant, category, location, age, gender, transaction_type
        ])
    
    # Convert to DataFrame
    columns = [
        'customer_id', 'timestamp', 'amount', 'old_balance', 'new_balance',
        'merchant', 'category', 'location', 'age', 'gender', 'transaction_type'
    ]
    df = pd.DataFrame(data, columns=columns)
    
    # Dynamic fraud threshold (target ~5% fraud rate)
    threshold = np.percentile(fraud_scores, 95)
    df['is_fraud'] = (fraud_scores >= threshold).astype(int)
    
    # Verify fraud distribution across categories
    fraud_rates = df.groupby('category')['is_fraud'].mean().sort_values(ascending=False)
    print("\nFraud rate by category:")
    print(fraud_rates)
    
    # Save to CSV
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"datasets/transactions_{num_rows}_{timestamp_str}.csv"
    df.to_csv(filename, index=False)
    
    print(f"\nDataset generated with {len(df)} rows | Fraud rate: {df['is_fraud'].mean():.2%}")
    print(f"Saved to: {filename}")
    return filename

if __name__ == "__main__":
    # Initialize Faker and set seeds
    fake = Faker()
    np.random.seed(42)
    random.seed(42)
    
    num_rows = int(input("Enter number of rows to generate: "))
    generate_transaction_dataset(num_rows)

    