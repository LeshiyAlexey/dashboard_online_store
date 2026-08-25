import pandas as pd
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / 'data'

@st.cache_data
def load_items():
    """
    Загружает данные по товарам из CSV-файла.
    """
    filepath = DATA_DIR / 'items.csv'
    df = pd.read_csv(filepath)
    print(f"items.csv загружен: {df.shape[0]} строк, {df.shape[1]} столбцов")
    return df

@st.cache_data
def load_orders():
    """
    Загружает данные по заказам из CSV-файла.
    """
    filepath = DATA_DIR / 'orders.csv'
    df = pd.read_csv(filepath)
    print(f"orders.csv загружен: {df.shape[0]} строк, {df.shape[1]} столбцов")
    return df

@st.cache_data
def load_users():
    """
    Загружает данные по клиентам из CSV-файла.
    """
    filepath = DATA_DIR / 'users.csv'
    df = pd.read_csv(filepath)
    print(f"users.csv загружен: {df.shape[0]} строк, {df.shape[1]} столбцов")
    return df

def load_all_data():
    """
    Загружает все данные проекта.
    Returns: tuple (items_df, orders_df, users_df)
    """
    items_data = load_items()
    orders_data = load_orders()
    users_data = load_users()

    return items_data, orders_data, users_data
