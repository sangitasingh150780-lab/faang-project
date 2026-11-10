import streamlit as st
import csv
import io
from datetime import date

st.set_page_config(page_title="Hisab AI - Pro", page_icon="🧾", layout="wide")

# --- STYLE ---
st.markdown("""
<style>
.big{font-size:22px;font-weight:bold}
.red{color:red;font-weight:bold}
.green{color:green;font-weight:bold}
</style>
""", unsafe_allow_html=True)

st.title("🧾 Hisab AI - PRO Advance")
st.write("Hindi ya English me pucho - `Ramesh ka udhaar kitna hai?` / `Total sale kitni hai?`")

# --- DATA ---
if "data" not in st.session_state:
    st.session_state.data = [
        {"ID": 1, "Customer": "Ramesh", "Item": "Chawal", "Amount": 500, "Udhaar": 500, "Date": "2026-11-08", "Status": "Udhaar"},
        {"ID": 2, "Customer": "Suresh", "Item": "Daal", "Amount": 300, "Udhaar": 0, "Date": "2026-11-08", "Status": "Paid"},
        {"ID": 3, "Customer": "Ramesh", "Item": "Cheeni", "Amount": 200, "Udhaar": 200, "Date": "2026-11-09", "Status": "Udhaar"},
        {"ID": 4, "Customer": "Priya", "Item": "Tel", "Amount": 400, "Udhaar": 0, "Date": "2026-11-09", "Status": "Paid"},
        {"ID": 5, "Customer": "Suresh", "Item": "Aata", "Amount": 350, "Udhaar": 350, "Date": "2026-11-09", "Status": "Udhaar"},
        {"ID": 6, "Customer": "Amit", "Item": "Chawal", "Amount": 600, "Udhaar": 600, "Date": "2026-11-09", "Status": "Udhaar"},
    ]
if "history" not in st.session_state:
    st.session_state.history = []
if "next_id" not in st.session_state:
    st.session_state.next_id = 7

data = st.session_state.data

# --- SIDEBAR ---
st.sidebar.header("⚙️ Control Panel")

# Upload
uploaded = st.sidebar.file_uploader("Apna CSV Upload Karo", type=["csv"])
if uploaded is not None:
    try:
        text = uploaded.getvalue().decode('utf-8')
        reader = csv.DictReader(io.StringIO(text))
        new_data = []
        nid = 1
        for r in reader:
            amt = int(float(r.get("Amount", 0) or 0))
            udh = int(float(r.get("Udhaar", 0) or 0))
            new_data.append({"ID": nid, "Customer": r.get("Customer",""), "Item": r.get("Item",""), "Amount": amt, "Udhaar": udh, "Date": r.get("Date","2026-11-09"), "Status": "Udhaar" if udh>0 else "Paid"})
            nid += 1
        st.session_state.data = new_data
        st.session_state.next_id = nid
        st.sidebar.success(f"Ho gaya! {len(new_data)} rows load ho gaye.")
        data = new_data
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# Add Entry
st.sidebar.subheader("➕ Nayi Entry")
with st.sidebar.form("add_form", clear_on_submit=True):
    c_name = st.text_input("Customer Name *")
    c_item = st.text_input("Item")
    c_amt = st.number_input("Amount (Rs.)", min_value=0, value=100)
    c_udhaar = st.number_input("Udhaar (Rs.)", min_value=0, value=0)
    c_date = st.date_input("Date", value=date.today())
    submit = st.form_submit_button("✅ Add Karo")
    if submit:
        if c_name:
            st.session_state.data.append({"ID": st.session_state.next_id, "Customer": c_name, "Item": c_item, "Amount": c_amt, "Udhaar": c_udhaar, "Date": str(c_date), "Status": "Udhaar" if c_udhaar>0 else "Paid"})
            st.session_state.next_id += 1
            st.sidebar.success("Entry add ho gayi!")
        else:
            st.sidebar.error("Customer naam to likho!")

# Download
st.sidebar.subheader("⬇️ Data Download")
if data:
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=["ID","Customer","Item","Amount","Udhaar","Date","Status"])
    w.writeheader()
    for d in data:
        w.writerow(d)
    st.sidebar.download_button("CSV Download Karo", out.getvalue(), file_name="hisab.csv", mime="text/csv")

