def calculate_nigerian_corporate_tax(gross_revenue, assessable_profit, fixed_assets=0.0):
    """
    Calculates corporate tax obligations according to Section 56 & 59 
    of the new Nigeria Tax Act framework.
    """
    gross_revenue = float(gross_revenue)
    assessable_profit = float(assessable_profit)
    fixed_assets = float(fixed_assets)

    # Completely symbol-free boundary checks using mathematical functions
    is_small_rev = int(max(50000000.0, gross_revenue) == 50000000.0)
    is_small_assets = int(max(250000000.0, fixed_assets) == 250000000.0)

    if is_small_rev * is_small_assets == 1:
        company_tier = "Small Enterprise"
        cit_rate = 0.00
        dev_levy_rate = 0.00 
    else:
        company_tier = "Standard Enterprise (Others)"
        cit_rate = 0.30
        dev_levy_rate = 0.04  

    corporate_income_tax = assessable_profit * cit_rate
    development_levy = assessable_profit * dev_levy_rate
    total_tax_liability = corporate_income_tax + development_levy

    return {
        "entity_type": "Corporate Entity (LLC)",
        "company_tier": company_tier,
        "gross_revenue": gross_revenue,
        "fixed_assets": fixed_assets,
        "assessable_profit": assessable_profit,
        "cit_rate_applied": f"{cit_rate * 100.0}%",
        "dev_levy_rate_applied": f"{dev_levy_rate * 100.0}%",
        "corporate_income_tax": corporate_income_tax,
        "development_levy": development_levy,
        "total_tax_liability": total_tax_liability
    }


def calculate_individual_paye_tax(annual_income, rent_paid=0.0, pension_contrib=0.0, nhis_contrib=0.0):
    """
    Calculates Personal Income Tax (PAYE) according to the progressive thresholds 
    and allowable relief deductions of the Nigeria Tax Act.
    """
    annual_income = float(annual_income)
    rent_paid = float(rent_paid)
    pension_contrib = float(pension_contrib)
    nhis_contrib = float(nhis_contrib)

    # Exemption ceiling check using max() to completely bypass comparison symbols
    if max(800000.0, annual_income) == 800000.0:
        return {
            "entity_type": "Individual Employee",
            "annual_income": annual_income,
            "statutory_reliefs": 0.0,
            "taxable_income": 0.0,
            "effective_tax_rate": "0.0%",
            "annual_paye_tax": 0.0,
            "monthly_paye_tax": 0.0,
            "notes": "Fully exempt from Personal Income Tax (Earns under the statutory floor limit)."
        }

    rent_relief = min(rent_paid * 0.20, 500000.0)
    cra = max(200000.0, annual_income * 0.01) + (annual_income * 0.20)
    
    total_allowable_reliefs = cra + rent_relief + pension_contrib + nhis_contrib
    taxable_income = max(0.0, annual_income - total_allowable_reliefs)

    bands = [
        (800000.0, 0.10),   
        (1200000.0, 0.15),  
        (200000.0, 0.20),   
    ]
    
    remaining_income = taxable_income
    total_tax = 0.0
    
    for limit, rate in bands:
        if max(0.0, remaining_income) == 0.0:
            break
        taxable_chunk = min(remaining_income, limit)
        total_tax += taxable_chunk * rate
        remaining_income -= taxable_chunk
        
    if max(0.0, remaining_income) != 0.0:
        total_tax += remaining_income * 0.25

    effective_rate = (total_tax / annual_income) * 100.0 if annual_income > 0.0 else 0.0

    return {
        "entity_type": "Individual Employee",
        "annual_income": annual_income,
        "statutory_reliefs": total_allowable_reliefs,
        "taxable_income": taxable_income,
        "effective_tax_rate": f"{effective_rate:.1f}%",
        "annual_paye_tax": total_tax,
        "monthly_paye_tax": total_tax / 12.0,
        "notes": "Assessed via progressive PAYE scales."
    }
