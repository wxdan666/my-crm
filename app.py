import streamlit as st
import pandas as pd
from database import session, Order, Worker, Material, IPFinance # Импортируем всё сразу

# Настройка страницы
st.set_page_config(page_title="ПросчетПрофи", page_icon="/Users/matvejdanilov/Desktop/WorkBot/Image/Gemini_Generated_Image_fgm2pdfgm2pdfgm2.jpeg", layout="wide")

# --- БЛОК ДИЗАЙНА (Исправлен под Dark Theme) ---
st.markdown("""
    <style>
    .stApp { background-color: #1a1a1a; }
    
    [data-testid="stSidebar"] {
        background-color: #1a1a1a;
        border-right: 1px solid #333333;
        min-width: 300px !important;
    }

    .stRadio [data-testid="stWidgetLabel"] p {
        font-size: 22px !important;
        font-weight: 700 !important;
        color: #ff4b4b !important;
        margin-bottom: 20px;
    }

    /* Кнопки меню */
    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label {
        background-color: #262626;
        border: 1px solid #444444;
        color: #ffffff !important;
        padding: 15px 20px !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
        transition: all 0.3s ease;
    }

    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label:hover {
        border-color: #ff4b4b;
        transform: translateX(5px);
    }

    /* Активная вкладка */
    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] [data-checked="true"] {
        background-color: #ff4b4b !important;
        border: none !important;
    }

    /* Скрываем стандартные кружочки */
    div[role="radiogroup"] div[data-testid="stSelectionControlActive"] { display: none !important; }

    /* Карточки метрик (Исправлено) */
    [data-testid="stMetric"] {
        background-color: #262626 !important;
        border: 1px solid #444444 !important;
        padding: 20px !important;
        border-radius: 15px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ЛОГИКА ПРИЛОЖЕНИЯ ---

st.sidebar.markdown("# ⚙️ ПросчетПрофи")
st.sidebar.markdown("---")

# ИСПРАВЛЕНО: Добавлен пункт в меню
choice = st.sidebar.radio(
    "ГЛАВНОЕ МЕНЮ",
    ["📋 Заявки", "👷 Персонал", "📦 Склад", "📊 Аналитика", "💰 Мой ИП (Личное)"],
    label_visibility="visible"
)

def color_status(val):
    colors = {'Новая': '#9e9e9e', 'В работе': '#1f77b4', 'Завершена': '#2ca02c', 'Отменен': '#d62728'}
    return f'color: {colors.get(val, "black")}; font-weight: bold'

# --- РАЗДЕЛ 1: ЗАЯВКИ ---
if choice == "📋 Заявки":
    st.header("📋 Управление заказами")
    orders = session.query(Order).all()
    if orders:
        data = []
        for o in orders:
            worker_list = ", ".join([f"{w.name}" for w in o.workers]) if o.workers else "---"
            data.append({
                "ID": o.id, "Описание": o.description, "Статус": o.status,
                "Исполнители": worker_list, "Сумма": f"{o.total_cost} ₽"
            })
        st.dataframe(pd.DataFrame(data).style.map(color_status, subset=['Статус']), use_container_width=True)
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.subheader("➕ Новая заявка")
            new_d = st.text_input("Описание поломки")
            if st.button("Создать запись"):
                if new_d:
                    session.add(Order(description=new_d))
                    session.commit()
                    st.rerun()
    with c2:
        with st.container(border=True):
            st.subheader("⚙️ Редактор задачи")
            if orders:
                o_id = st.selectbox("ID заявки", [o.id for o in orders])
                curr_o = session.query(Order).get(o_id)
                all_workers = session.query(Worker).all()
                worker_options = {f"{w.name} ({w.specialty})": w for w in all_workers}
                current_w = [f"{w.name} ({w.specialty})" for w in curr_o.workers]
                sel_workers = st.multiselect("Мастера", options=list(worker_options.keys()), default=current_w)
                col_s, col_p = st.columns(2)
                st_list = ["Новая", "В работе", "Завершена", "Отменен"]
                new_status = col_s.selectbox("Статус", st_list, index=st_list.index(curr_o.status))
                new_price = col_p.number_input("Цена", value=float(curr_o.total_cost))
                if st.button("Обновить задачу"):
                    curr_o.workers = [worker_options[name] for name in sel_workers]
                    curr_o.status = new_status
                    curr_o.total_cost = new_price
                    session.commit()
                    st.rerun()

# --- РАЗДЕЛ 2: ПЕРСОНАЛ ---
elif choice == "👷 Персонал":
    st.header("👷 База сотрудников")
    workers = session.query(Worker).all()
    if workers:
        st.dataframe(pd.DataFrame([{"ID": w.id, "ФИО": w.name, "Роль": w.specialty} for w in workers]), use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.subheader("Добавить в штат")
            n = st.text_input("Имя")
            s = st.text_input("Специальность")
            if st.button("Нанять"):
                session.add(Worker(name=n, specialty=s))
                session.commit()
                st.rerun()
    with c2:
        with st.container(border=True):
            st.subheader("Увольнение")
            if workers:
                d_id = st.selectbox("ID сотрудника", [w.id for w in workers])
                if st.button("❌ Удалить из базы"):
                    session.delete(session.query(Worker).get(d_id))
                    session.commit()
                    st.rerun()

# --- РАЗДЕЛ 3: СКЛАД ---
elif choice == "📦 Склад":
    st.header("📦 Материалы и цены")
    mats = session.query(Material).all()
    for m in mats:
        with st.expander(f"📦 {m.name} — {m.price} ₽"):
            c1, c2, c3 = st.columns(3)
            m.name = c1.text_input("Название", m.name, key=f"n{m.id}")
            m.price = c2.number_input("Цена", float(m.price), key=f"p{m.id}")
            m.stock = c3.number_input("Склад", int(m.stock), key=f"s{m.id}")
            if st.button("Сохранить изменения", key=f"b{m.id}"):
                session.commit()
                st.rerun()
    if st.button("➕ Добавить новую позицию товара"):
        session.add(Material(name="Новый материал", price=0, stock=0))
        session.commit()
        st.rerun()

# --- РАЗДЕЛ 4: АНАЛИТИКА ---
elif choice == "📊 Аналитика":
    st.header("📊 Статистика сервиса")
    orders = session.query(Order).all()
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("Выручка (завершенные)", f"{sum(o.total_cost for o in orders if o.status == 'Завершена')} ₽")
    with col_m2:
        st.metric("Всего активных заказов", len([o for o in orders if o.status in ["Новая", "В работе"]]))
    st.subheader("Распределение по статусам")
    if orders:
        st.bar_chart(pd.Series([o.status for o in orders]).value_counts())

# --- РАЗДЕЛ 5: МОЙ ИП ---
elif choice == "💰 Мой ИП (Личное)":
    st.header("💰 Личный учет ИП (15%)")
    with st.container(border=True):
        st.subheader("📝 Новая запись")
        c1, c2, c3 = st.columns(3)
        obj_name = c1.text_input("Объект")
        inc_val = c2.number_input("Доход (₽)", min_value=0.0)
        exp_val = c3.number_input("Расход (₽)", min_value=0.0)
        if st.button("📈 Внести данные"):
            if obj_name:
                session.add(IPFinance(object_name=obj_name, income=inc_val, expense=exp_val))
                session.commit()
                st.rerun()

    data_ip = session.query(IPFinance).all()
    if data_ip:
        records = []
        for r in data_ip:
            profit = r.income - r.expense
            tax = profit * 0.15 if profit > 0 else 0
            records.append({
                "Объект": r.object_name, "Доход": r.income, "Расход": r.expense,
                "Прибыль": profit, "Налог": round(tax, 2), "Чистыми": round(profit - tax, 2)
            })
        st.dataframe(pd.DataFrame(records), use_container_width=True)
        
        # Итоговые метрики
        t_inc = sum(r.income for r in data_ip)
        t_exp = sum(r.expense for r in data_ip)
        t_tax = sum(max(0, (r.income - r.expense) * 0.15) for r in data_ip)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Всего доходов", f"{t_inc} ₽")
        m2.metric("Всего расходов", f"{t_exp} ₽")
        m3.metric("Налог к уплате", f"{round(t_tax, 2)} ₽")
        
        if st.button("🗑 Очистить финансы"):
            session.query(IPFinance).delete()
            session.commit()
            st.rerun()
