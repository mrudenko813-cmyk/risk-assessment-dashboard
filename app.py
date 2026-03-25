import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Система оцінки ризику підприємств",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
.t1 {
    font-size: 34px;
    font-weight: 700;
    margin-bottom: 4px;
}
.t2 {
    font-size: 17px;
    color: #475569;
    margin-bottom: 18px;
}
.kartka {
    background-color: #f8fafc;
    padding: 16px;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.kartka h3 {
    margin: 0;
    font-size: 16px;
}
.kartka p {
    margin: 8px 0 0 0;
    font-size: 28px;
    font-weight: bold;
}
.high-risk {
    color: #b91c1c;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="t1">📊 Система оцінки ризику підприємств</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="t2">Аналіз фінансових, податкових і публічних ознак підприємств з обчисленням інтегрального індексу ризику</div>',
    unsafe_allow_html=True
)

# ------------------ Завантаження або тестові дані ------------------
st.sidebar.header("Налаштування")

uploaded_file = st.sidebar.file_uploader("Завантажте CSV-файл", type=["csv"])

use_demo = st.sidebar.checkbox("Використати тестові дані", value=True if uploaded_file is None else False)

def create_demo_data():
    np.random.seed(42)
    companies = [
        "ТОВ Альфа", "ТОВ Бета", "ПП Вектор", "ТОВ Горизонт", "ТОВ Дельта",
        "ПП Еталон", "ТОВ Жасмин", "ТОВ Зеніт", "ПП Імпульс", "ТОВ Кардинал"
    ]

    data = {
        "Компанія": companies,
        "Фінансовий_ризик": np.random.randint(20, 95, size=10),
        "Податковий_ризик": np.random.randint(10, 100, size=10),
        "Публічний_ризик": np.random.randint(5, 90, size=10)
    }
    return pd.DataFrame(data)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    if use_demo:
        df = create_demo_data()
    else:
        st.warning("Завантажте CSV-файл або увімкніть тестові дані.")
        st.stop()

# ------------------ Перевірка структури ------------------
required_columns = ["Компанія", "Фінансовий_ризик", "Податковий_ризик", "Публічний_ризик"]

missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    st.error(f"У файлі відсутні потрібні стовпці: {', '.join(missing_columns)}")
    st.stop()

# ------------------ Ваги ризику ------------------
st.sidebar.subheader("Ваги для інтегрального індексу")

w_fin = st.sidebar.slider("Вага фінансового ризику", 0.0, 1.0, 0.4, 0.05)
w_tax = st.sidebar.slider("Вага податкового ризику", 0.0, 1.0, 0.35, 0.05)
w_pub = st.sidebar.slider("Вага публічного ризику", 0.0, 1.0, 0.25, 0.05)

weight_sum = w_fin + w_tax + w_pub
if weight_sum == 0:
    st.error("Сума ваг не може дорівнювати нулю.")
    st.stop()

# Нормалізація ваг
w_fin /= weight_sum
w_tax /= weight_sum
w_pub /= weight_sum

# ------------------ Розрахунок інтегрального індексу ------------------
df["Інтегральний_індекс_ризику"] = (
    df["Фінансовий_ризик"] * w_fin +
    df["Податковий_ризик"] * w_tax +
    df["Публічний_ризик"] * w_pub
).round(2)

def risk_level(value):
    if value < 40:
        return "Низький"
    elif value < 70:
        return "Середній"
    return "Високий"

df["Рівень_ризику"] = df["Інтегральний_індекс_ризику"].apply(risk_level)

# ------------------ Фільтри ------------------
selected_level = st.sidebar.selectbox(
    "Фільтр за рівнем ризику",
    ["Усі", "Низький", "Середній", "Високий"]
)

filtered = df.copy()
if selected_level != "Усі":
    filtered = filtered[filtered["Рівень_ризику"] == selected_level]

# ------------------ Показники ------------------
total_companies = len(filtered)
avg_risk = round(filtered["Інтегральний_індекс_ризику"].mean(), 2) if not filtered.empty else 0
high_risk_count = (filtered["Рівень_ризику"] == "Високий").sum() if not filtered.empty else 0
top_company = (
    filtered.sort_values("Інтегральний_індекс_ризику", ascending=False).iloc[0]["Компанія"]
    if not filtered.empty else "—"
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
        <div class="kartka">
            <h3>Кількість компаній</h3>
            <p>{total_companies}</p>
        </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
        <div class="kartka">
            <h3>Середній індекс ризику</h3>
            <p>{avg_risk}</p>
        </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
        <div class="kartka">
            <h3>Компаній з високим ризиком</h3>
            <p>{high_risk_count}</p>
        </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div class="kartka">
            <h3>Найризикованіша компанія</h3>
            <p style="font-size:20px;">{top_company}</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ------------------ Gauge chart ------------------
st.subheader("Шкала інтегрального індексу ризику")

if not filtered.empty:
    avg_value = filtered["Інтегральний_індекс_ризику"].mean()

    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_value,
        title={"text": "Середній інтегральний індекс ризику"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"thickness": 0.3},
            "steps": [
                {"range": [0, 40], "color": "#bbf7d0"},
                {"range": [40, 70], "color": "#fde68a"},
                {"range": [70, 100], "color": "#fecaca"}
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.8,
                "value": avg_value
            }
        }
    ))
    st.plotly_chart(gauge, use_container_width=True)
