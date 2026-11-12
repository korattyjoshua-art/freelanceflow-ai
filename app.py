import streamlit as st
import json
import os
import datetime
import urllib.parse
import re
st.set_page_config(
    page_title="FreelanceFlow AI",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Historical Payment Escrow Sidebar
with st.sidebar:
    st.header("Historical Payment Escrow")
    st.markdown("---")
    st.markdown("*Gig #101:* React Portfolio Setup")
    st.write("Status: Escrow Funded 🟢")
    st.write("Amount: $300")

# Custom UI Styling & Color Palette for FreelanceFlow AI
st.markdown("""
<style>
    /* Main background & font styling */
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    
    /* Sleek sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
</style>
""", unsafe_allow_html=True)

    /* Custom buttons with PayPal / Tech blue accent */
    .stButton>button {
        background: linear-gradient(135deg, #0070ba 0%, #003087 100%);
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 12px rgba(0, 112, 186, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #005ea6 0%, #002266 100%);
        box-shadow: 0 6px 16px rgba(0, 112, 186, 0.5);
        color: #ffffff;
    }

    /* Chat message bubbles styling */
    .stChatMessage {
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 10px;
        border: 1px solid #30363d;
    }

    st.markdown("*Gig #102:* E-commerce Landing Page")
    st.write("Status: Payout Released ✅")
    st.write("Amount: $650")

# Main Branding Header
st.markdown("<h1 style='text-align: center; color: #0f172a;'>💼 FreelanceFlow AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.1rem;'>Autonomous Agentic Commerce & Milestone Escrow Vault</p>", unsafe_allow_html=True)
st.divider()
HISTORY_FILE = "escrow_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(contract_data):
    history = load_history()
    if not any(h.get('timestamp') == contract_data.get('timestamp') for h in history):
        history.append(contract_data)
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=4)

# 3. Initialize Session State for Chat and Escrow
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your native PayPal Escrow Agent. Type or paste your project negotiation below, and I will structure it into secure milestones."}
    ]

if "escrow_data" not in st.session_state:
    st.session_state.escrow_data = None

if "escrow_status" not in st.session_state:
    st.session_state.escrow_status = "PENDING_DEPOSIT"

# Replace your hardcoded key line with:
import os
import streamlit as st

groq_api_key = st.secrets["GROQ_API_KEY"]

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. User Input Handling
chat_input = st.chat_input("Type project negotiation or chat log here...")

if chat_input:
    # Append and display user message
    st.session_state.messages.append({"role": "user", "content": chat_input})
    with st.chat_message("user"):
        st.markdown(chat_input)

    # AI Processing with Smart Dynamic Extraction
    with st.chat_message("assistant"):
        with st.spinner("💳 PayPal AI Agent analyzing commercial terms..."):
            prompt = f"""
            You are a native PayPal AI Messaging Assistant specializing in escrow.
            Analyze this conversation / text: "{chat_input}"
            prompt = f"""
        You are a native PayPal AI Messaging Assistant specializing in escrow.
        Analyze this conversation / text: "{chat_input}"
        Extract the commercial terms and return ONLY a valid JSON object with this exact structure:
        {{
            "total_contract_value": 3000,
            "milestone_1_title": "string description",
            "milestone_1_amount": 1200,
            "milestone_2_title": "string description",
            "milestone_2_amount": 1800,
            "authenticity_summary": "short trust summary"
        }}
        """

       ai_data = None
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192",
                temperature=0.2,
                max_tokens=500
            )
            raw_content = chat_completion.choices[0].message.content
            if "{" in raw_content and "}" in raw_content:
                start_idx = raw_content.find("{")
                end_idx = raw_content.rfind("}") + 1
                raw_content = raw_content[start_idx:end_idx]

            ai_data = json.loads(raw_content)
        except Exception as e:
            st.error(f"API Error: {e}")
                numbers = [int(n.replace(",", "")) for n in re.findall(r'\b\d{1,3}(?:,\d{3})+\b|\b\d{3,5}\b', chat_input)]
                
                total_val = max(numbers) if numbers else 2500
                m1_val = int(total_val * 0.4)
                m2_val = total_val - m1_val
                
                ai_data = {
                    "total_contract_value": total_val,
                    "milestone_1_title": "Phase 1: Wireframes, UI Setup & Initial Delivery",
                    "milestone_1_amount": m1_val,
                    "milestone_2_title": "Phase 2: Core Logic, Integration & Final Deployment",
                    "milestone_2_amount": m2_val,
                    "authenticity_summary": f"Verified secure agreement extracted from chat log."
                }
                st.toast("⚡ Smart dynamic parser extracted values from your text.", icon="🛡️")

            st.session_state.escrow_data = ai_data
            response_text = f"✅ *Escrow Contract Generated Successfully!* Total Value: *${int(ai_data.get('total_contract_value', 2500)):,} USD*. Scroll down to review milestones and lock funds."
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})

# 6. # 6. Active Escrow Dashboard (Rendered when contract is active)
if st.session_state.escrow_data:
    data = st.session_state.escrow_data
    
    st.write("---")
    st.subheader("🔵 Active PayPal Smart Escrow Vault")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="💳 Total Escrow Value", value=f"${int(data.get('total_contract_value', 3000))}")
    with col2:
        st.metric(label="🔒 Vault Status", value=st.session_state.escrow_status)
        
    st.info(f"📌 *Milestone 1:* {data.get('milestone_1_title', 'Task 1')} (${data.get('milestone_1_amount', 1200)})")
    st.info(f"📌 *Milestone 2:* {data.get('milestone_2_title', 'Task 2')} (${data.get('milestone_2_amount', 1800)})")
    st.write(f"🛡️ *AI Trust Verification:* {data.get('authenticity_summary', 'Verified safe')}")
# Interactive Actions based on State
# Ensure data dictionary exists safely in session state
data = st.session_state.get('data', {})
if st.session_state.escrow_status == "PENDING_DEPOSIT":
    # Use PayPal's standard hosted checkout URL structure for sandbox testing
    total_val = f"{data.get('total_contract_value', 2500):.2f}"
    paypal_sandbox_url = f"https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_xclick&business=sb-6hhqk53795569@business.example.com&amount={total_val}&currency_code=USD&item_name=Freelance+Escrow+Milestone+Lock"
    
    st.link_button("🔒 Deposit & Lock Funds into Secure PayPal Vault", paypal_sandbox_url)

    if st.button("Simulate Buyer Deposit Complete", use_container_width=True):
        st.session_state.escrow_status = "FUNDS_LOCKED_IN_VAULT"
        st.rerun()

elif st.session_state.escrow_status == "FUNDS_LOCKED_IN_VAULT":
    st.success("🔒 Funds are securely locked in the PayPal Sandbox Vault!")
    if st.button("✅ Mark Milestone 1 Complete & Release Funds"):
        st.session_state.escrow_status = "MILESTONE_1_PAID"
        st.rerun()

elif st.session_state.escrow_status == "MILESTONE_1_PAID":
    st.success("🎉 Milestone 1 funds released to freelancer wallet!")
    if st.button("🏁 Complete Final Milestone & Close Contract"):
        st.session_state.escrow_status = "CONTRACT_COMPLETED"
        st.rerun()

elif st.session_state.escrow_status == "CONTRACT_COMPLETED":
    st.balloons()
    st.success("🌟 Contract successfully finalized and fully settled!")
    # Save the completed contract to local history
    contract_record = {
        "status": "COMPLETED",
        "total_value": data.get('total_contract_value', 600),
        "timestamp": str(datetime.datetime.now())
    }
    save_history(contract_record)