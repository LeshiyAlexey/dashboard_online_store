# === 0. ИМПОРТ БИБЛИОТЕК И ФУНКЦИЙ ===
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
from pathlib import Path
from src.data_loader import load_all_data
from src.data_merge import merge_all_data
from src.data_cleaner import handle_missing_values, check_data_types

project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# === 1. ЗАГРУЗКА ДАННЫХ ===
items_data, orders_data, users_data = load_all_data()
print(f"Загружено записей о товарах: {len(items_data)}")
print(f"Загружено записей о заказах: {len(orders_data)}")
print(f"Загружено записей о клиентах: {len(users_data)}")
print(f"")

# === 2. ОБЬЕДИНЕНИЕ ДАННЫХ ===
df = merge_all_data(items_data, orders_data, users_data)

# === 3. ОЧИСТКА ДАННЫХ ===
data_merged = handle_missing_values(df)   # обработка пропусков
type_errors = check_data_types(df)        # проверка типов

# === 4. СОЗДАНИЕ ДАШБОРДА ===
st.set_page_config(layout="wide")
st.title("Дашборд продаж")

# Получение уникальных значений для дат, сегментов и категорий
date_options = ["Все даты"] + list(df['order_date'].unique())
segment_options = ["Все сегменты"] + list(df['user_segment'].unique())
category_options = ["Все категории"] + list(df['category'].unique())


with st.sidebar:
    # Дата
    selected_date = st.selectbox("Дата заказа", date_options)
    # Сегмент клиента
    selected_segment = st.selectbox("Сегмент клиента", segment_options)
    # Категория товара
    selected_category = st.selectbox("Категория товара", category_options)


# 1. Фильтр по дате
if selected_date == "Все даты":
    filtered_df = df
else:
    filtered_df = df[df['order_date'] == selected_date]

# 2. Фильтр по сегменту
if selected_segment != "Все сегменты":
    filtered_df = filtered_df[filtered_df['user_segment'] == selected_segment]

# 3. Фильтр по категории
if selected_category != "Все категории":
    filtered_df = filtered_df[filtered_df['category'] == selected_category]


tab_raw, tab_kpi, tab_sum = st.tabs(["Сырые данные", "Отчет", "Аналитические выводы"])

with tab_raw:
    st.subheader("Таблица заказов")
    st.dataframe(filtered_df)

# Расчет метрик
total_orders = len(filtered_df)                                                     # Общее количество заказов
total_revenue = (filtered_df['price_per_unit'] * filtered_df['quantity']).sum()     # Общая выручка
unique_users = filtered_df['user_id'].nunique()                                     # Количество уникальных пользователей
avg_check = total_revenue/total_orders                                              # Средний чек

# Расчет топ-10 товаров по выручке
filtered_df['revenue'] = filtered_df['quantity'] * filtered_df['price_per_unit']
product_revenue = filtered_df.groupby('item_name')['revenue'].sum().reset_index()
product_revenue.columns = ['Товар', 'Выручка']
top10 = product_revenue.sort_values('Выручка', ascending=False).head(10)

# Построение горизонтальной столбчатой диаграмму для топ-10
fig_bar_chart, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(top10['Товар'], top10['Выручка'], color='skyblue')
ax.set_xlabel('Выручка')
ax.set_title('Топ-10 товаров по выручке')
ax.invert_yaxis()  # чтобы самый продаваемый был сверху

# Расчет выручки по категортиям товаров
category_revenue = filtered_df.groupby('category')['revenue'].sum().reset_index()
category_revenue = category_revenue.sort_values('revenue', ascending=False)

# Построение круговой диаграммы: доля каждой категории в общей выручке
fig_pie_chart, ax = plt.subplots(figsize=(10, 8))
wedges, texts, autotexts = ax.pie(
    category_revenue['revenue'],
    labels=None,                # убираем подписи с диаграммы
    autopct='%1.0f%%',          # проценты можно оставить
    startangle=90,
    pctdistance=0.75            # чуть дальше от центра
)
ax.legend(wedges, category_revenue['category'], title="Категории", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
ax.set_title('Выручка по категориям товаров')
plt.tight_layout()

# Данные, сгруппированные по дням недели для анализа
df_orders = filtered_df.copy()
df_orders['weekday'] = df_orders['order_date'].dt.dayofweek
orders_by_weekday = df_orders.groupby('weekday').size().reset_index(name='order_count')
weekday_names = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
orders_by_weekday['weekday_name'] = orders_by_weekday['weekday'].apply(lambda x: weekday_names[x])
orders_by_weekday = orders_by_weekday.sort_values('weekday')

# Построение графика линейной зависимости кол-ва заказов от дней недели
fig_lin, ax = plt.subplots(figsize=(10, 5))
ax.plot(
    orders_by_weekday['weekday_name'],
    orders_by_weekday['order_count'],
    marker='o',          # маркер в виде кружочков
    linestyle='-',       # сплошная линия
    color='green',
    linewidth=2,
    markersize=8
)
ax.set_xlabel('День недели')
ax.set_ylabel('Количество заказов')
ax.set_title('Зависимость количества заказов от дня недели')
ax.grid(True, alpha=0.3)  # лёгкая сетка
plt.xticks(rotation=45)   # поворот подписей оси X
plt.tight_layout()

with tab_kpi:
    st.subheader("Ключевые показатели")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Общее количество заказов", total_orders)
    with col2:
        st.metric("Общая выручка", f"{total_revenue:.2f} ₽")  # форматирование с разделителями
    with col3:
        st.metric("Уникальные пользователи", unique_users)
    with col4:
        st.metric("Средний чек", f"{avg_check:.2f} ₽")

    st.subheader("Топ-10 товаров по выручке")
    st.pyplot(fig_bar_chart)
    st.subheader("Выручка по категориям товаров")
    st.pyplot(fig_pie_chart)
    st.subheader("Зависимость количества заказов от дня недели")
    st.pyplot(fig_lin)


with tab_sum:
    st.subheader("Аналитические выводы")
    st.markdown("""
    1. **Основная выручка приходится на категорию «Электроника»**  
   Рекомендуется расширять ассортимент в этой категории и проводить целевые маркетинговые акции.

    2. **Пик заказов наблюдается в пятницу**  
   Анализ динамики заказов по дням недели показывает рост активности к концу рабочей недели.
   Пользователи предпочитают совершать покупки перед выходными.
   Оптимальное время для запуска промоакций — четверг и пятница.

    3. **Товар «Ноутбук ASUS VivoBook» является лидером продаж**  
   Следует обеспечить его постоянное наличие на складе, а также рассмотреть перекрёстные продажи (например, сумки, мыши, подставки) для увеличения среднего чека.
    """)