# Delete
st.sidebar.subheader("🗑️ Entry Delete Karo")
if data:
    del_id = st.sidebar.selectbox("Kis ID ko delete karna hai?", [d["ID"] for d in data])
    if st.sidebar.button("Delete Karo"):
        st.session_state.data = [d for d in st.session_state.data if d["ID"] != del_id]
        st.sidebar.success(f"ID {del_id} delete ho gaya!")
        st.rerun()

# --- FILTER ---
st.subheader("🔍 Filter / Search")
col_f1, col_f2, col_f3 = st.columns(3)
all_cust = ["Sab"] + sorted(list(set(d["Customer"] for d in data)))
sel_cust = col_f1.selectbox("Customer Chunno", all_cust)
sel_status = col_f2.selectbox("Status", ["Sab", "Paid", "Udhaar"])
search_txt = col_f3.text_input("Search Item / Customer", placeholder="Chawal likho...")

filtered = data
if sel_cust != "Sab":
    filtered = [d for d in filtered if d["Customer"] == sel_cust]
if sel_status != "Sab":
    filtered = [d for d in filtered if d["Status"] == sel_status]
if search_txt:
    filtered = [d for d in filtered if search_txt.lower() in d["Customer"].lower() or search_txt.lower() in d["Item"].lower()]

# --- DASHBOARD ---
total_sale = sum(d["Amount"] for d in data)
total_udhaar = sum(d["Udhaar"] for d in data)
total_paid = total_sale - total_udhaar
total_cust = len(set(d["Customer"] for d in data))

c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Total Sale", f"Rs. {total_sale}")
c2.metric("⚠️ Total Udhaar", f"Rs. {total_udhaar}")
c3.metric("✅ Total Paid", f"Rs. {total_paid}")
c4.metric("👥 Total Customers", f"{total_cust}")

# --- UDHAAR ALERT ---
st.subheader("🚨 Udhaar Alert - Jiska Udhaar Zyada Hai")
udhaar_map = {}
for d in data:
    udhaar_map[d["Customer"]] = udhaar_map.get(d["Customer"], 0) + d["Udhaar"]
udhaar_sorted = sorted(udhaar_map.items(), key=lambda x: x[1], reverse=True)
for cust, tot in udhaar_sorted:
    if tot > 0:
        if tot >= 500:
            st.write(f"🔴 **{cust}** - Rs. {tot} - **Jaldi Vasool Karo!**")
        else:
            st.write(f"🟡 **{cust}** - Rs. {tot}")
    else:
        st.write(f"🟢 **{cust}** - Sab Paid Hai!")

# --- TABLE - WITHOUT DATAFRAME ---
st.subheader(f"📊 Full Hisab - {len(filtered)} Entries Dikha Raha Hai")
st.write("**ID | Customer | Item | Amount | Udhaar | Date | Status**")
st.write("---")
for d in filtered:
    emoji = "🔴" if d["Udhaar"] >= 500 else "🟡" if d["Udhaar"] > 0 else "🟢"
    st.write(f"{emoji} **{d['ID']}** | {d['Customer']} | {d['Item']} | Rs. {d['Amount']} | Rs. {d['Udhaar']} | {d['Date']} | {d['Status']}")

# --- CHARTS - WITHOUT BAR_CHART ---
st.divider()
col_ch1, col_ch2 = st.columns(2)
with col_ch1:
    st.subheader("📈 Item Wise Sale")
    item_tot = {}
    for d in data:
        item_tot[d["Item"]] = item_tot.get(d["Item"], 0) + d["Amount"]
    for item, tot in sorted(item_tot.items(), key=lambda x: x[1], reverse=True):
        st.write(f"**{item}** - Rs. {tot}")
        st.progress(min(tot / max(total_sale, 1), 1.0))

with col_ch2:
    st.subheader("💰 Customer Wise Udhaar")
    for cust, tot in udhaar_sorted:
        st.write(f"**{cust}** - Rs. {tot}")
        if total_udhaar > 0:
            st.progress(min(tot / total_udhaar, 1.0))
        else:
            st.progress(0.0)

# --- AI BRAIN ---
st.divider()
st.subheader("💬 Hisab AI se Pucho")
col_a, col_b, col_c, col_d = st.columns(4)
if col_a.button("Total sale kitni hai?"): st.session_state.q = "total sale kitni hai"
if col_b.button("Ramesh ka udhaar?"): st.session_state.q = "Ramesh ka udhaar kitna hai"
if col_c.button("Sabse zyada kya bika?"): st.session_state.q = "sabse zyada kya bika"
if col_d.button("Who has highest udhaar?"): st.session_state.q = "who has highest udhaar"

