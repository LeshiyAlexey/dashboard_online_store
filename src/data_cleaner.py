import numpy as np
import pandas as pd

def handle_missing_values(df):
    """
    Обрабатывает пропуски в DataFrame:
    - выводит статистику по пропускам
    - удаляет строки с пропусками
    Возвращает очищенный DataFrame.
    """
    total_missing = df.isnull().sum().sum()
    if total_missing == 0:
        print(f"")
        print("В объединенной таблице пропусков нет")
        return df
    else:
        print(f"")
        print(f"В объединенной таблице пропусков: {total_missing}")

        rows_before = len(df)
        df_clean = df.dropna()
        rows_after = len(df_clean)
        rows_lost = rows_before - rows_after

        print(f"Удалено строк с пропусками: {rows_lost} из {rows_before}")
        print(f"Потеряно данных: {rows_lost / rows_before * 100:.2f}%")
        print(f"Осталось строк: {rows_after}")
        return df_clean

def check_and_fix_data_types(df):
    """
    Проверяет и исправляет типы данных в датафрейме.

    Порядок действий:
    1. Проверяет текущие типы
    2. Приводит к нужным типам (int, float, datetime)
    3. Выводит отчёт об исправлениях
    
    Returns: DataFrame с исправленными типами
    """
    df = df.copy()  # работаем с копией, чтобы не изменять оригинал
    errors = 0

    # Целочисленные столбцы
    int_columns = ['order_id', 'user_id', 'item_id', 'quantity']
    for col in int_columns:
        if df[col].dtype != np.int64:
            df[col] = df[col].astype(np.int64)
            errors += 1

    # Вещественные столбцы
    float_columns = ['price_per_unit', 'base_price']
    for col in float_columns:
        if df[col].dtype != np.float64:
            df[col] = df[col].astype(np.int64)
            errors += 1

    # Столбцы с датами
    datetime_columns = ['order_date', 'registration_date']
    for col in datetime_columns:
        if df[col].dtype != 'datetime64[us]':
            df[col] = pd.to_datetime(df[col])
            errors += 1

    if errors == 0:
        print(f"")
        print("Все типы данных корректны, исправления не требуются.")
    else:
        print(f"")
        print(f"Найдено и исправленно столбцов с некорректным типом: {errors}")

    return df