else:
    st.warning("Немає даних для побудови шкали.")

st.markdown("---")

# ------------------ Таблиця ------------------
st.subheader("Таблиця оцінки ризику підприємств")

def highlight_high_risk(row):
    if row["Рівень_ризику"] == "Високий":
        return ["background-color: #fee2e2"] * len(row)
    return [""] * len(row)

if not filtered.empty:
    styled_df = filtered.sort_values("Інтегральний_індекс_ризику", ascending=False).style.apply(highlight_high_risk, axis=1)
    st.dataframe(
        filtered.sort_values("Інтегральний_індекс_ризику", ascending=False),
        use_container_width=True
    )
else:
    st.warning("Немає даних для відображення.")

st.markdown("---")

# ------------------ Діаграми ------------------
left, right = st.columns(2)

with left:
    st.subheader("Індекс ризику за компаніями")
    if not filtered.empty:
        plot_df = filtered.sort_values("Інтегральний_індекс_ризику", ascending=False)

        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(plot_df["Компанія"], plot_df["Інтегральний_індекс_ризику"])

        for i, level in enumerate(plot_df["Рівень_ризику"]):
            if level == "Високий":
                bars[i].set_hatch("//")

        ax.set_title("Порівняння компаній за індексом ризику")
        ax.set_xlabel("Компанія")
        ax.set_ylabel("Індекс ризику")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)
    else:
        st.warning("Немає даних для побудови діаграми.")

with right:
    st.subheader("Розподіл компаній за рівнем ризику")
    if not filtered.empty:
        level_counts = filtered["Рівень_ризику"].value_counts()

        fig2, ax2 = plt.subplots(figsize=(7, 5))
        ax2.pie(level_counts.values, labels=level_counts.index, autopct="%1.1f%%", startangle=90)
        ax2.set_title("Частка компаній за рівнем ризику")
        st.pyplot(fig2)
    else:
        st.warning("Немає даних для побудови діаграми.")

st.markdown("---")

# ------------------ Високий ризик ------------------
st.subheader("Компанії з високим ризиком")

high_risk_df = filtered[filtered["Рівень_ризику"] == "Високий"]

if not high_risk_df.empty:
    for _, row in high_risk_df.sort_values("Інтегральний_індекс_ризику", ascending=False).iterrows():
        st.error(
            f"{row['Компанія']} — інтегральний індекс ризику: {row['Інтегральний_індекс_ризику']}"
        )
else:
    st.success("У вибірці немає компаній з високим ризиком.")

st.markdown("---")
st.caption("Навчальний вебзастосунок для оцінки ризику підприємств")
