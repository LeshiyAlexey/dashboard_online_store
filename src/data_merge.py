import pandas as pd

def merge_all_data(items_data, orders_data, users_data):
    """
    Объединяет данные о товарах, заказах и клиентах
        
    Returns:
        pd.DataFrame: объединенные данные
    """
    data_merged = orders_data.merge(users_data, on='user_id', how='left')
    merged_final = data_merged.merge(items_data, on='item_id', how='left')
    print(f"")
    print(f"Данные обьединены")
    print(f"Всего записей в обьединеной таблице: {len(merged_final)}")
    return merged_final
