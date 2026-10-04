import streamlit as st
import os
from dotenv import load_dotenv
from tax_engine import calculate_nigerian_corporate_tax
from excel_parser import extract_financials_from_excel
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Load keys from your local hidden .env file
load_dotenv()

# Page configurations for a wider, executive workspace
st.set_page_config(page_title="NaijaTax AI Dashboard", page_icon="🏛️", layout="wide")

# Custom CSS styling to introduce clean layout typography and modern visual containers
st.markdown("""
    <style>
    .report-card {
        padding: 24px;
        border-radius: 12px;
        background-color: #f8f9fa;
        border-left: 5px solid #0066cc;
        margin-bottom: 20px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #1e293b;
    }
    </style>
""", unsafe_allow_html=True)

# Main Title and Professional Context Subheader
st.title("🏛️ NaijaTax AI: Corporate Tax Compliance Suite")
st.markdown("##### **Enterprise-Grade Fiscal Assessment Engine & Legislative Retrieval Pipeline**")
st.write("Evaluate corporate tax liabilities, evaluate threshold exemptions, and retrieve context-grounded statutory clauses under the current **Nigeria Tax Act** framework.")
st.markdown("---")

DB_DIR = "tax_vector_db"

if not os.path.exists(DB_DIR):
    st.warning("⚠️ Database storage folder not found locally. Please run 'python index_tax_db.py' first.")
elif not os.environ.get("GROQ_API_KEY"):
    st.error("❌ Setup incomplete: Please add your free GROQ_API_KEY to your secure configuration vault.")
