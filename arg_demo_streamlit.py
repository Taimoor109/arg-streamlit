
import streamlit as st
import pandas as pd

st.set_page_config(page_title="ARG Investor Demo", page_icon="🐑", layout="centered")

# ----------------------- Data -----------------------
ANIMALS = ["Sheep", "Goat", "Cow"]
PROCESSES = ["Live", "Butchered", "Meat"]
WEIGHT_BUCKETS = [
    {"key":"lt80","label":"Less than 80 kg","min":40,"max":79},
    {"key":"81-100","label":"81 – 100 kg","min":81,"max":100},
    {"key":"101-150","label":"101 – 150 kg","min":101,"max":150},
    {"key":"151-200","label":"151 – 200 kg","min":151,"max":200},
    {"key":"gt200","label":"More than 200 kg","min":201,"max":350},
]
PRODUCTS = [
    dict(id="s1", animal="Sheep", process="Meat", title="Premium Sheep Meat", weightKg=50, exWorks=3.6, distanceKm=120, addCostPerKg=0.2, rating=4.8, sold=729, icon="🥩", moqKg=50, progressKg=68, state="Selangor"),
    dict(id="s2", animal="Sheep", process="Meat", title="Healthy Sheep Meat",  weightKg=108, exWorks=3.5, distanceKm=60,  addCostPerKg=0.15, rating=3.2, sold=239, icon="🍖", moqKg=80, progressKg=38, state="Johor"),
    dict(id="c1", animal="Cow",   process="Butchered", title="Premium Cow (Butchered)", weightKg=91, exWorks=2.9, distanceKm=220, addCostPerKg=0.25, rating=4.7, sold=3415, icon="🥩", moqKg=100, progressKg=92, state="Pahang"),
    dict(id="g1", animal="Goat",  process="Live", title="Whole Goat – Live",     weightKg=86, exWorks=4.1, distanceKm=30,  addCostPerKg=0.10, rating=4.6, sold=1012, icon="🐐", moqKg=70, progressKg=70, state="Malacca"),
]
SHIPPING_RATE = 0.005  # RM per kg per km

def price_per_kg(p): 
    return round(p["exWorks"] + SHIPPING_RATE * p["distanceKm"] + p["addCostPerKg"], 2)

# ----------------------- Session State -----------------------
if "page" not in st.session_state: st.session_state.page = "Shop"
if "wallet" not in st.session_state: st.session_state.wallet = 210.0
if "selection" not in st.session_state: st.session_state.selection = {"animal":None, "process":None, "weight":None}
if "detail" not in st.session_state: st.session_state.detail = None

def reset_shop():
    st.session_state.selection = {"animal":None, "process":None, "weight":None}
    st.session_state.detail = None

# ----------------------- UI Helpers -----------------------
def header_bar(title: str):
    left, mid, right = st.columns([3,2,3])
    with left:
        st.text_input("Search", placeholder="Search", label_visibility="collapsed")
    with mid:
        st.write("")
    with right:
        st.metric("Wallet (MYR)", value=f"{st.session_state.wallet:,.0f}")

def product_card(p):
    c = st.container(border=True)
    with c:
        st.markdown(f"### {p['icon']} {p['title']}")
        st.caption(f"{p['state']} • {p['distanceKm']} km  |  ⭐ {p['rating']}  |  Sold {p['sold']}")
        st.write(f"**{price_per_kg(p):.2f} RM/kg**")
        cols = st.columns([1,1])
        if cols[0].button("View", key=f"view_{p['id']}"):
            st.session_state.detail = p
            st.experimental_rerun()
        cols[1].button("Add to Compare", key=f"cmp_{p['id']}")

def price_breakdown(p):
    logistics = SHIPPING_RATE * p["distanceKm"]
    df = pd.DataFrame({
        "Component": ["Ex-Works", f"Distance × {SHIPPING_RATE:.3f}", "Seller add. cost", "Total"],
        "Value (RM/kg)": [p["exWorks"], round(logistics,2), p["addCostPerKg"], price_per_kg(p)]
    })
    st.dataframe(df, hide_index=True, use_container_width=True)

