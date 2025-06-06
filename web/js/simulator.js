// simulator.js - Simulator Page JavaScript

// Mock fraud detection logic (simulates ML model behavior)
function calculateFraudScore(transaction) {
    let score = 0;
    
    // Amount risk
    if (transaction.amount > 5000) score += 25;
    else if (transaction.amount > 2000) score += 15;
    else if (transaction.amount > 1000) score += 10;
    
    // Balance coverage risk
    const balanceRatio = transaction.amount / transaction.balance;
    if (balanceRatio > 1) score += 30; // Overdraft
    else if (balanceRatio > 0.8) score += 20;
    else if (balanceRatio > 0.5) score += 10;
    
    // Time risk (late night/early morning)
    const hour = parseInt(transaction.time);
    if (hour >= 0 && hour < 5) score += 20;
    else if (hour >= 22 || hour < 7) score += 10;
    
    // Category risk
    const riskyCategories = ['electronics', 'travel', 'gaming'];
    if (riskyCategories.includes(transaction.category)) score += 15;
    
    // Location risk
    const riskyLocations = ['Nigeria', 'Russia'];
    if (riskyLocations.includes(transaction.location)) score += 15;
    
    // Transaction type risk
    if (transaction.type === 'withdrawal' && transaction.amount > 1000) score += 10;
    
    // Age risk (very young or very old)
    if (transaction.age < 25 || transaction.age > 70) score += 5;
    
    // Add some randomness to simulate model uncertainty
    score += Math.random() * 10 - 5;
    
    // Ensure score is between 0 and 100
    return Math.max(0, Math.min(100, score));
}

// Update value displays for sliders
function setupSliders() {
    const sliders = [
        { id: 'amount', suffix: '', prefix: '$' },
        { id: 'balance', suffix: '', prefix: '$' },
        { id: 'age', suffix: ' years' },
        { id: 'time', suffix: ':00', format: 'time' }
    ];
    
    sliders.forEach(slider => {
        const input = document.getElementById(slider.id);
        const display = document.getElementById(`${slider.id}-value`);
        
        input.addEventListener('input', () => {
            let value = input.value;
            
            if (slider.format === 'time') {
                const hour = parseInt(value);
                const period = hour >= 12 ? 'PM' : 'AM';
                const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
                display.textContent = `${displayHour}:00 ${period}`;
            } else {
                display.textContent = `${slider.prefix || ''}${value}${slider.suffix}`;
            }
        });
    });
}

// Analyze transaction
function analyzeTransaction() {
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
    
    // Calculate fraud score
    const fraudScore = calculateFraudScore(transaction);
    
    // Update risk meter
    updateRiskMeter(fraudScore);
    
    // Update risk factors
    updateRiskFactors(transaction, fraudScore);
    
    // Update decision panel
    updateDecisionPanel(fraudScore);
    
    // Add animation class
    document.querySelector('.risk-analysis').classList.add('analyzing');
    setTimeout(() => {
        document.querySelector('.risk-analysis').classList.remove('analyzing');
    }, 1000);
}

// Update risk meter visualization
function updateRiskMeter(score) {
    const percentage = document.querySelector('.risk-percentage');
    const label = document.querySelector('.risk-label');
    const fill = document.querySelector('.gauge-fill');
    const needle = document.querySelector('.gauge-needle-line');
    
    // Update percentage
    percentage.textContent = Math.round(score) + '%';
    
    // Update label
    if (score < 30) {
        label.textContent = 'Low Risk';
        label.style.color = 'var(--success)';
    } else if (score < 70) {
        label.textContent = 'Medium Risk';
        label.style.color = 'var(--warning)';
    } else {
        label.textContent = 'High Risk';
        label.style.color = 'var(--danger)';
    }
    
    // Update gauge fill (arc length is ~251.2)
    const offset = 251.2 - (251.2 * score / 100);
    fill.style.strokeDashoffset = offset;
    
    // Update needle rotation (-90 to 90 degrees)
    const rotation = -90 + (180 * score / 100);
    needle.style.transform = `rotate(${rotation}deg)`;
}

// Update risk factors visualization
function updateRiskFactors(transaction, totalScore) {
    const factors = {
        amount: Math.min(100, (transaction.amount / 5000) * 100),
        time: isRiskyTime(transaction.time) ? 80 : 20,
        category: ['electronics', 'travel', 'gaming'].includes(transaction.category) ? 70 : 30,
        balance: transaction.amount > transaction.balance ? 100 : (transaction.amount / transaction.balance) * 100,
        location: ['Nigeria', 'Russia'].includes(transaction.location) ? 80 : 20
    };
    
    Object.entries(factors).forEach(([factor, value]) => {
        const fill = document.querySelector(`[data-factor="${factor}"]`);
        const impact = fill.parentElement.parentElement.querySelector('.factor-impact');
        
        fill.style.width = value + '%';
        
        if (value < 30) {
            impact.textContent = 'Low';
            impact.style.color = 'var(--success)';
        } else if (value < 70) {
            impact.textContent = 'Medium';
            impact.style.color = 'var(--warning)';
        } else {
            impact.textContent = 'High';
            impact.style.color = 'var(--danger)';
        }
    });
}