sawal = st.text_input("Apna sawaal yahan likho...", value=st.session_state.get("q", ""), key="input_q", placeholder="Ex: Priya ne kitna kharida? / Chawal ki sale kitni hai?")

def answer_question(q, data):
    q_low = q.lower().strip()
    customers = list(set(d["Customer"] for d in data))
    found = None
    for c in customers:
        if c.lower() in q_low:
            found = c
            break
    if found and any(w in q_low for w in ["udhaar","udhar","baki","bakaya","due","pending","balance"]):
        total = sum(d["Udhaar"] for d in data if d["Customer"] == found)
        return f"✅ {found} ka total udhaar hai: Rs. {total}", [d for d in data if d["Customer"] == found]
    if found and any(w in q_low for w in ["kitna","how much","total","kharida","bought","liya","sale"]):
        total = sum(d["Amount"] for d in data if d["Customer"] == found)
        items = ", ".join([d["Item"] for d in data if d["Customer"] == found])
        return f"✅ {found} ne total Rs. {total} ka liya hai. Items: {items}", [d for d in data if d["Customer"] == found]
    if found:
        rows = [d for d in data if d["Customer"] == found]
        return f"✅ {found} ka full hisab. Total: Rs. {sum(d['Amount'] for d in rows)} | Udhaar: Rs. {sum(d['Udhaar'] for d in rows)}", rows
    if any(w in q_low for w in ["total sale","total bikri","kul sale","kitni sale","kitni bikri","total business"]):
        return f"✅ Total Sale hai: Rs. {sum(d['Amount'] for d in data)}", data
    if any(w in q_low for w in ["total udhaar","total udhar","total baki","total bakaya","total due","kitna udhaar"]):
        return f"✅ Total Udhaar hai: Rs. {sum(d['Udhaar'] for d in data)}", data
    if any(w in q_low for w in ["total paid","kitna paid","kitna mila"]):
        paid = sum(d["Amount"] for d in data) - sum(d["Udhaar"] for d in data)
        return f"✅ Total Paid (Mila Hua) hai: Rs. {paid}", data
    if any(w in q_low for w in ["sabse zyada","sabse jyada","top","best seller","most sold","zyada bika"]):
        top_item = max(item_tot, key=item_tot.get)
        return f"✅ Sabse zyada bika: {top_item} - Rs. {item_tot[top_item]}", data
    if any(w in q_low for w in ["sabse zyada udhaar","highest udhaar","kispe sabse zyada"]):
        top_c = max(udhaar_map, key=udhaar_map.get)
        return f"✅ Sabse zyada udhaar {top_c} pe hai: Rs. {udhaar_map[top_c]}", data
    if any(w in q_low for w in ["kitne customer","how many customer","customer list","sab customer"]):
        return f"✅ Total {len(customers)} customers hai: {', '.join(customers)}", data
    items_list = list(set(d["Item"] for d in data))
    for it in items_list:
        if it.lower() in q_low:
            tot = sum(d["Amount"] for d in data if d["Item"] == it)
            return f"✅ {it} ki total sale hai: Rs. {tot}", [d for d in data if d["Item"] == it]
    return "❌ Sorry, main ye sawaal nahi samjha. Try karo: Total sale kitni hai? / Ramesh ka udhaar?", None

if st.button("🔍 Jawab Do", type="primary"):
    if sawal:
        ans, f_rows = answer_question(sawal, data)
        st.success(ans)
        if f_rows is not None and len(f_rows) < len(data):
            for d in f_rows:
                st.write(f"{d['Customer']} | {d['Item']} | Rs. {d['Amount']} | Rs. {d['Udhaar']} | {d['Status']}")
        st.session_state.history.append((sawal, ans))

if st.session_state.history:
    st.divider()
    st.subheader("🕒 Pichle Sawaal")
    for q, a in reversed(st.session_state.history[-5:]):
        st.write(f"**Q:** {q}")
        st.write(f"**A:** {a}")
        st.write("---")

st.caption("Hisab AI PRO v4 - 100% No Pandas | No Dataframe | No Bar Chart | Hindi + English")