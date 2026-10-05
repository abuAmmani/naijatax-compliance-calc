import streamlit as st
import os
from dotenv import load_dotenv
from tax_engine import calculate_nigerian_corporate_tax, calculate_individual_paye_tax
from excel_parser import extract_financials_from_excel
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

st.set_page_config(page_title="NaijaTax AI Suite", page_icon="🏛️", layout="wide")

st.title("🏛️ NaijaTax AI: Omnichannel Statutory Assessment Platform")
st.write("Evaluate dynamic regulatory tax liabilities under the current framework.")
st.markdown("---")

DB_DIR = "tax_vector_db"

if not os.path.exists(DB_DIR):
    st.warning("⚠️ Database missing.")
elif not os.environ.get("GROQ_API_KEY"):
    st.error("❌ GROQ_API_KEY missing.")
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

    if tax_category == "👤 Individual Employee / Salaried Earner":
        engine_mode = "individual"
        input_income = st.number_input("Total Gross Annual Salary (₦):", min_value=0.0, step=50000.0)
        input_pension = st.number_input("Annual Pension Contribution (₦):", min_value=0.0, step=10000.0)
        input_rent = st.number_input("Total Annual Rent Paid (₦):", min_value=0.0, step=50000.0)
        input_nhis = st.number_input("Annual Health Insurance (NHIS) (₦):", min_value=0.0, step=50000.0)
            
        if st.button("Calculate Personal Income Tax Report"):
            annual_income = input_income
            rent_paid = input_rent
            pension_contrib = input_pension
            nhis_contrib = input_nhis
            data_ready = True
    else:
        engine_mode = "corporate"
        manual_revenue = st.number_input("Total Annual Gross Revenue (₦):", min_value=0.0, step=100000.0)
        manual_expenses = st.number_input("Total Allowable Operating Expenses (₦):", min_value=0.0, step=50000.0)
        manual_assets = st.number_input("Total Net Value of Fixed Assets (₦):", min_value=0.0, step=500000.0)
        if st.button("Execute Business Assessment Report"):
            gross_revenue = manual_revenue
            assessable_profit = max(0.0, manual_revenue - manual_expenses)
            fixed_assets = manual_assets
            data_ready = True

    if data_ready:
        if engine_mode == "individual":
            report = calculate_individual_paye_tax(annual_income, rent_paid, pension_contrib, nhis_contrib)
            st.success(f"Total Annual PAYE Tax Liability: ₦{report['annual_paye_tax']:,.2f}")
            query_input = f"Individual annual earnings: N{annual_income:,.2f}"
        else:
            report = calculate_nigerian_corporate_tax(gross_revenue, assessable_profit, fixed_assets)
            st.success(f"Total Consolidated Corporate Tax Liability: ₦{report['total_tax_liability']:,.2f}")
            query_input = f"Corporate entity turnover: N{gross_revenue:,.2f}"

        st.markdown("---")
        with st.spinner("Retrieving text chunks..."):
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            db = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
            retriever = db.as_retriever(search_kwargs={"k": 2})
            llm = ChatGroq(model_name="mixtral-8x7b-32768", temperature=0.1)

            system_prompt = "You are a Nigerian Tax Consultant. Review context:\n{context}\n\nQuestion: {user_query}"
            prompt = ChatPromptTemplate.from_template(system_prompt)
            
            # Format retrieved context documents into text
            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)
            
            # Form modern cross-compatible chain execution loop using LCEL
            rag_chain = (
                {"context": retriever | format_docs, "user_query": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
            )
            
            response = rag_chain.invoke(query_input)
            st.info(response)
