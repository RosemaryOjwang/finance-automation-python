import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import plotly.graph_objects as go

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
            
            #Expenses Tab
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

            #Payments Tab
            with tab2:
                st.subheader("Payments Summary")
                total_payments = credits_df["Amount"].sum()
                st.metric("Total Payments", f"{total_payments:,.2f} KES")
                st.write(credits_df)


            #Visualizations Tab
            with tab3:
                st.subheader("Financial Visualizations")
                category_totals = st.session_state.debits_df.groupby("Category")["Amount"].sum().reset_index()
                category_totals = category_totals.sort_values("Amount", ascending=False)

                #Calculate totals for bar chart
                total_expenses = category_totals["Amount"].sum()
                total_payments = credits_df["Amount"].sum()
                remaining_balance = total_payments - total_expenses

                pie_data = pd.DataFrame({
                    "Category": ["Total Expenses", "Remaining Balance"],
                    "Amount": [total_expenses, remaining_balance]
                        })

                #Row 1: summary + Pie
                row1_col1, row1_col2 = st.columns(2)
                with row1_col1:
                    st.subheader('Expense Summary')
                    
                    #Display expense summary
                    st.dataframe(
                        category_totals,
                        column_config={
                            "Amount": st.column_config.NumberColumn("Amount", format="%.2f KES")
                        },
                        use_container_width=True,
                        hide_index=True
                    )


                with row1_col2:
                    
                    
                    #Create Gauge Chart for spending vs payments
                   
                    gauge_fig = go.Figure(go.Indicator(
                        mode="gauge+number+delta",
                        value=total_expenses,
                        delta={'reference': total_payments, 'increasing': {'color': '#000080'}, 'decreasing': {'color': '#FFDB58'}},
                        title={'text': "Spending Progress", 'font': {'size': 24}},
                        gauge={
                            'axis': {'range': [0, total_payments], 'tickwidth': 1, 'tickcolor': "#000080"},
                            'bar': {'color': "#FFDB58"},
                            'bgcolor': "#FFFFFF",
                            'borderwidth': 2,
                            'bordercolor': "#000080",
                            'steps': [
                                {'range': [0, total_payments*0.5], 'color': '#FFF8DC'},
                                {'range': [total_payments*0.5, total_payments], 'color': '#F5DEB3'},
                            ],
                            'threshold': {
                                'line': {'color': "#FFDB58", 'width': 4},
                                'thickness': 0.75,
                                'value': total_expenses
                            }
                        }
                    ))
                      
                    gauge_fig.update_layout(
                        height=380,
                        margin=dict(t=50, b=20, l=20, r=20),
                        paper_bgcolor="#FFFFFF"
                        )


                    #Display gauge chart
                    st.plotly_chart(gauge_fig, use_container_width=True)
                
                row2_col1, row2_col2 = st.columns(2)
                with row2_col1:
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
                        textfont_size=11,
                        marker_color='#FFDB58'
                    )

                    fig.update_layout(
                        uniformtext_minsize=8,
                        #uniformtext_mode='hide',
                        xaxis_title='Category',
                        yaxis_title='Amount (KES)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        height=380,
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with row2_col2:
                    # Prepare daily expenses data
                    daily_expenses = st.session_state.debits_df.groupby("Date")["Amount"].sum().reset_index()

                    #Create the line chart
                    line_fig = px.line(
                        daily_expenses,
                        x="Date",
                        y="Amount",
                        title="Daily Expenses Over Time",
                        markers=True,                    
                        line_shape="linear"
                    )

                    line_fig.update_traces(
                        line_color="#FFDB58"
                        )
                    line_fig.update_layout(
                        height=380,
                        xaxis_title="Date",
                        yaxis_title="Amount (KES)",
                        plot_bgcolor='rgba(0,0,0,0)'
                        #marging=dict(t=50, b=40, l=40, r=40)
                    )

                    #Display the line chart
                    st.plotly_chart(line_fig, use_container_width=True)

main()