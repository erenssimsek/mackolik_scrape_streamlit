import requests
import pandas as pd
import streamlit as st
from datetime import date, timedelta
import io

st.set_page_config(page_title="Maç Veri Çekici", layout="wide")

st.markdown("""
<style>

.stApp {
    background-color: #f6f9f7;
}

.main-title {
    font-size: 42px;
    font-weight: 800;
    color: #0f5132;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 17px;
    color: #6c757d;
    margin-bottom: 25px;
}

div.stButton > button {
    background-color: #198754;
    color: white;
    border-radius: 10px;
    font-weight: 600;
    border: none;
    height: 42px;
}

div.stButton > button:hover {
    background-color: #157347;
    color: white;
}

div.stDownloadButton > button {
    background-color: #20c997;
    color: white;
    border-radius: 10px;
    font-weight: 600;
}

div.stDownloadButton > button:hover {
    background-color: #1aa179;
    color: white;
}

[data-testid="stDataFrame"] {
    border-radius: 12px;
    border: 1px solid #d1e7dd;
}

div.stAlert-success {
    background-color: #d1e7dd;
    color: #0f5132;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">Geçmiş Maç Verisi ve Oran Çekici</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Tarih aralığı seç, maç verilerini çek, tabloyu görüntüle ve CSV / Excel olarak indir.</div>',
    unsafe_allow_html=True
)

def is_valid(x):
    try:
        return float(x) > 0
    except:
        return False

yesterday = date.today() - timedelta(days=1)

with st.container():
    col1, col2 = st.columns([2, 1])

    with col1:
        date_range = st.date_input(
            "Tarih aralığı seç",
            value=(yesterday, yesterday),
            max_value=yesterday
        )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range

    with col2:
        st.write("")
        st.write("")
        fetch_button = st.button("📥 Maçları Getir", use_container_width=True)

if fetch_button:
    rows = []

    with st.spinner("Maç verileri çekiliyor..."):
        current_date = start_date

        while current_date <= end_date:
            api_date = current_date.strftime("%d/%m/%Y")
            url = f"https://vd.mackolik.com/livedata?date={api_date}"

            res = requests.get(url)
            data = res.json()

            matches = data["m"]

            for m in matches:
                ms1 = m[18]
                msx = m[19]
                ms2 = m[20]

                valid_odds = sum(is_valid(x) for x in [ms1, msx, ms2])

                if valid_odds < 2:
                    continue

                rows.append({
                    "date": m[35],
                    "time": m[16],
                    "league_short": m[36][9],
                    "home_team": m[2],
                    "away_team": m[4],
                    "half_time": (m[31] + "-" + m[32]),
                    "full_time": (m[29] + "-" + m[30]),
                    "ms1": ms1,
                    "msx": msx,
                    "ms2": ms2,
                    "under_25": m[21],
                    "over_25": m[22],
                })

            current_date += timedelta(days=1)

    df = pd.DataFrame(rows)

    st.success(f"{len(df)} maç bulundu.")

    st.subheader("📊 Maç Listesi")
    st.dataframe(df, use_container_width=True, height=520)

    csv = df.to_csv(index=False, encoding="utf-8-sig")

    excel_buffer = io.BytesIO()

    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Maclar")

    excel_data = excel_buffer.getvalue()

    col_csv, col_excel = st.columns(2)

    with col_csv:
        st.download_button(
            label="⬇️ CSV indir",
            data=csv,
            file_name=f"maclar_{start_date}_to_{end_date}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col_excel:
        st.download_button(
            label="⬇️ Excel indir",
            data=excel_data,
            file_name=f"maclar_{start_date}_to_{end_date}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )