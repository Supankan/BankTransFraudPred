import os
import numpy as np
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
import random
from collections import defaultdict

# Initialize Faker and random seed
fake = Faker()
np.random.seed(42)
random.seed(42)

# Set the working directory to the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

def generate_transaction_dataset(num_rows):
    # Predefined constants
    CUSTOMERS = [fake.unique.uuid4()[:8] for _ in range(1000)]
    CITIES = [fake.city() for _ in range(50)]
    HIGH_RISK_CITIES = random.sample(CITIES, 5)
    CATEGORIES = ['groceries', 'electronics', 'gas', 'dining', 'travel',
                 'entertainment', 'clothing', 'health', 'education', 'other']
    HIGH_RISK_CATEGORIES = ['electronics', 'travel']
    LOW_RISK_CATEGORIES = ['groceries', 'gas']

    # Initialize customer balances
    customer_balances = {cid: random.uniform(100, 10000) for cid in CUSTOMERS}
    customer_transaction_counts = defaultdict(int)

    # Create datasets folder
    os.makedirs("datasets", exist_ok=True)

    # Initialize data lists
    data = []
    fraud_scores = []

    # Generate transactions
    for _ in range(num_rows):
        # Core transaction features
        customer_id = random.choice(CUSTOMERS)
        timestamp = fake.date_time_between(start_date='-1y', end_date='now')
        amount = abs(np.random.lognormal(3, 0.8))
        category = random.choice(CATEGORIES)
        location = random.choice(CITIES)
        merchant = fake.company()

        # Customer features
        age = random.randint(18, 80)
        gender = random.choice(['M', 'F'])
        transaction_type = random.choice(['online', 'POS', 'ATM'])

        # Balance features
        old_balance = customer_balances[customer_id]
        new_balance = old_balance - amount
        customer_balances[customer_id] = new_balance  # Update balance

        # Transaction frequency feature
        customer_transaction_counts[customer_id] += 1
        txn_freq = customer_transaction_counts[customer_id]

        # Calculate fraud score (deterministic components)
        score = 0
        # Higher scores for large transactions
        score += min(amount / 1000, 1.5)
        # Location risk
        score += 1.0 if location in HIGH_RISK_CITIES else 0
        # Category risk
        score += 1.5 if category in HIGH_RISK_CATEGORIES else 0
        score += -0.5 if category in LOW_RISK_CATEGORIES else 0
        # Time risk (late night)
        score += 0.8 if timestamp.hour < 5 else 0
        # Overdraft pattern
        score += 1.2 if amount > old_balance * 1.1 else 0
        # Frequency pattern (burst transactions)
        score += min(txn_freq / 10, 1.0)

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

    # Determine fraud threshold (top 8% of scores)
    threshold = np.percentile(fraud_scores, 92)
    df['is_fraud'] = (fraud_scores >= threshold).astype(int)

    # Save to CSV
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"datasets/transactions_{num_rows}_{timestamp_str}.csv"
    df.to_csv(filename, index=False)

    print(f"Dataset generated with {len(df)} rows | Fraud rate: {df['is_fraud'].mean():.2%}")
    print(f"Saved to: {filename}")
    return filename

if __name__ == "__main__":
    num_rows = int(input("Enter number of rows to generate: "))
    generate_transaction_dataset(num_rows)