else:
    # High-level metrics tracking layout blocks
    gross_revenue = 0.0
    assessable_profit = 0.0
    fixed_assets = 0.0
    data_ready = False

    # Side-by-side organizational design: Input Workspace vs Documentation Panel
    left_panel, right_panel = st.columns([1, 1], gap="large")

    with left_panel:
        st.markdown("### 📥 Financial Data Ingestion")
        tab1, tab2 = st.tabs(["📁 Automated Spreadsheet Parser", "✍️ Manual Financial Ledger Form"])

        # -------------------------------------------------------------
        # TAB 1: AUTOMATED EXCEL PARSER LAYER
        # -------------------------------------------------------------
        with tab1:
            st.write("Upload your company balance sheet or ledger rows to extract parameters instantly.")
            uploaded_file = st.file_uploader("Drag and drop your company .xlsx or .csv sheet here:", type=["xlsx", "csv"])
            
            if uploaded_file:
                temp_filename = "temp_uploaded_ledger.xlsx"
                with open(temp_filename, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                    
                with st.spinner("Parsing spreadsheet arrays..."):
                    extracted_data = extract_financials_from_excel(temp_filename)
                    
                if extracted_data["extracted_successfully"]:
                    st.success("✅ Financial rows parsed successfully!")
                    gross_revenue = extracted_data["gross_revenue"]
                    assessable_profit = extracted_data["assessable_profit"]
                    
                    fixed_assets = st.number_input("Enter Book Value of Fixed Assets (₦):", min_value=0.0, step=500000.0, format="%.2f", key="excel_fa")
                    if st.button("Generate Assessment from Spreadsheet", use_container_width=True):
                        data_ready = True
                else:
                    st.error("❌ Failed to parse data. Please check column headers or use manual entry.")
                    
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)

        # -------------------------------------------------------------
        # TAB 2: MANUAL INPUT FORM LAYER
        # -------------------------------------------------------------
        with tab2:
            st.write("Input your high-level financial parameters line by line:")
            manual_revenue = st.number_input("Total Annual Gross Revenue (₦):", min_value=0.0, step=100000.0, format="%.2f")
            manual_expenses = st.number_input("Total Allowable Operating Expenses (₦):", min_value=0.0, step=50000.0, format="%.2f")
            manual_assets = st.number_input("Total Net Value of Fixed Assets (₦):", min_value=0.0, step=500000.0, format="%.2f")
            
            if st.button("Execute Financial Assessment Report", use_container_width=True):
                gross_revenue = manual_revenue
                assessable_profit = max(0.0, manual_revenue - manual_expenses)
                fixed_assets = manual_assets
                data_ready = True

    with right_panel:
        st.markdown("### 📋 Legislative Quick-Reference")
        with st.container(border=True):
            st.markdown("""
            **Statutory Corporate Tax Brackets (Current Nigeria Tax Act):**
            * **Small Company Threshold:** Gross Revenue ≤ **₦50,000,000.00** **AND** Fixed Assets ≤ **₦250,000,000.00**.
            * **Tax Exemptions:** Eligible Small Companies qualify for a **0% CIT Rate** and are exempt from the Development Levy.
            * **Standard Company Bracket:** All entities exceeding small thresholds are assessed at a **30% CIT Rate** and a **4% Unified Development Levy**.
            """)

    # -------------------------------------------------------------
    # FINANCIAL CALCULATION & RAG ADVICE DISPLAY
    # -------------------------------------------------------------
    if data_ready:
        st.markdown("---")
        
        # Trigger Deterministic Math Engine
        tax_report = calculate_nigerian_corporate_tax(gross_revenue, assessable_profit, fixed_assets)
        
        st.subheader("📊 Official Fiscal Assessment Summary")
        st.caption("Calculated in accordance with Section 56 & 59 of the current Nigeria Tax Act. All figures are rendered in Nigerian Naira (₦).")
        
        # Display professional structured table with comma formatting for numeric values
        st.markdown(f"""

        | Assessment Parameter | Value / Metric Baseline |
        | :--- | :--- |
        | **Assessed Company Classification Tier** | `{tax_report['company_tier']}` |
        | **Aggregated Gross Top-Line Revenue** | ₦{tax_report['gross_revenue']:,.2f} |
        | **Total Declared Net Fixed Assets** | ₦{tax_report['fixed_assets']:,.2f} |
        | **Calculated Assessable Net Profit** | ₦{tax_report['assessable_profit']:,.2f} |
        | **Corporate Income Tax (CIT) Rate Applied** | {tax_report['cit_rate_applied']} |
        | **Assessed Corporate Income Tax (CIT)** | **₦{tax_report['corporate_income_tax']:,.2f}** |
        | **Unified Development Levy Rate Applied** | {tax_report['dev_levy_rate_applied']} |
        | **Assessed Development Levy Liability** | **₦{tax_report['development_levy']:,.2f}** |
        | ### **Total Consolidated Tax Liability** | ### **₦{tax_report['total_tax_liability']:,.2f}** |
        """)
        
        # -------------------------------------------------------------
        # SEMANTIC RAG COMPLIANCE GENERATOR
        # -------------------------------------------------------------
        st.markdown("---")
        st.subheader("🤖 AI Regulatory Compliance Insights")
        
        with st.spinner("Querying active statutory vector structures..."):
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            db = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
            retriever = db.as_retriever(search_kwargs={"k": 2})

            llm = ChatGroq(model_name="openai/gpt-oss-20b", temperature=0.1)

            system_prompt = (
                "You are an expert Nigerian Corporate Tax Consultant specializing in the current Nigeria Tax Act rules.\n"
                "Review the following retrieved legislative clauses and explain the exact compliance scenario for this company size.\n"
                "Explicitly point out if they qualify for the 0% CIT rate exemption for small businesses (turnover under 50 Million and fixed assets under 250 Million).\n"
                "Format currency figures clearly with commas. Structure your notes using clean bullet points.\n\n"
                "Retrieved Legislative Text:\n{context}"
            )

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "My company generated gross revenue of ₦{revenue:,.2f} and holds fixed assets worth ₦{assets:,.2f}. Explain my compliance duties and exemptions under the law."),
            ])

            question_answer_chain = create_stuff_documents_chain(llm, prompt)
            rag_chain = create_retrieval_chain(retriever, question_answer_chain)

            input_text = f"Gross Revenue: {gross_revenue}, Fixed Assets: {fixed_assets}"
            response = rag_chain.invoke({
                "input": input_text,
                "revenue": gross_revenue,
                "assets": fixed_assets
            })

            # Display response beautifully inside a custom stylized block container
            st.markdown(f"""
            <div class="report-card">
                {response["answer"]}
            </div>
            """, unsafe_allow_html=True)

            # Source transparency expander panel
            with st.expander("🔍 Inspect Supporting Statutory Source Materials"):
                for doc in response["context"]:
                    st.markdown(f"**Page Reference: {doc.metadata.get('page', 'N/A')}**")
                    st.info(doc.page_content)
