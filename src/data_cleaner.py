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
        print("В объединенной таблице пропусков нет")
        return df
    else:
        print(f"В объединенной таблице пропусков: {total_missing}")

        rows_before = len(df)
        df_clean = df.dropna()
        rows_after = len(df_clean)
        rows_lost = rows_before - rows_after

        print(f"Удалено строк с пропусками: {rows_lost} из {rows_before}")
        print(f"Потеряно данных: {rows_lost / rows_before * 100:.2f}%")
        print(f"Осталось строк: {rows_after}")
        return df_clean

def check_data_types(df):
    """
    Проверяет типы данных в ключевых столбцах.
    Выводит сообщения об ошибках, если тип не соответствует ожидаемому.
    Возвращает количество столбцов с некорректным типом.
    """
    errors = 0

    # Целочисленные столбцы
    int_columns = ['order_id', 'user_id', 'item_id', 'quantity']
    for col in int_columns:
        if df[col].dtype != np.int64:
            print(f"Ошибка: {col} должен быть int64")
            errors += 1

    # Вещественные столбцы
    float_columns = ['price_per_unit', 'base_price']
    for col in float_columns:
        if df[col].dtype != np.float64:
            print(f"Ошибка: {col} должен быть float64")
            errors += 1

    # Столбцы с датами
    datetime_columns = ['order_date', 'registration_date']
    for col in datetime_columns:
        if df[col].dtype != 'datetime64[us]':
            print(f"Ошибка: {col} должен быть datetime64[us]")
            errors += 1

    if errors == 0:
        print("Типы данных в столбцах корректны")
    else:
        print(f"Есть столбцы с некорректным типом данных: {errors} шт")

    return errors