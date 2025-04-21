import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

#Set page configuration
st.set_page_config(page_title="Simple Finance App", layout="wide")

#File upload

def load_transactions(file):
    pass
def main():
    st.title("Simple Finance Dashboard")
    uploaded_file = st.file_uploader("Upload your transaction CSV file", type=["csv"])

    if uploaded_file is not None:
        df = load_transactions(uploaded_file)

main()