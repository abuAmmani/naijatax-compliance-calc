import streamlit as st
import os
from dotenv import load_dotenv
from tax_engine import calculate_nigerian_corporate_tax, calculate_individual_paye_tax
from excel_parser import extract_financials_from_excel
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

st.set_page_config(page_title="NaijaTax AI Hub", page_icon="🏛️", layout="wide")

st.title("🏛️ NaijaTax AI: Omnichannel Statutory Assessment Platform")
st.write("Evaluate regulatory tax liabilities across individuals, dynamic relief allowances, and multi-tier business operations under the current **Nigeria Tax Act** framework.")
st.markdown("---")

DB_DIR = "tax_vector_db"

if not os.path.exists(DB_DIR):
    st.warning("⚠️ Database missing. Please run 'python index_tax_db.py' first.")
elif not os.environ.get("GROQ_API_KEY"):
    st.error("❌ Add your secure GROQ_API_KEY into your environment secrets portal.")
else:
    tax_category = st.radio(
        "**Select Assessment Group Category:**",
        ["👤 Individual Employee / Salaried Earner", "🏢 Registered Corporate Entity (LLC / Business)"],
        horizontal=True
    )

    gross_revenue, assessable_profit, fixed_assets, annual_income = 0.0, 0.0, 0.0, 0.0
    rent_paid, pension_contrib, nhis_contrib = 0.0, 0.0, 0.0
    data_ready = False
    engine_mode = ""

    st.markdown("---")
    
    # -------------------------------------------------------------
    # UPGRADED ROUTE A: INDIVIDUAL CALCULATION PANEL WITH NEW FIELDS
    # -------------------------------------------------------------
    if tax_category == "👤 Individual Employee / Salaried Earner":
        engine_mode = "individual"
        st.subheader("👤 Personal Income Tax (PAYE) Assessment Form")
        
        i_col1, i_col2 = st.columns(2)
        with i_col1:
            input_income = st.number_input("Total Gross Annual Salary / Revenue (₦):", min_value=0.0, step=50000.0, format="%.2f")
            input_pension = st.number_input("Annual Statutory Pension Contribution (8%) (₦):", min_value=0.0, step=10000.0, format="%.2f")
        with i_col2:
            input_rent = st.number_input("Total Annual Rent Paid (For Rent Relief Allowance) (₦):", min_value=0.0, step=50000.0, format="%.2f")
            input_nhis = st.number_input("Annual Health Insurance (NHIS) Contribution (₦):", min_value=0.0, step=50000.0, format="%.2f")
            
        if st.button("Calculate Personal Income Tax Report", use_container_width=True):
            annual_income = input_income
            rent_paid = input_rent
            pension_contrib = input_pension
            nhis_contrib = input_nhis
            data_ready = True

    # -------------------------------------------------------------
    # ROUTE B: CORPORATE CALCULATION PANEL
    # -------------------------------------------------------------
    else:
        engine_mode = "corporate"
        tab1, tab2 = st.tabs(["📁 Spreadsheet Ingestion Parser", "✍️ Manual Data Entry Form"])
        
        with tab1:
            uploaded_file = st.file_uploader("Upload corporate transaction sheet:", type=["xlsx", "csv"])
            if uploaded_file:
                temp_filename = "temp_uploaded_ledger.xlsx"
                with open(temp_filename, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                extracted_data = extract_financials_from_excel(temp_filename)
                if extracted_data["extracted_successfully"]:
                    st.success("Data parsed from sheet rows!")
                    gross_revenue = extracted_data["gross_revenue"]
                    assessable_profit = extracted_data["assessable_profit"]
                    fixed_assets = st.number_input("Enter Book Value of Fixed Assets (₦):", min_value=0.0, step=500000.0, format="%.2f", key="excel_fa")
                    if st.button("Process Spreadsheet Tax Metrics", use_container_width=True):
                        data_ready = True
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)

        with tab2:
            manual_revenue = st.number_input("Total Annual Gross Revenue (₦):", min_value=0.0, step=100000.0, format="%.2f")
            manual_expenses = st.number_input("Total Allowable Operating Expenses (₦):", min_value=0.0, step=50000.0, format="%.2f")
            manual_assets = st.number_input("Total Net Value of Fixed Assets (₦):", min_value=0.0, step=500000.0, format="%.2f")
            if st.button("Execute Business Assessment Report", use_container_width=True):
                gross_revenue = manual_revenue
                assessable_profit = max(0.0, manual_revenue - manual_expenses)
                fixed_assets = manual_assets
                data_ready = True

    # -------------------------------------------------------------
    # RENDER COMMA REPORT LAYOUTS
    # -------------------------------------------------------------
    if data_ready:
        st.markdown("---")
        st.header("📊 Official Tax Assessment Summary Report")
        
        if engine_mode == "individual":
            report = calculate_individual_paye_tax(annual_income, rent_paid, pension_contrib, nhis_contrib)
            st.markdown(f"""

| Parameter Metric Baseline | Values |
| :--- | :--- |
| **Assessed Entity Group** | {report['entity_type']} |
| **Total Gross Annual Income** | ₦{report['annual_income']:,.2f} |
| **Applied Statutory Deductions / Reliefs** | ₦{report['statutory_reliefs']:,.2f} |
| **Calculated Taxable Net Baseline** | ₦{report['taxable_income']:,.2f} |
| **Effective Tax Rate Percentage** | {report['effective_tax_rate']} |
| **Total Annual PAYE Tax Liability** | **₦{report['annual_paye_tax']:,.2f}** |
| **Estimated Monthly PAYE Deductions** | **₦{report['monthly_paye_tax']:,.2f}** |
""")
            st.info(f"**Compliance Ingestion Note:** {report['notes']}")
            query_input = f"Individual earnings: ₦{annual_income:,.2f}, Relief allowances applied: ₦{report['statutory_reliefs']:,.2f}"
            
        else:
            report = calculate_nigerian_corporate_tax(gross_revenue, assessable_profit, fixed_assets)
            st.markdown(f"""

| Parameter Metric Baseline | Values |
| :--- | :--- |
| **Assessed Entity Group** | {report['entity_type']} |
| **Classification Category Bracket** | {report['company_tier']} |
| **Aggregated Gross Revenue** | ₦{report['gross_revenue']:,.2f} |
| **Total Corporate Net Profit** | ₦{report['assessable_profit']:,.2f} |
| **Assessed Corporate Income Tax (CIT)** | **₦{report['corporate_income_tax']:,.2f}** ({report['cit_rate_applied']}) |
| **Assessed Development Levy Liability** | **₦{report['development_levy']:,.2f}** ({report['dev_levy_rate_applied']}) |
| **Total Consolidated Tax Liability** | **₦{report['total_tax_liability']:,.2f}** |
""")
            query_input = f"Corporate entity turnover: ₦{gross_revenue:,.2f}, Fixed assets: ₦{fixed_assets:,.2f}"

        # Trigger RAG Context Clauses Delivery
        st.markdown("---")
        st.subheader("🤖 Smart Legislative Advisor Analysis")
        with st.spinner("Retrieving corresponding text chunks from the Nigeria Tax Act index..."):
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            db = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
            retriever = db.as_retriever(search_kwargs={"k": 2})
            llm = ChatGroq(model_name="openai/gpt-oss-20b", temperature=0.1)

            system_prompt = (
                "You are an expert Nigerian Tax Consultant analyzing the new Nigeria Tax Act rules.\n"
                "Review the retrieved legislative text below and explain the specific tax obligations, progressive bands, or complete exemptions for this scenario.\n"
                "Explicitly ground your response in the provided text. Format currency balances cleanly with commas.\n\n"
                "Retrieved Clauses:\n{context}"
            )
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{user_query}"),
            ])
            chain = create_retrieval_chain(retriever, create_stuff_documents_chain(llm, prompt))
            response = chain.invoke({"input": query_input, "user_query": query_input})
            
            st.info(response["answer"])
            with st.expander("🔍 View Verifiable Source Material Utilized"):
                for doc in response["context"]:
                    st.info(doc.page_content)