# ----------------------- Pages -----------------------
def page_shop():
    header_bar("ARG Marketplace")
    sel = st.session_state.selection

    # Step 1: Animal
    if not sel["animal"]:
        st.subheader("Please select your type of meat")
        cols = st.columns(3)
        for i, a in enumerate(ANIMALS):
            if cols[i].button(f"{'🐑' if a=='Sheep' else '🐐' if a=='Goat' else '🐄'}\n{a}"):
                sel["animal"] = a
                st.experimental_rerun()
        return

    # Step 2: Process
    if not sel["process"]:
        st.subheader(f"{sel['animal']} — select processing")
        cols = st.columns(3)
        for i, p in enumerate(PROCESSES):
            if cols[i].button(f"{ '🧬' if p=='Live' else '🔪' if p=='Butchered' else '🥩'}\n{p}"):
                sel["process"] = p
                st.experimental_rerun()
        st.button("← Back", on_click=reset_shop)
        return

    # Step 3: Weight
    if not sel["weight"]:
        st.subheader("Select weight range")
        for b in WEIGHT_BUCKETS:
            if st.button(b["label"]):
                sel["weight"] = b
                st.experimental_rerun()
        st.button("← Back", on_click=lambda: sel.update({"process":None}))
        return

    # Step 4: List
    st.markdown(f"**{sel['animal']} › {sel['process']} › {sel['weight']['label']}**")
    tabs = st.tabs(["Popular", "Sale", "Nearby"])  # mimic quick view tabs
    filtered = [p for p in PRODUCTS if p["animal"]==sel["animal"] and p["process"]==sel["process"] and sel["weight"]["min"] <= p["weightKg"] <= sel["weight"]["max"]]
    with tabs[0]:
        for p in sorted(filtered, key=lambda x: x["sold"], reverse=True):
            product_card(p)
    with tabs[1]:
        for p in sorted(filtered, key=lambda x: price_per_kg(x)):
            product_card(p)
    with tabs[2]:
        for p in sorted(filtered, key=lambda x: x["distanceKm"]):
            product_card(p)

    if st.button("← Back", key="back_list"):
        st.session_state.selection["weight"] = None
        st.experimental_rerun()

def page_product_detail(p):
    header_bar(p["title"])
    st.markdown(f"### {p['icon']} {p['title']}") 
    st.caption(f"{p['state']} • {p['distanceKm']} km | ⭐ {p['rating']} | Sold {p['sold']}") 
    st.metric("Price (RM/kg)", f"{price_per_kg(p):.2f}") 
    st.info("Delivery cost included in price") 
    st.subheader("Group Buy Progress") 
    st.progress(min(1.0, p["progressKg"]/p["moqKg"])) 
    st.caption(f"{p['progressKg']}/{p['moqKg']} kg — {'MOQ met' if p['progressKg']>=p['moqKg'] else 'Open group'}") 
    st.subheader("Pricing Breakdown") 
    price_breakdown(p) 

    qty = st.number_input("Quantity (kg)", min_value=1, max_value=999, value=5)
    subtotal = qty * price_per_kg(p)
    st.write(f"**Subtotal:** RM {subtotal:.2f}")

    c1, c2, c3 = st.columns(3)
    if c1.button("Join Group"):
        st.success(f"Joined group for {qty} kg (demo)")
    if c2.button("Direct Buy"):
        st.session_state.wallet = max(0.0, st.session_state.wallet - subtotal)
        st.success(f"Purchased {qty} kg — RM {subtotal:.2f} deducted (demo)")
    if c3.button("← Back"):
        st.session_state.detail = None
        st.experimental_rerun()

def page_wallet():
    header_bar("Wallet")
    st.subheader("Balances") 
    c = st.container(border=True)
    with c:
        st.metric("Cash (MYR)", f"{st.session_state.wallet:,.2f}")
        st.write(":blue[Coupon:] MYR 20 (demo)") 
        st.write(":green[Points:] 10 (demo)") 
    st.subheader("Top up") 
    cols = st.columns(6)
    for i, v in enumerate([5,10,20,50,100,200]):
        if cols[i].button(f"RM {v}"):
            st.session_state.wallet += v
            st.experimental_rerun()
    st.caption("Top-ups are simulated for the demo.")

def page_discover():
    header_bar("Supplier Suite")
    st.subheader("Monthly Sales") 
    df = pd.DataFrame({"Jun":[95000],"Jul":[98000],"Aug":[102000],"Sep":[110000],"Oct":[117458]}).T
    df.columns = ["RM"]
    st.bar_chart(df)
    st.metric("Monthly Sales Value", "RM 117,458")

    st.subheader("Inventory Overview") 
    inv = pd.DataFrame([
        {"Animal":"Sheep","Live":13,"Butchered":1,"Meat(kg)":15},
        {"Animal":"Goat","Live":8,"Butchered":5,"Meat(kg)":60},
        {"Animal":"Cow","Live":4,"Butchered":2,"Meat(kg)":48},
    ])
    st.dataframe(inv, use_container_width=True)

    st.subheader("Farm Supply Overview")
    supply = pd.DataFrame([
        {"Animal":"Sheep","Item":"Feed","Qty":255,"Unit":"kg"},
        {"Animal":"Sheep","Item":"Medicine","Qty":58,"Unit":"vials"},
        {"Animal":"Sheep","Item":"Shampoo","Qty":63,"Unit":"bottles"},
        {"Animal":"Goat","Item":"Medicine","Qty":78,"Unit":"vials"},
        {"Animal":"Cow","Item":"Feed","Qty":351,"Unit":"kg"},
    ])
    st.dataframe(supply, use_container_width=True)

# ----------------------- Router -----------------------
with st.sidebar:
    choice = st.radio("Navigation", ["Shop","Discover","Wallet"], index=["Shop","Discover","Wallet"].index(st.session_state.page))
    if st.button("Reset Shop Flow"):
        reset_shop()
    st.session_state.page = choice

if st.session_state.page == "Wallet":
    page_wallet()
elif st.session_state.page == "Discover":
    page_discover()
else:
    if st.session_state.detail:
        page_product_detail(st.session_state.detail)
    else:
        page_shop()
