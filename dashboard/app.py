import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

@st.cache_data
def load_data():
    df = pd.read_csv("final_data.csv")
    
    df["order_delivered_customer_date"] = pd.to_datetime(df["order_delivered_customer_date"])
    df["order_estimated_delivery_date"] = pd.to_datetime(df["order_estimated_delivery_date"])
    
    return df

df = load_data()

min_date = df["order_delivered_customer_date"].min().date()
max_date = df["order_delivered_customer_date"].max().date()

with st.sidebar:

    start_date, end_date = st.date_input(
        label="📅 Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

filtered_df = df[
    (df["order_delivered_customer_date"].dt.date >= start_date) &
    (df["order_delivered_customer_date"].dt.date <= end_date)
]

st.header('E-Commerce Dashboard :sparkles:')

st.subheader("⭐ Analisis Rating Produk")

rating_per_category = (
    filtered_df.groupby("product_category_name_english")["review_score"]
    .mean()
    .reset_index()
    .sort_values(by="review_score", ascending=False)
)

option = st.radio("Pilih kategori:", ["Terbaik", "Terburuk"])

if option == "Terbaik":
    selected_data = rating_per_category.head(10)
    title = f"⭐ Top 10 Kategori Produk (Rating Terbaik) | {start_date} - {end_date}"
    color = "Blues_r"
else:
    selected_data = rating_per_category.tail(10)
    title = f"🔻 Top 10 Kategori Produk (Rating Terburuk) | {start_date} - {end_date}"
    color = "Reds_r"

fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(x="review_score", y="product_category_name_english", data=selected_data, palette=color)
ax.set_title(title)
ax.set_xlabel("Rata-rata Rating")
ax.set_ylabel("Kategori Produk")

st.pyplot(fig)

st.subheader("📦 Analisis Keterlambatan Pengiriman")

filtered_df["delivery_delay_days"] = (
    filtered_df["order_delivered_customer_date"] - filtered_df["order_estimated_delivery_date"]
).dt.days

bins = [-999, 0, 3, 7, 999]
labels = ["Tepat Waktu", "Terlambat 1-3 hari", "Terlambat 4-7 hari", "Terlambat >7 hari"]
filtered_df["delivery_category"] = pd.cut(filtered_df["delivery_delay_days"], bins=bins, labels=labels)

delay_counts = filtered_df.groupby(["product_category_name_english", "delivery_category"]).size().unstack()

num_categories = st.slider("Pilih jumlah kategori:", min_value=5, max_value=20, value=10)
delay_counts = delay_counts.head(num_categories)

fig, ax = plt.subplots(figsize=(10, 6))
delay_counts.plot(kind="bar", stacked=True, colormap="coolwarm", ax=ax)
ax.set_xlabel("Kategori Produk")
ax.set_ylabel("Jumlah Keterlambatan")
ax.set_title(f"🚚 Pola Keterlambatan Pengiriman | {start_date} - {end_date}")
plt.xticks(rotation=45, ha="right")

st.pyplot(fig)
