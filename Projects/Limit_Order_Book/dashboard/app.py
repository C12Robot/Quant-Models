import os
import mysql.connector
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def query(sql, params=None):
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"), user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"), database=os.getenv("DB_NAME"))
    df = pd.read_sql(sql, conn, params=params)
    conn.close()
    return df

st.title("Limit Order Book Dashboard")

tab1, tab2, tab3, tab4 = st.tabs(["Orders", "Fills", "Analytics", "Manage"])

with tab1:
    st.dataframe(query("SELECT * FROM orders ORDER BY order_id"))

with tab2:
    st.dataframe(query("SELECT * FROM fills ORDER BY fill_id"))

with tab3:
    st.subheader("Volume per price level")
    vol = query("SELECT price_ticks, SUM(quantity) AS volume FROM fills GROUP BY price_ticks")
    st.bar_chart(vol.set_index("price_ticks"))
    st.subheader("Orders by status")
    stat = query("SELECT status, COUNT(*) AS n FROM orders GROUP BY status")
    st.bar_chart(stat.set_index("status"))

def run(sql, params=None, proc=None):
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"), user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"), database=os.getenv("DB_NAME"))
    cur = conn.cursor()
    try:
        if proc:
            cur.callproc(proc, params)
        else:
            cur.execute(sql, params)
        conn.commit()
        return None
    except mysql.connector.Error as e:
        conn.rollback()
        return e.msg
    finally:
        conn.close()

with tab4:
    st.subheader("Place order")
    with st.form("place"):
        oid = st.number_input("Order ID (below 900000)", min_value=1, max_value=899999, value=20)
        trader = st.number_input("Trader ID", min_value=1, value=1)
        inst = st.number_input("Instrument ID", min_value=1, value=1)
        side = st.selectbox("Side", ["BUY", "SELL"])
        otype = st.selectbox("Type", ["LIMIT", "MARKET"])
        price = st.number_input("Price ticks (LIMIT only)", min_value=0, value=58000)
        qty = st.number_input("Quantity", min_value=1, value=1)
        if st.form_submit_button("Place"):
            err = run("INSERT INTO orders VALUES (%s,%s,%s,%s,%s,%s,%s,'NEW',%s)",
                      (oid, trader, inst, side, otype,
                       price if otype == "LIMIT" else None, qty, 999))
            if err:
                st.error(err)
            else:
                st.success("Order placed")


    st.subheader("Cancel order")
    cid = st.number_input("Order ID to cancel", min_value=1, value=3)
    if st.button("Cancel"):
        err = run(None, (cid,), proc="cancel_order")
        if err:
            st.error(err)
        else:
            st.success("Cancelled")