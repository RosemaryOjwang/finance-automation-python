import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

#Set page configuration
st.set_page_config(page_title="Simple Finance App", layout="wide")

category_file = "categories.json"

if "categories" not in st.session_state:
    st.session_state.categories = {
        "Uncategorized": []
    }

if os.path.exists("category_file"):
    with open("category_file", "r") as f:
        st.session_state.categories = json.load(f)

def save_categories():
    with open("category_file", "w") as f:
        json.dump(st.session_state.categories, f)

def categorize_transactions(df):
    df["Category"] = "Uncategorized"

    for category, keywords in st.session_state.categories.items():
        if category == "Uncategorized" or not keywords:
            continue

        lowered_keywords = [keyword.lower().strip() for keyword in keywords]
        
        for idx, row in df.iterrows():
            details = row["Details"].lower().strip()
            if details in lowered_keywords:
                df.at[idx, "Category"] = category

    return df


#File upload

def load_transactions(file):
    try:
        df = pd.read_csv(file)
        df.columns = [col.strip() for col in df.columns]
        df["Amount"] = df["Amount"].str.replace(",", "").astype(float)
        df["Date"] = pd.to_datetime(df["Date"], format="%d %b %Y")
        
        return categorize_transactions(df)
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def add_keyword_to_category(category, keyword):
    keyword = keyword.strip()
    if keyword and keyword not in st.session_state.categories[category]:
        st.session_state.categories[category].append(keyword)
        save_categories()
        return True

def main():
    st.title("Simple Finance Dashboard")
    uploaded_file = st.file_uploader("Upload your transaction CSV file", type=["csv"])

    if uploaded_file is not None:
        df = load_transactions(uploaded_file)

#Separate transactions based on the Debit/Credit column into Debit and Credit
        if df is not None:
            debits_df = df[df["Debit/Credit"] == "Debit"].copy()
            credits_df = df[df["Debit/Credit"] == "Credit"].copy()

            st.session_state.debits_df = debits_df.copy()

#Create Expenses (Debits), Payments (Credits)  and Visualization tabs
            tab1, tab2, tab3 = st.tabs(["Expenses (Debits)", "Payments (Credits)", "Visualizations"])
            with tab1:
                new_category = st.text_input("New Category Name")
                add_button = st.button("Add Category")

                if add_button and new_category:
                    if new_category not in st.session_state.categories:
                        st.session_state.categories[new_category] = []
                        save_categories()
                        st.success(f"Added a new category: {new_category}")
                        st.rerun()

                st.subheader("Your Expenses")
                edited_df = st.data_editor(
                    st.session_state.debits_df[["Date", "Details", "Amount", "Category"]],
                    column_config={
                        "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                        "Amount": st.column_config.NumberColumn("Amount", format="%.2f KES"),
                        "Category": st.column_config.SelectboxColumn(
                            "Category",
                            options=list(st.session_state.categories.keys())
                        )
                    },
                    hide_index=True,
                    use_container_width=True,
                    key="category_editor"
                )
                save_button = st.button("Apply Changes", type="primary")
                if save_button:
                    for idx, row in edited_df.iterrows():
                        new_category = row["Category"]
                        if new_category == st.session_state.debits_df.at[idx, "Category"]:
                            continue

                        details = row["Details"]
                        st.session_state.debits_df.at[idx, "Category"] = new_category
                        add_keyword_to_category(new_category, details)

                 


            with tab2:
                st.subheader("Payments Summary")
                total_payments = credits_df["Amount"].sum()
                st.metric("Total Payments", f"{total_payments:,.2f} KES")
                st.write(credits_df)

            with tab3:
                st.subheader("Financial Visualizations")
                #Show summary of categories
                st.subheader('Expense Summary')
                category_totals = st.session_state.debits_df.groupby("Category")["Amount"].sum().reset_index()
                category_totals = category_totals.sort_values("Amount", ascending=False)

                #Calculate totals for pie chart
                total_expenses = category_totals["Amount"].sum()
                total_payments = credits_df["Amount"].sum()
                remaining_balance = total_payments - total_expenses

                pie_data = pd.DataFrame({
                    "Category": ["Total Expenses", "Remaining Balance"],
                    "Amount": [total_expenses, remaining_balance]
                })

                #Display as a different dataframe
                st.dataframe(
                    category_totals,
                    column_config={
                        "Amount": st.column_config.NumberColumn("Amount", format="%.2f KES")
                    },
                    use_container_width=True,
                    hide_index=True
                )

                #Create a bar chart for the different categories
                fig = px.bar(
                    category_totals,
                    y="Amount",
                    x="Category",
                    title="Expenses by Category",
                    text="Amount"
                )

                fig.update_traces(
                    texttemplate='%{text}',
                    textposition='outside',
                    textfont_size=10,
                    marker_color='#FFDB58'
                )

                fig.update_layout(
                    uniformtext_minsize=8,
                    uniformtext_mode='hide',
                    xaxis_title='Category',
                    yaxis_title='Amount (KES)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict( r=80),
                    width=900,
                    showlegend=False
                )

                #Create pie chart for payments vs expenses
                color_map = {
                    'Total Expenses': '#FFDB58',
                    'Remaining Balance': '#000080'
                }
                pie_fig = px.pie(
                    pie_data,
                    names="Category",
                    values="Amount",
                    title="Total Payments Allocation: Expenses vs. Remaining Balance",
                    color="Category",
                    color_discrete_map=color_map
                )
                pie_fig.update_layout(margin=dict(t=70, b=40, l=40, r=0))
            

                #Display the charts side by side
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(fig, use_container_width=True )
                with col2:
                    st.plotly_chart(pie_fig, use_container_width=True)



main()