// Update decision panel
function updateDecisionPanel(score) {
    const icon = document.querySelector('.decision-icon');
    const title = document.querySelector('.decision-text h4');
    const description = document.querySelector('.decision-text p');
    const confidenceFill = document.querySelector('.confidence-fill');
    const confidenceValue = document.querySelector('.confidence-value');
    
    // Calculate confidence (higher score = higher confidence in fraud detection)
    const confidence = score > 50 ? 
        75 + (score - 50) * 0.5 : // 75-100% for fraud
        95 - score * 0.4; // 95-75% for legitimate
    
    confidenceFill.style.width = confidence + '%';
    confidenceValue.textContent = Math.round(confidence) + '%';
    
    if (score < 30) {
        icon.className = 'decision-icon';
        icon.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9 12l2 2 4-4"/></svg>';
        title.textContent = 'Transaction Approved';
        description.textContent = 'This transaction appears to be legitimate based on our analysis.';
    } else if (score < 70) {
        icon.className = 'decision-icon warning';
        icon.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 9v4"/><circle cx="12" cy="17" r="1"/></svg>';
        title.textContent = 'Additional Verification Required';
        description.textContent = 'This transaction requires additional verification before approval.';
    } else {
        icon.className = 'decision-icon danger';
        icon.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M15 9l-6 6"/><path d="M9 9l6 6"/></svg>';
        title.textContent = 'Transaction Blocked';
        description.textContent = 'This transaction has been flagged as potentially fraudulent.';
    }
}

// Helper function to check risky time
function isRiskyTime(hour) {
    const h = parseInt(hour);
    return (h >= 0 && h < 5) || (h >= 22);
}

// Load preset scenarios
function loadScenario(type) {
    const scenarios = {
        normal: {
            amount: 50,
            balance: 2000,
            age: 35,
            category: 'groceries',
            time: 14,
            location: 'USA',
            type: 'purchase'
        },
        suspicious: {
            amount: 2500,
            balance: 3000,
            age: 22,
            category: 'electronics',
            time: 23,
            location: 'USA',
            type: 'purchase'
        },
        fraud: {
            amount: 5000,
            balance: 2000,
            age: 19,
            category: 'travel',
            time: 3,
            location: 'Nigeria',
            type: 'withdrawal'
        },
        edge: {
            amount: 1200,
            balance: 1500,
            age: 45,
            category: 'gaming',
            time: 21,
            location: 'UK',
            type: 'purchase'
        }
    };
    
    const scenario = scenarios[type];
    
    // Set form values
    document.getElementById('amount').value = scenario.amount;
    document.getElementById('balance').value = scenario.balance;
    document.getElementById('age').value = scenario.age;
    document.getElementById('category').value = scenario.category;
    document.getElementById('time').value = scenario.time;
    document.getElementById('location').value = scenario.location;
    document.querySelector(`input[value="${scenario.type}"]`).checked = true;
    
    // Update displays
    document.getElementById('amount-value').textContent = `$${scenario.amount}`;
    document.getElementById('balance-value').textContent = `$${scenario.balance}`;
    document.getElementById('age-value').textContent = `${scenario.age} years`;
    
    const hour = scenario.time;
    const period = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
    document.getElementById('time-value').textContent = `${displayHour}:00 ${period}`;
    
    // Analyze automatically
    analyzeTransaction();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    setupSliders();
    
    // Add gradient definition to SVG
    const svg = document.querySelector('.risk-gauge');
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    const gradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
    gradient.setAttribute('id', 'gradient');
    gradient.setAttribute('x1', '0%');
    gradient.setAttribute('y1', '0%');
    gradient.setAttribute('x2', '100%');
    gradient.setAttribute('y2', '0%');
    
    const stop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
    stop1.setAttribute('offset', '0%');
    stop1.setAttribute('style', 'stop-color:#10b981');
    
    const stop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
    stop2.setAttribute('offset', '50%');
    stop2.setAttribute('style', 'stop-color:#f59e0b');
    
    const stop3 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
    stop3.setAttribute('offset', '100%');
    stop3.setAttribute('style', 'stop-color:#ef4444');
    
    gradient.appendChild(stop1);
    gradient.appendChild(stop2);
    gradient.appendChild(stop3);
    defs.appendChild(gradient);
    svg.insertBefore(defs, svg.firstChild);
    
    // Run initial analysis
    analyzeTransaction();
});

