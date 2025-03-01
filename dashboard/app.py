import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

@st.cache_data
def load_data():
    df1 = pd.read_csv("dashboard/final_df_case1.csv")
    df2 = pd.read_csv("dashboard/final_df_case2.csv", parse_dates=["order_delivered_customer_date", "order_estimated_delivery_date"])

    return df1, df2

df_case1, df_case2 = load_data()

min_date = df_case2["order_delivered_customer_date"].min().date()
max_date = df_case2["order_delivered_customer_date"].max().date()

with st.sidebar:

    start_date, end_date = st.date_input(
        label="📅 Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

filtered_df_case2 = df_case2[
    (df_case2["order_delivered_customer_date"].dt.date >= start_date) &
    (df_case2["order_delivered_customer_date"].dt.date <= end_date)
]

if filtered_df_case2.empty:
    st.warning("Tidak ada data dalam rentang tanggal yang dipilih.")
    st.stop()

st.header('E-Commerce Dashboard :sparkles:')

st.subheader("📊 Analisis Jumlah Pesanan")

order_count_per_category = df_case1.groupby("product_category_name_english")["order_id"].count().reset_index()
order_count_per_category.columns = ["product_category_name_english", "total_orders"]
order_count_per_category = order_count_per_category.sort_values(by="total_orders", ascending=False)

fig, ax = plt.subplots(figsize=(10, 5))
max_value = order_count_per_category["total_orders"].head(10).max()
colors = ["#D3D3D3" if val < max_value else "#90CAF9" for val in order_count_per_category["total_orders"].head(10)]

sns.barplot(
    x=order_count_per_category["total_orders"].head(10),
    y=order_count_per_category["product_category_name_english"].head(10),
    palette=colors
)
ax.set_xlabel("Jumlah Pesanan")
ax.set_ylabel(None)
ax.set_title("Top 10 Kategori Produk dengan Jumlah Pesanan Tertinggi")

st.pyplot(fig)

st.subheader("⭐ Analisis Rating Produk")

rating_per_category = df_case1.groupby("product_category_name_english").agg(
    avg_rating=("review_score", "mean")
).reset_index()
rating_per_category = rating_per_category.sort_values(by="avg_rating", ascending=False)

option = st.radio("Pilih kategori:", ["Terbaik", "Terburuk"])

if option == "Terbaik":
    selected_data = rating_per_category.head(10)
    title = f"Top 10 Kategori Produk (Rating Terbaik) | {start_date} - {end_date}"
    color = "Blues_r"
else:
    selected_data = rating_per_category.tail(10)
    title = f"Top 10 Kategori Produk (Rating Terburuk) | {start_date} - {end_date}"
    color = "Reds_r"

fig, ax = plt.subplots(figsize=(8, 5))
max_value = selected_data["avg_rating"].max()
colors = ["#D3D3D3" if val < max_value else "#90CAF9" for val in selected_data["avg_rating"]]
sns.barplot(x="avg_rating", y="product_category_name_english", data=selected_data, palette=colors)
ax.set_title(title)
ax.set_xlabel("Rata-rata Rating")
ax.set_ylabel(None)

st.pyplot(fig)

st.subheader("📦 Analisis Keterlambatan Pengiriman")

delay_counts = filtered_df_case2.groupby(["product_category_name_english", "delivery_category"]).agg(
    total_orders=("order_id", "count")
).reset_index()

delay_counts = delay_counts.pivot(index="product_category_name_english", columns="delivery_category", values="total_orders").fillna(0)

num_categories = st.slider("Pilih jumlah kategori:", min_value=5, max_value=10, value=10)
delay_counts = delay_counts.head(num_categories)

fig, ax = plt.subplots(figsize=(12, 6))
colors = ["#99CC99","#FFD95F", "#FBA518", "#FF6B6B"]
delay_counts.plot(kind="bar", stacked=False, color=colors, ax=ax, width=0.8)
ax.set_xlabel(None)
ax.set_ylabel("Jumlah Keterlambatan")
ax.set_title(f"Pola Keterlambatan Pengiriman | {start_date} - {end_date}")
ax.legend(title="Kategori Keterlambatan")
plt.xticks(rotation=45, ha="right")

for container in ax.containers:
    ax.bar_label(container, fmt='%d', label_type='edge', fontsize=6, color='black')

st.pyplot(fig)

st.subheader("Kesimpulan")
st.markdown("""
- **Kategori dengan rating terbaik** adalah `fashion_childrens_clothes`, menunjukkan bahwa konsumen merasa puas dengan produk-produk dalam kategori ini.
- **Kategori dengan rating terburuk** adalah `furniture_mattress_and_upholstery`, kemungkinan karena masalah kualitas produk, layanan, atau faktor lain yang memengaruhi kepuasan pelanggan.
- Sebagian besar pengiriman dalam semua kategori produk berhasil dilakukan tepat waktu. Ini ditunjukkan oleh bagian (warna) hijau yang dominan di setiap batang grafik. **Kategori dengan frekuensi keterlambatan tertinggi** adalah `bed_bath_table`, menunjukkan adanya masalah khusus dalam proses pengiriman untuk produk-produk dalam kategori ini.
""")