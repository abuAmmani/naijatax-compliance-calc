def calculate_individual_paye_tax(annual_income: float):
    """
    Calculates Personal Income Tax (PAYE) using the progressive tax bands 
    mandated by the new Nigeria Tax Act 2025.
    """
    # Section 38: Incomes of ₦800,000 or less are 100% tax-exempt
    if annual_income  0:
        total_tax += remaining_income * 0.25

    effective_rate = (total_tax / annual_income) * 100 if annual_income > 0 else 0

    return {
        "entity_type": "Individual Employee",
        "annual_income": annual_income,
        "taxable_income": taxable_income,
        "effective_tax_rate": f"{effective_rate:.1f}%",
        "annual_paye_tax": total_tax,
        "monthly_paye_tax": total_tax / 12,
        "notes": "Assessed via progressive PAYE rate thresholds (10% to 25% scale)."
    }


def calculate_nigerian_corporate_tax(gross_revenue: float, assessable_profit: float, fixed_assets: float = 0.0):
    """
    Calculates corporate tax obligations according to Section 56 & 59 
    of the new Nigeria Tax Act 2025 framework.
    """
    if gross_revenue <= 50000000 and fixed_assets <= 250000000:
        company_tier = "Small Enterprise"
        cit_rate = 0.00
        dev_levy_rate = 0.00 
    else:
        company_tier = "Standard Enterprise (Others)"
        cit_rate = 0.30
        dev_levy_rate = 0.04  # 4% Unified Development Levy

    corporate_income_tax = assessable_profit * cit_rate
    development_levy = assessable_profit * dev_levy_rate
    total_tax_liability = corporate_income_tax + development_levy

    return {
        "entity_type": "Corporate Entity (LLC)",
        "company_tier": company_tier,
        "gross_revenue": gross_revenue,
        "fixed_assets": fixed_assets,
        "assessable_profit": assessable_profit,
        "cit_rate_applied": f"{cit_rate * 100}%",
        "corporate_income_tax": corporate_income_tax,
        "dev_levy_rate_applied": f"{dev_levy_rate * 100}%",
        "development_levy": development_levy,
        "total_tax_liability": total_tax_liability
    }
