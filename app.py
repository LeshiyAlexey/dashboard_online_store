# === 0. ИМПОРТ БИБЛИОТЕК И ФУНКЦИЙ ===
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
from pathlib import Path
from src.data_loader import load_all_data
from src.data_merge import merge_all_data
from src.data_cleaner import handle_missing_values, check_and_fix_data_types

project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# === 1. ЗАГРУЗКА ДАННЫХ ===
items_data, orders_data, users_data = load_all_data()

# === 2. ОБЬЕДИНЕНИЕ ДАННЫХ ===
df_merged = merge_all_data(items_data, orders_data, users_data)

# === 3. ОЧИСТКА ДАННЫХ ===
df_merged = handle_missing_values(df_merged)
df_clean = check_and_fix_data_types(df_merged)

# === 4. СОЗДАНИЕ ДАШБОРДА ===
st.set_page_config(layout="wide")
st.title("Дашборд продаж")

# Подготовка опций для фильтров
min_date = df_clean['order_date'].min().date()
max_date = df_clean['order_date'].max().date()
segment_options = list(df_clean['user_segment'].unique())
category_options = list(df_clean['category'].unique())

with st.sidebar:
    st.header("Фильтры")
    
    # Фильтр по диапазону дат
    st.subheader("Диапазон дат")
    date_range = st.date_input(
        "Выберите даты",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Фильтр по сегментам клиентов
    st.subheader("Сегменты клиентов")
    selected_segments = st.multiselect(
        "Выберите сегменты",
        options=segment_options,
        default=segment_options
    )
    
    # Фильтр по категориям товаров
    st.subheader("Категории товаров")
    selected_categories = st.multiselect(
        "Выберите категории",
        options=category_options,
        default=category_options
    )

# === ПРИМЕНЕНИЕ ФИЛЬТРОВ ===
filtered_df = df_clean.copy()

# 1. Фильтр по диапазону дат
if len(date_range) == 2:
    start_date, end_date = date_range
    start_datetime = pd.Timestamp(start_date)
    end_datetime = pd.Timestamp(end_date) + pd.Timedelta(days=1)
    
    filtered_df = filtered_df[
        (filtered_df['order_date'] >= start_datetime) & 
        (filtered_df['order_date'] < end_datetime)
    ]

# 2. Фильтр по сегментам клиентов
filtered_df = filtered_df[filtered_df['user_segment'].isin(selected_segments)]

# 3. Фильтр по категориям товаров
filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]

# === 5. ВКЛАДКИ ===
tab_raw, tab_kpi, tab_sum = st.tabs(["Сырые данные", "Отчет", "Аналитические выводы"])

with tab_raw:
    st.subheader("Таблица заказов")
    st.dataframe(filtered_df)

# === 6. РАСЧЁТ МЕТРИК И ГРАФИКОВ ===
# Расчет метрик
total_orders = len(filtered_df)
total_revenue = (filtered_df['price_per_unit'] * filtered_df['quantity']).sum()
unique_users = filtered_df['user_id'].nunique()
avg_check = total_revenue / total_orders if total_orders > 0 else 0

# Расчет топ-10 товаров по выручке
filtered_df['revenue'] = filtered_df['quantity'] * filtered_df['price_per_unit']
product_revenue = filtered_df.groupby('item_name')['revenue'].sum().reset_index()
product_revenue.columns = ['Товар', 'Выручка']
top10 = product_revenue.sort_values('Выручка', ascending=False).head(10)

# Построение горизонтальной столбчатой диаграммы для топ-10 (Plotly)
fig_bar_chart = px.bar(
    top10,
    x='Выручка',
    y='Товар',
    orientation='h',
    title='Топ-10 товаров по выручке',
    labels={'Выручка': 'Выручка, ₽', 'Товар': 'Товар'},
    color='Выручка',
    color_continuous_scale='Blues',
    text='Выручка'
)
fig_bar_chart.update_layout(
    yaxis={'categoryorder': 'total ascending'},
    showlegend=False,
    height=500
)
fig_bar_chart.update_traces(
    texttemplate='%{text:.2f}',
    textposition='outside'
)

# Расчет выручки по категориям товаров
category_revenue = filtered_df.groupby('category')['revenue'].sum().reset_index()
category_revenue = category_revenue.sort_values('revenue', ascending=False)

# Построение круговой диаграммы (Plotly)
fig_pie_chart = px.pie(
    category_revenue,
    values='revenue',
    names='category',
    title='Выручка по категориям товаров',
    hole=0.4,
    color_discrete_sequence=px.colors.qualitative.Set3
)
fig_pie_chart.update_traces(
    textposition='inside',
    textinfo='percent+label',
    hovertemplate='<b>%{label}</b><br>Выручка: %{value:.2f} ₽<br>Доля: %{percent}'
)
fig_pie_chart.update_layout(
    height=500,
    showlegend=True
)

# Данные, сгруппированные по дням недели
df_orders = filtered_df.copy()
df_orders['weekday'] = df_orders['order_date'].dt.dayofweek
orders_by_weekday = df_orders.groupby('weekday').size().reset_index(name='order_count')
weekday_names = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
orders_by_weekday['weekday_name'] = orders_by_weekday['weekday'].apply(lambda x: weekday_names[x])
orders_by_weekday = orders_by_weekday.sort_values('weekday')

# Построение линейного графика (Plotly)
fig_line = px.line(
    orders_by_weekday,
    x='weekday_name',
    y='order_count',
    title='Зависимость количества заказов от дня недели',
    labels={'weekday_name': 'День недели', 'order_count': 'Количество заказов'},
    markers=True,
    line_shape='linear'
)
fig_line.update_traces(
    line=dict(color='green', width=3),
    marker=dict(size=10, color='darkgreen'),
    hovertemplate='<b>%{x}</b><br>Заказов: %{y}'
)
fig_line.update_layout(
    height=500,
    xaxis_title='День недели',
    yaxis_title='Количество заказов',
    hovermode='x unified'
)

# === 7. ВКЛАДКА "ОТЧЁТ" ===
with tab_kpi:
    st.subheader("Ключевые показатели")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Общее количество заказов", total_orders)
    with col2:
        st.metric("Общая выручка", f"{total_revenue:,.2f} ₽")
    with col3:
        st.metric("Уникальные пользователи", unique_users)
    with col4:
        st.metric("Средний чек", f"{avg_check:,.2f} ₽")

    st.subheader("Топ-10 товаров по выручке")
    st.plotly_chart(fig_bar_chart, use_container_width=True)
    
    st.subheader("Выручка по категориям товаров")
    st.plotly_chart(fig_pie_chart, use_container_width=True)
    
    st.subheader("Зависимость количества заказов от дня недели")
    st.plotly_chart(fig_line, use_container_width=True)

# === 8. ВКЛАДКА "АНАЛИТИЧЕСКИЕ ВЫВОДЫ" ===
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
