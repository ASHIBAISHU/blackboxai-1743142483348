import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

def generate_synthetic_leads(num_records=1000):
    """Generate synthetic lead data for testing"""
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate company data
    industries = ['logistics', 'manufacturing', 'retail', 'technology', 'finance']
    lead_sources = ['web', 'referral', 'trade_show', 'cold_call', 'email']
    
    data = []
    for _ in range(num_records):
        # Generate company details
        company_name = fake.company()
        industry = np.random.choice(industries)
        company_size = np.random.randint(10, 10000)
        annual_revenue = np.random.randint(100000, 1000000000)
        num_employees = int(company_size * np.random.uniform(0.7, 1.3))
        lead_source = np.random.choice(lead_sources)
        past_interactions = np.random.poisson(2)
        
        # Generate conversion outcome with industry bias
        if industry == 'logistics':
            base_prob = 0.4
        elif industry == 'technology':
            base_prob = 0.6
        else:
            base_prob = 0.3
            
        # Adjust probability based on other factors
        prob = base_prob
        prob += 0.1 if lead_source == 'referral' else 0
        prob += 0.05 * past_interactions
        prob += 0.0000001 * annual_revenue  # Small effect from revenue
        
        # Add some noise
        prob = np.clip(prob + np.random.normal(0, 0.1), 0, 1)
        
        converted = np.random.binomial(1, prob)
        
        data.append({
            'company_name': company_name,
            'industry': industry,
            'company_size': company_size,
            'annual_revenue': annual_revenue,
            'num_employees': num_employees,
            'lead_source': lead_source,
            'past_interactions': past_interactions,
            'converted': converted,
            'created_at': fake.date_time_between(start_date='-1y', end_date='now')
        })
    
    df = pd.DataFrame(data)
    return df

if __name__ == '__main__':
    # Generate and save synthetic data
    leads_df = generate_synthetic_leads(5000)
    leads_df.to_csv('data/leads.csv', index=False)
    print("Generated synthetic lead data with shape:", leads_df.shape)