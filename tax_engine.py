def calculate_nigerian_corporate_tax(gross_revenue: float, assessable_profit: float):
    """
    Calculates Nigerian Corporate Income Tax (CIT) and Tertiary Education Tax (TETFUND)
    based on the provisions of the current Finance Act rules.
    """
    # 1. Determine company classification tier and CIT rate based on Gross Revenue
    if gross_revenue <= 25000000:
        company_tier = "Small Enterprise"
        cit_rate = 0.00
    elif gross_revenue <= 100000000:
        company_tier = "Medium Enterprise"
        cit_rate = 0.20
    else:
        company_tier = "Large Enterprise"
        cit_rate = 0.30

    # 2. Statutory Tertiary Education Tax (TETFUND) is 3% of Assessable Profit for all corporate entities
    tetfund_rate = 0.03

    # 3. Execute tax assessments
    corporate_income_tax = assessable_profit * cit_rate
    education_tax = assessable_profit * tetfund_rate
    total_tax_liability = corporate_income_tax + education_tax

    # 4. Compile data results into a dictionary profile payload
    report = {
        "company_tier": company_tier,
        "gross_revenue": gross_revenue,
        "assessable_profit": assessable_profit,
        "cit_rate_applied": f"{cit_rate * 100}%",
        "corporate_income_tax": corporate_income_tax,
        "tetfund_rate_applied": f"{tetfund_rate * 100}%",
        "education_tax": education_tax,
        "total_tax_liability": total_tax_liability
    }
    
    return report

if __name__ == "__main__":
    # Test block to verify math executions locally
    print("⏳ Running engine test matrix locally...")
    sample_calculation = calculate_nigerian_corporate_tax(gross_revenue=45000000, assessable_profit=12000000)
    
    print("\n--- 📊 TEST RESULTS PROFILE ---")
    for key, value in sample_calculation.items():
        if isinstance(value, float) and key != "gross_revenue" and key != "assessable_profit":
            print(f"{key.replace('_', ' ').title()}: ₦{value:,.2f}")
        else:
            print(f"{key.replace('_', ' ').title()}: {value}")
