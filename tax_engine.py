def calculate_individual_paye_tax(annual_income):
    """
    Calculates Personal Income Tax (PAYE) using the progressive tax bands 
    mandated by the new Nigeria Tax Act 2025.
    """
    if annual_income  0:
        total_tax += remaining_income * 0.25

    effective_rate = (total_tax / annual_income) * 100 if annual_income > 0 else 0

    return {
        "entity_type": "Individual Employee",
        "annual_income": float(annual_income),
        "taxable_income": taxable_income,
        "effective_tax_rate": f"{effective_rate:.1f}%",
        "annual_paye_tax": total_tax,
        "monthly_paye_tax": total_tax / 12.0,
        "notes": "Assessed via progressive PAYE rate thresholds (10% to 25% scale)."
    }


def calculate_nigerian_corporate_tax(gross_revenue, assessable_profit, fixed_assets=0.0):
    """
    Calculates corporate tax obligations according to Section 56 & 59 
    of the new Nigeria Tax Act 2025 framework.
    """
    if float(gross_revenue) <= 50000000.0 and float(fixed_assets) <= 250000000.0:
        company_tier = "Small Enterprise"
        cit_rate = 0.00
        dev_levy_rate = 0.00 
    else:
        company_tier = "Standard Enterprise (Others)"
        cit_rate = 0.30
        dev_levy_rate = 0.04  

    corporate_income_tax = float(assessable_profit) * cit_rate
    development_levy = float(assessable_profit) * dev_levy_rate
    total_tax_liability = corporate_income_tax + development_levy

    return {
        "entity_type": "Corporate Entity (LLC)",
        "company_tier": company_tier,
        "gross_revenue": float(gross_revenue),
        "fixed_assets": float(fixed_assets),
        "assessable_profit": float(assessable_profit),
        "cit_rate_applied": f"{cit_rate * 100}%",
        "corporate_income_tax": corporate_income_tax,
        "dev_levy_rate_applied": f"{dev_levy_rate * 100}%",
        "development_levy": development_levy,
        "total_tax_liability": total_tax_liability
    }
