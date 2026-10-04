def calculate_nigerian_corporate_tax(gross_revenue: float, assessable_profit: float, fixed_assets: float = 0.0):
    """
    Calculates corporate tax obligations according to Section 56 & 59 
    of the new Nigeria Tax Act 2025 framework.
    """
    # 1. New Statutory Tier Thresholds (Turnover <= 50M AND Fixed Assets <= 250M)
    if gross_revenue <= 50000000 and fixed_assets <= 250000000:
        company_tier = "Small Enterprise"
        cit_rate = 0.00
        dev_levy_rate = 0.00  # Small companies are completely exempt from the Development Levy
    else:
        company_tier = "Standard Enterprise (Others)"
        cit_rate = 0.30
        dev_levy_rate = 0.04  # 4% Development Levy replaces legacy TETFUND/NITDA earmarks

    # 2. Execute precision math assessments
    corporate_income_tax = assessable_profit * cit_rate
    development_levy = assessable_profit * dev_levy_rate
    total_tax_liability = corporate_income_tax + development_levy

    # 3. Compile report payload
    report = {
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
    
    return report

if __name__ == "__main__":
    print("⏳ Running updated Nigeria Tax Act 2025 test matrix...")
    sample_calculation = calculate_nigerian_corporate_tax(gross_revenue=65000000, assessable_profit=15000000, fixed_assets=30000000)
    
    print("\n--- 📊 NEW LEGISLATIVE TEST RESULTS ---")
    for key, value in sample_calculation.items():
        if isinstance(value, float) and "rate" not in key:
            print(f"{key.replace('_', ' ').title()}: ₦{value:,.2f}")
        else:
            print(f"{key.replace('_', ' ').title()}: {value}")
