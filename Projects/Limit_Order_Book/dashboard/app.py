import os
import re

import mysql.connector
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Limit Order Book", layout="wide")


def get_conn():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


def query(sql, params=None):
    conn = get_conn()
    try:
        return pd.read_sql(sql, conn, params=params)
    finally:
        conn.close()


def run(sql, params=None, proc=False):
    """Run a write. Returns (ok, message). Commits on success, rolls back on error."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        if proc:
            cur.callproc(sql, params or ())
        else:
            cur.execute(sql, params or ())
        conn.commit()
        return True, ""
    except mysql.connector.Error as e:
        conn.rollback()
        return False, e.msg
    finally:
        conn.close()


QUERIES_PATH = os.path.join(os.path.dirname(__file__), "..", "sql", "queries.sql")


def load_report_queries():
    """Parse sql/queries.sql into [(title, sql)]. One source of truth for the report."""
    with open(QUERIES_PATH, encoding="utf-8") as fh:
        text = fh.read()
    out = []
    for block in re.split(r"(?m)^-- (?=Q\d)", text)[1:]:
        lines = block.split("\n")
        title = lines[0].strip()
        body = "\n".join(ln for ln in lines[1:] if not ln.lstrip().startswith("--")).strip()
        out.append((title, body.rstrip(";")))
    return out


def flash_and_rerun(message):
    st.session_state["flash"] = message
    st.rerun()


st.title("Limit Order Book Dashboard")

# Show the message saved before the last rerun
if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

tab_orders, tab_fills, tab_analytics, tab_reports, tab_manage = st.tabs(
    ["Orders", "Fills", "Analytics", "Reports", "Manage"]
)

# ---------------- Orders ----------------
with tab_orders:
    orders = query("SELECT * FROM orders ORDER BY ts DESC, order_id DESC")
    st.caption(f"{len(orders)} orders")
    st.dataframe(orders, use_container_width=True, hide_index=True)

# ---------------- Fills ----------------
with tab_fills:
    fills = query("SELECT * FROM fills ORDER BY fill_id DESC")
    st.caption(f"{len(fills)} fills")
    st.dataframe(fills, use_container_width=True, hide_index=True)

# ---------------- Analytics ----------------
with tab_analytics:
    left, right = st.columns(2)
    with left:
        st.subheader("Orders by status")
        by_status = query("SELECT status, COUNT(*) AS n FROM orders GROUP BY status")
        st.bar_chart(by_status.set_index("status"))
    with right:
        st.subheader("Fill volume per price")
        by_price = query(
            "SELECT price_ticks, SUM(quantity) AS volume "
            "FROM fills GROUP BY price_ticks ORDER BY price_ticks"
        )
        st.bar_chart(by_price.set_index("price_ticks"))

# ---------------- Reports ----------------
with tab_reports:
    st.caption("Each panel runs a query from sql/queries.sql")
    for title, body in load_report_queries():
        with st.expander(title, expanded=False):
            st.code(body + ";", language="sql")
            try:
                st.dataframe(query(body), use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(str(e))

# ---------------- Manage ----------------
with tab_manage:
    st.subheader("Place order")

    next_id = query(
        "SELECT COALESCE(MAX(order_id), 0) + 1 AS n FROM orders WHERE order_id < 900000"
    )["n"].iloc[0]

    next_ts = int(query(
        "SELECT COALESCE(MAX(ts), 0) + 1 AS n FROM orders WHERE order_id < 900000"
    )["n"].iloc[0])

    with st.form("place_order"):
        c1, c2, c3 = st.columns(3)
        order_id = c1.number_input("Order ID", min_value=1, value=int(next_id), step=1)
        trader_id = c2.number_input("Trader ID", min_value=1, value=1, step=1)
        instrument_id = c3.number_input("Instrument ID", min_value=1, value=1, step=1)

        c4, c5, c6, c7 = st.columns(4)
        side = c4.selectbox("Side", ["BUY", "SELL"])
        order_type = c5.selectbox("Type", ["LIMIT", "MARKET"])
        price = c6.number_input("Price (ticks)", min_value=0, value=58000, step=1)
        qty = c7.number_input("Quantity", min_value=1, value=1, step=1)

        submitted = st.form_submit_button("Place order")

    if submitted:
        price_val = None if order_type == "MARKET" else int(price)
        ok, msg = run(
            "INSERT INTO orders (order_id, trader_id, instrument_id, side, order_type, "
            "price_ticks, quantity, ts) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (int(order_id), int(trader_id), int(instrument_id), side,
             order_type, price_val, int(qty), next_ts),
        )
        if ok:
            flash_and_rerun(f"Order {int(order_id)} placed")
        else:
            st.error(msg)

    st.divider()
    st.subheader("Cancel order")

    with st.form("cancel_order"):
        cancel_id = st.number_input("Order ID to cancel", min_value=1, value=1, step=1)
        cancel_clicked = st.form_submit_button("Cancel order")

    if cancel_clicked:
        ok, msg = run("cancel_order", (int(cancel_id),), proc=True)
        if ok:
            flash_and_rerun(f"Order {int(cancel_id)} cancelled")
        else:
            st.error(msg)

    st.divider()
    st.subheader("Stop orders")
    st.dataframe(
        query("SELECT * FROM stop_orders_status ORDER BY stop_id DESC"),
        use_container_width=True, hide_index=True,
    )

    next_stop = int(query(
        "SELECT COALESCE(MAX(stop_id), 899999) + 1 AS n FROM stop_orders"
    )["n"].iloc[0])

    with st.form("add_stop"):
        s1, s2, s3 = st.columns(3)
        stop_id = s1.number_input("Stop ID", min_value=900000, value=next_stop, step=1)
        stop_trader = s2.number_input("Trader ID", min_value=1, value=1, step=1, key="st_tr")
        stop_instr = s3.number_input("Instrument ID", min_value=1, value=1, step=1, key="st_in")
        s4, s5, s6, s7 = st.columns(4)
        stop_side = s4.selectbox("Side", ["BUY", "SELL"], key="st_side")
        trigger = s5.number_input("Trigger (ticks)", min_value=1, value=58020, step=1)
        limit_p = s6.number_input("Limit (ticks)", min_value=1, value=58030, step=1)
        stop_qty = s7.number_input("Quantity", min_value=1, value=1, step=1, key="st_q")
        add_stop = st.form_submit_button("Add stop order")

    if add_stop:
        ok, msg = run(
            "INSERT INTO stop_orders (stop_id, trader_id, instrument_id, side, "
            "limit_price_ticks, trigger_price_ticks, quantity) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (int(stop_id), int(stop_trader), int(stop_instr), stop_side,
             int(limit_p), int(trigger), int(stop_qty)),
        )
        if ok:
            flash_and_rerun(f"Stop order {int(stop_id)} added (dormant)")
        else:
            st.error(msg)