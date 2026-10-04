import pandas as pd

def extract_financials_from_excel(file_path):
    """
    Reads an uploaded corporate financial transaction spreadsheet,
    automatically aggregates total sales as Gross Revenue, and sums 
    operating costs to return clean parameters for tax assessment.
    """
    try:
        # Load the spreadsheet file using the pandas openpyxl engine
        df = pd.read_excel(file_path)
        
        # Normalize column name casing to avoid missing string matches
        df.columns = [str(col).strip().lower() for col in df.columns]
        
        # 1. Search for and aggregate Total Sales/Revenue
        revenue_columns = ['sales', 'revenue', 'turnover', 'gross sales']
        gross_revenue = 0.0
        
        for col in revenue_columns:
            if col in df.columns:
                gross_revenue = float(df[col].sum())
                break
                
        # 2. Search for and aggregate Total Allowable Operating Expenses
        expense_columns = ['expenses', 'costs', 'operating expenses', 'outflows']
        total_expenses = 0.0
        
        for col in expense_columns:
            if col in df.columns:
                total_expenses = float(df[col].sum())
                break
                
        # 3. Derive Assessable Profit deterministically via python arithmetic
        assessable_profit = max(0.0, gross_revenue - total_expenses)
        
        return {
            "gross_revenue": gross_revenue,
            "assessable_profit": assessable_profit,
            "extracted_successfully": True
        }
        
    except Exception as e:
        print(f"❌ Spreadsheet Parsing Error: {str(e)}")
        return {"gross_revenue": 0.0, "assessable_profit": 0.0, "extracted_successfully": False}

if __name__ == "__main__":
    print("⏳ Excel parsing module loaded successfully. Awaiting streaming upload hooks from the Streamlit UI layer...")
