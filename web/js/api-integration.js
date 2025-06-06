// api-integration.js - Example of how to integrate with the real ML model API

// Replace the mock calculateFraudScore function with this real API call
async function calculateFraudScoreAPI(transaction) {
    try {
        // Prepare the transaction data for the API
        const apiData = {
            amount: transaction.amount,
            old_balance: transaction.balance,
            new_balance: transaction.balance - transaction.amount,
            age: transaction.age,
            category: transaction.category,
            gender: 'M', // You might want to add this to the form
            transaction_type: transaction.type,
            location: `${transaction.location}`,
            timestamp: new Date().toISOString(),
            customer_id: 'WEB_DEMO_USER',
            merchant: 'Demo Merchant'
        };
        
        // Call your Flask API
        const response = await fetch('http://localhost:5000/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(apiData)
        });
        
        if (!response.ok) {
            throw new Error('API request failed');
        }
        
        const result = await response.json();
        
        // Convert probability to percentage score
        const fraudScore = result.fraud_probability * 100;
        
        // You can also use the additional information
        console.log('API Response:', {
            score: fraudScore,
            isFraud: result.is_fraud,
            threshold: result.threshold,
            riskLevel: result.risk_level
        });
        
        return fraudScore;
        
    } catch (error) {
        console.error('Error calling fraud detection API:', error);
        // Fallback to mock calculation if API is unavailable
        return calculateFraudScore(transaction);
    }
}

// Update the analyzeTransaction function to use the API
async function analyzeTransactionWithAPI() {
    // Show loading state
    document.querySelector('.risk-percentage').textContent = '...';
    document.querySelector('.risk-label').textContent = 'Analyzing...';
    
    // Get form values
    const transaction = {
        amount: parseFloat(document.getElementById('amount').value),
        balance: parseFloat(document.getElementById('balance').value),
        age: parseInt(document.getElementById('age').value),
        category: document.getElementById('category').value,
        time: document.getElementById('time').value,
        location: document.getElementById('location').value,
        type: document.querySelector('input[name="transaction-type"]:checked').value
    };
    
    try {
        // Calculate fraud score using API
        const fraudScore = await calculateFraudScoreAPI(transaction);
        
        // Update visualizations
        updateRiskMeter(fraudScore);
        updateRiskFactors(transaction, fraudScore);
        updateDecisionPanel(fraudScore);
        
    } catch (error) {
        console.error('Error in transaction analysis:', error);
        // Handle error - show error message to user
        document.querySelector('.risk-label').textContent = 'Analysis Error';
    }
    
    // Add animation class
    document.querySelector('.risk-analysis').classList.add('analyzing');
    setTimeout(() => {
        document.querySelector('.risk-analysis').classList.remove('analyzing');
    }, 1000);
}

// Batch analysis example
async function analyzeBatch(transactions) {
    try {
        const response = await fetch('http://localhost:5000/predict_batch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ transactions })
        });
        
        if (!response.ok) {
            throw new Error('Batch API request failed');
        }
        
        const result = await response.json();
        return result;
        
    } catch (error) {
        console.error('Error in batch analysis:', error);
        return null;
    }
}

// Example of how to set up CORS for development
// Add this to your Flask API:
/*
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])
*/

// Note: In production, you should:
// 1. Use HTTPS for the API
// 2. Configure proper CORS settings
// 3. Add authentication/API keys
// 4. Implement rate limiting
// 5. Add request validation
// 6. Handle errors gracefully

