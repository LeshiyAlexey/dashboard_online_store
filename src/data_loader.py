import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / 'data'

def load_items():
    """
    Загружает данные по товарам
    """
    filepath = DATA_DIR / 'items.csv'
    df = pd.read_csv(filepath)
    return df

def load_orders():
    """
    Загружает данные по заказам
    """
    filepath = DATA_DIR / 'orders.csv'
    df = pd.read_csv(filepath)
    df['order_date'] = pd.to_datetime(df['order_date'])
    return df

def load_users():
    """
    Загружает данные по клиентам
    """
    filepath = DATA_DIR / 'users.csv'
    df = pd.read_csv(filepath)
    df['registration_date'] = pd.to_datetime(df['registration_date'])
    return df

def load_all_data():
    """
    Загружает все данные проекта
    """
    items_data = load_items()
    orders_data = load_orders()
    users_data = load_users()
    return items_data, orders_data, users_data