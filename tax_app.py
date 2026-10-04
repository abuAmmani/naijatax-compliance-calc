import streamlit as st
import os
from tax_engine import calculate_nigerian_corporate_tax
from excel_parser import extract_financials_from_excel

st.set_page_config(page_title="NaijaTax AI", page_icon="📊", layout="centered")

st.title("📊 NaijaTax AI: Smart Corporate Tax Calculator")
st.write("Determine your company's tax bracket, Corporate Income Tax (CIT), and Education Tax (TETFUND) compliance liabilities under current Nigerian Finance Act regulations.")

# Create clean side-by-side layout tabs for data entry styles
tab1, tab2 = st.tabs(["📁 Excel File Upload Parser", "✍️ Manual Entry Form"])

gross_revenue = 0.0
assessable_profit = 0.0
data_ready = False

# -------------------------------------------------------------
# TAB 1: AUTOMATED EXCEL PARSER LAYER
# -------------------------------------------------------------
with tab1:
    st.subheader("Upload Corporate Financial Spreadsheet")
    st.write("Our data processing engine will automatically aggregate your Sales and Operating Expenses rows.")
    
    uploaded_file = st.file_uploader("Drag and drop your company .xlsx or .csv ledger here:", type=["xlsx", "csv"])
    
    if uploaded_file:
        # Save file temporarily to disk to pass to the parser module
        temp_filename = "temp_uploaded_ledger.xlsx"
        with open(temp_filename, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        with st.spinner("Extracting parameters out of spreadsheet arrays..."):
            extracted_data = extract_financials_from_excel(temp_filename)
            
        if extracted_data["extracted_successfully"]:
            st.success("✅ Data extracted successfully from file logs!")
            gross_revenue = extracted_data["gross_revenue"]
            assessable_profit = extracted_data["assessable_profit"]
            data_ready = True
            
            # Show extracted parameters metrics inside an informational block
            st.metric(label="Aggregated Gross Revenue", value=f"₦{gross_revenue:,.2f}")
            st.metric(label="Calculated Assessable Net Profit", value=f"₦{assessable_profit:,.2f}")
        else:
            st.error("❌ Failed to parse financial rows. Please double check column headers or fill the manual form.")
            
        # Clean up temp file safely from disk storage folder
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

# -------------------------------------------------------------
# TAB 2: MANUAL INPUT FORM LAYER
# -------------------------------------------------------------
with tab2:
    st.subheader("Manual Financial Ledger Entry Form")
    st.write("Input your aggregated high-level top-line and net parameters directly below:")
    
    manual_revenue = st.number_input("Total Annual Sales Invoices / Gross Revenue (₦):", min_value=0.0, step=100000.0)
    manual_expenses = st.number_input("Total Allowable Operating Expenses (₦):", min_value=0.0, step=50000.0)
    
    if st.button("Run Manual Form Calculations"):
        gross_revenue = manual_revenue
        assessable_profit = max(0.0, manual_revenue - manual_expenses)
        data_ready = True

# -------------------------------------------------------------
# TAX CALCULATION REPORT DISPLAY SPACE
# -------------------------------------------------------------
if data_ready:
    st.markdown("---")
    with st.spinner("Compiling structural tax reporting matrices..."):
        # Trigger our deterministic tax math script calculations
        tax_report = calculate_nigerian_corporate_tax(gross_revenue, assessable_profit)
        
    st.header("📊 Official Corporate Tax Assessment Report")
    
    # Visual grid metrics setup layout blocks
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Company Classification Tier:**\n\n### {tax_report['company_tier']}")
    with col2:
        st.warning(f"**Total Consolidated Tax Liability:**\n\n### ₦{tax_report['total_tax_liability']:,.2f}")
        
    # Detailed data parameter breakdowns
    st.markdown("### Detailed Structural Breakdowns:")
    st.write(f"• **Corporate Income Tax (CIT) Rate Applied:** {tax_report['cit_rate_applied']}")
    st.write(f"• **Calculated Corporate Income Tax (CIT):** ₦{tax_report['corporate_income_tax']:,.2f}")
    st.write(f"• **Tertiary Education Tax (TETFUND) Rate Applied:** {tax_report['tetfund_rate_applied']} (Assessable Profit baseline)")
    st.write(f"• **Calculated Education Tax:** ₦{tax_report['education_tax']:,.2f}")
    
    st.success("🤖 Next Stage: Connect the RAG legal memory files to display the exact supporting Finance Act statutory sections next to these metrics.")
