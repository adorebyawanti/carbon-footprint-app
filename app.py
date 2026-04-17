import streamlit as st
import pandas as pd
from db import add_user, login_user, save_history, get_history, get_leaderboard
from model import predict_category

# ---------------- CHATBOT ----------------
def chatbot_response(user_msg):
    msg = user_msg.lower()

    if any(word in msg for word in ["reduce", "improve", "lower", "decrease"]):
        return "Try reducing vehicle usage 🚗, save electricity ⚡, and manage waste ♻️."

    elif any(word in msg for word in ["transport", "travel", "vehicle", "car"]):
        return "Use public transport 🚍, carpool, or switch to EVs."

    elif any(word in msg for word in ["electricity", "power", "energy"]):
        return "Switch to LED bulbs 💡 and turn off unused appliances."

    elif any(word in msg for word in ["diet", "food", "eat"]):
        return "Plant-based diets 🌱 are more eco-friendly."

    elif any(word in msg for word in ["waste", "garbage", "trash"]):
        return "Recycle ♻️, reuse, and compost waste."

    else:
        return "🌍 Ask me about transport, electricity, diet, or waste to reduce carbon footprint!"

# 🏅 Badge based on rank
def get_badge(rank):
    if rank == 1:
        return "👑 Carbon Champion"
    elif rank == 2:
        return "🥈 Eco Warrior"
    elif rank == 3:
        return "🥉 Green Star"
    elif rank <= 5:
        return "🌿 Eco Contributor"
    else:
        return "🌱 Beginner"

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Carbon AI", layout="wide")

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------- UI ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #fbc2eb, #fda085);
}
.glass {
    background: rgba(255,255,255,0.9);
    padding: 25px;
    border-radius: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🌍 Carbon AI</h1>", unsafe_allow_html=True)

# ---------------- AUTH ----------------
if not st.session_state.logged_in:

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Signup"])

    with tab1:
        user = st.text_input("👤 Username")
        password = st.text_input("🔒 Password", type="password")

        if st.button("🚀 Login", key="login_btn"):
            result = login_user(user, password)

            if result == "success":
                st.session_state.logged_in = True
                st.session_state.username = user
                st.rerun()
            elif result == "no_user":
                st.error("⚠️ Account not found")
            elif result == "wrong_password":
                st.error("❌ Incorrect password")

    with tab2:
        new_user = st.text_input("🆕 Create Username")
        new_pass = st.text_input("🔑 Create Password", type="password")

        if st.button("✨ Signup", key="signup_btn"):
            add_user(new_user, new_pass)
            st.success("✅ Account created!")

# ---------------- MAIN ----------------
else:
    user = st.session_state.username

    st.sidebar.write(f"👤 {user}")

    if st.sidebar.button("🚪 Logout", key="logout_btn"):
        st.session_state.logged_in = False
        st.rerun()

    # ---------------- LEADERBOARD ----------------
    st.sidebar.markdown("### 🏆 Monthly Leaderboard")
    leaders = get_leaderboard()

    if leaders:
        for i, (uname, avg) in enumerate(leaders, 1):
            badge = get_badge(i)
            st.sidebar.write(f"{i}. {uname} - {round(avg,2)} CO₂ {badge}")
    else:
        st.sidebar.write("No data yet")

    page = st.sidebar.radio("📌 Menu", ["Dashboard", "History"])

    # ---------------- DASHBOARD ----------------
    if page == "Dashboard":

        st.markdown('<div class="glass">', unsafe_allow_html=True)

        leaders = get_leaderboard()
        user_rank = None

        for i, (uname, avg) in enumerate(leaders, 1):
            if uname == user:
                user_rank = i
                break

        if user_rank:
            badge = get_badge(user_rank)
            st.markdown(f"""
            <div style="background:#222;padding:15px;border-radius:10px;color:white;text-align:center;">
            🏅 Your Rank: {user_rank} <br>
            {badge}
            </div>
            """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        distance = col1.number_input("🚗 Travel Distance (km)", 0.0)
        electricity = col2.number_input("⚡ Electricity (kWh)", 0.0)
        transport = col3.selectbox("🚍 Transport", ["car", "bus", "bike"])
        city = col4.selectbox("🌆 City", ["Mumbai", "Delhi", "Pune", "Bangalore"])

        diet = st.selectbox("🥗 Diet", ["veg", "nonveg"])
        waste = st.number_input("🗑 Waste (kg)", 0.0)

        transport_factor = {"car": 0.21, "bus": 0.1, "bike": 0.05}
        city_factor = {"Mumbai": 1.2, "Delhi": 1.5, "Pune": 1.0, "Bangalore": 1.1}
        diet_factor = 2 if diet == "nonveg" else 1

        base = (
            distance * transport_factor[transport]
            + electricity * 0.82
            + diet_factor
            + waste * 0.5
        )

        total = base * city_factor[city]

        score = max(0, 100 - int(total))
        trees = int(total / 21)

        category = predict_category(distance, transport, electricity, diet)

        st.markdown(f"## 🌡 Total CO₂: **{round(total,2)} kg**")

        colA, colB = st.columns(2)
        colA.metric("🌟 Eco Score", score)
        colB.metric("🌳 Trees Needed", trees)

        if score > 80:
            badge = "🌟 Eco Hero"
            color = "#4CAF50"
        elif score > 50:
            badge = "🌿 Green Citizen"
            color = "#2196F3"
        else:
            badge = "⚠️ High Polluter"
            color = "#F44336"

        st.markdown(
            f"""
            <div style="background:{color};padding:15px;border-radius:10px;color:white;text-align:center;">
            🏅 {badge}
            </div>
            """,
            unsafe_allow_html=True
        )

        data = pd.DataFrame({
            "Type": ["🚗 Transport", "⚡ Electricity", "🥗 Diet", "🗑 Waste"],
            "CO2": [
                distance * transport_factor[transport],
                electricity * 0.82,
                diet_factor,
                waste * 0.5
            ]
        })

        st.subheader("📊 Emission Breakdown")
        st.bar_chart(data.set_index("Type"))

        st.subheader(f"🧠 AI Prediction: {category}")

        if st.button("💾 Save", key="save_btn"):
            save_history(user, total, category)
            st.success("Saved!")
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # ---------------- CHATBOT ----------------
        st.markdown("### 🤖 AI Eco Assistant 🌱")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        user_input = st.text_input("💬 Ask something...")

        if st.button("📨 Send", key="send_btn"):
            if user_input:
                reply = chatbot_response(user_input)
                st.session_state.chat_history.append(("🧑 You", user_input))
                st.session_state.chat_history.append(("🤖 AI", reply))

        for sender, msg in st.session_state.chat_history:
            st.markdown(f"**{sender}:** {msg}")

        # ---------------- 🌱 SUSTAINABLE HUB ----------------
        st.markdown("### 🌱 Take Action (Sustainable Hub)")

        st.markdown("""
        #### 🚗 Green Transport
        - https://www.iea.org/reports/global-ev-outlook-2023
        - Use public transport or carpool

        #### ☀️ Clean Energy
        - https://en.wikipedia.org/wiki/Solar_energy
        - Use solar panels and save electricity
        
        #### ♻️ Waste Management
        - https://www.epa.gov/recycle/reducing-waste-what-you-can-do
        - Recycle and compost
        """)

        # ---------------- 🎯 PERSONALIZED SUGGESTIONS ----------------
        st.markdown("### 🎯 Personalized Suggestions")

        if transport == "car":
            st.info("🚗 You rely on cars. Consider switching to EVs or carpooling!")

        if electricity > 100:
            st.info("⚡ High electricity usage. Try solar energy or reduce consumption!")

        if waste > 10:
            st.info("🗑 High waste generation. Start recycling and composting!")

    # ---------------- HISTORY ----------------
    elif page == "History":

        st.markdown('<div class="glass">', unsafe_allow_html=True)

        history = get_history(user)

        if history:
            df = pd.DataFrame(history, columns=["User", "CO2", "Category", "Date"])
            df["Date"] = pd.to_datetime(df["Date"]).dt.date
            st.dataframe(df)
            st.line_chart(df["CO2"])
        else:
            st.info("No history available")

        st.markdown('</div>', unsafe_allow_html=True)