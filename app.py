import os
import json
import uuid
from datetime import datetime
import pandas as pd
import streamlit as st

try:
    from groq import Groq
except ImportError:
    Groq = None

st.set_page_config(
    page_title="FreelanceFlow AI | Contract Risk & Escrow Control",
    page_icon="🛡️",
    layout="wide",
)

# --- SAMPLE CONTRACTS FOR 1-CLICK DEMO ---
SAMPLE_CONTRACTS = {
    "High-Risk Marketing Retainer ($6,000)": """SERVICE AGREEMENT
Client: Apex D2C Brands Pvt. Ltd. | Vendor: Independent Growth Consultant
1. Scope: Consultant will deliver brand strategy, ad creatives, and unlimited revisions until Client is fully satisfied.
2. Fees & Payment: Total fee of $6,000 payable Net 90 days after final campaign launch. Client may withhold payment at its sole discretion if KPIs are not met.
3. Intellectual Property: All drafts, frameworks, and source files become exclusive property of Client immediately upon creation, regardless of payment status.
4. Termination: Client may terminate this agreement at any time without prior notice and without paying for partially completed milestones.""",
    "Balanced SaaS Analytics Project ($4,500)": """MILESTONE CONSULTING AGREEMENT
Client: FinEdge Operations | Vendor: Data & Risk Analyst
1. Scope: Build an automated reconciliation dashboard and variance report. Includes up to 2 rounds of revisions per milestone.
2. Milestones & Escrow:
   - M1: Data Schema & Audit ($1,500) - Due upon schema sign-off.
   - M2: Risk & Variance Dashboard ($2,000) - Due upon UAT approval.
   - M3: Handover & SOP Documentation ($1,000) - Due within 7 days of delivery.
3. Payment Terms: Invoices payable Net 15 via escrow release. Late payments accrue 1.5% monthly interest.
4. IP Rights: Full IP transfers to Client strictly upon cleared final payment."""
}

# --- SESSION STATE INITIALIZATION ---
if "contract_text" not in st.session_state:
    st.session_state.contract_text = SAMPLE_CONTRACTS["High-Risk Marketing Retainer ($6,000)"]

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = {
        "risk_score": 82,
        "risk_level": "High Risk",
        "payment_terms": "Net 90 + Discretionary Withholding",
        "ip_trigger": "Upon Creation (Before Payment)",
        "revision_cap": "Unlimited Revisions (Scope Creep Risk)",
        "summary": "Severe cash-flow and IP exposure: payment is delayed 90 days with unilateral withholding rights, while IP transfers before any funds clear.",
        "clauses": [
            {
                "severity": "High",
                "title": "Unilateral Payment Withholding & Net 90 Delay",
                "issue": "Client can withhold payment at sole discretion if subjective KPIs are missed, plus a 90-day payout lag.",
                "redline": "Change to Net 15 upon milestone delivery; tie fees to deliverable completion rather than subjective KPI outcomes."
            },
            {
                "severity": "High",
                "title": "Premature IP Transfer",
                "issue": "IP transfers immediately upon creation even if the client never pays.",
                "redline": "Amend so IP transfers strictly upon receipt of cleared payment for the respective milestone."
            },
            {
                "severity": "Medium",
                "title": "Unlimited Revisions & Zero-Notice Termination",
                "issue": "Unlimited revisions create unbounded labor cost, and termination without notice forfeits in-progress work.",
                "redline": "Cap revisions at 2 rounds per milestone and require 7 days' notice plus pro-rata payment for completed work."
            }
        ]
    }

if "milestones" not in st.session_state:
    st.session_state.milestones = pd.DataFrame([
        {"Milestone": "M1: Discovery & Scope Audit", "Amount ($)": 1500.0, "Due Trigger": "Signed Scope", "Status": "Released"},
        {"Milestone": "M2: Core Deliverable Build", "Amount ($)": 2500.0, "Due Trigger": "Staging Review", "Status": "Escrowed"},
        {"Milestone": "M3: Final Handover & QA", "Amount ($)": 2000.0, "Due Trigger": "Final Sign-Off", "Status": "Pending"},
    ])

if "audit_log" not in st.session_state:
    st.session_state.audit_log = [
        {
            "Timestamp (UTC)": "2026-11-23 16:30:00",
            "Milestone": "M1: Discovery & Scope Audit",
            "Action": "PayPal Sandbox Payout Released ($1,500.00)",
            "Reference ID": "PP-SBX-84A19C",
        },
        {
            "Timestamp (UTC)": "2026-11-23 16:45:00",
            "Milestone": "M2: Core Deliverable Build",
            "Action": "Funds Locked in Escrow ($2,500.00)",
            "Reference ID": "PP-SBX-91F04D",
        },
    ]


def analyze_contract_with_groq(text: str, api_key: str) -> dict:
    """Calls Groq LLM to return structured JSON risk analysis."""
    client = Groq(api_key=api_key)
    prompt = f"""
    You are a Senior Financial Risk & Commercial Operations Analyst.
    Analyze the following freelance/vendor contract and return ONLY valid JSON with this exact schema:
    {{
      "risk_score": <integer 0-100 where 100 is highest risk>,
      "risk_level": "<Low Risk | Medium Risk | High Risk>",
      "payment_terms": "<short summary of net days / payment conditions>",
      "ip_trigger": "<when IP transfers>",
      "revision_cap": "<revision limit or scope risk>",
      "summary": "<2-sentence executive risk & cash-flow assessment>",
      "clauses": [
        {{
          "severity": "<High | Medium | Low>",
          "title": "<clause name>",
          "issue": "<financial or operational risk>",
          "redline": "<recommended protective rewrite>"
        }}
      ]
    }}

    Contract Text:
    {text}
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Control Panel")
    api_key = st.text_input(
        "Groq API Key (Optional for Live AI)",
        value=os.getenv("GROQ_API_KEY", ""),
        type="password",
        help="Uses built-in sample analysis if left blank so reviewers can test immediately."
    )
    st.divider()
    st.subheader("📄 Quick Load Sample")
    selected_sample = st.selectbox("Choose a preset contract:", list(SAMPLE_CONTRACTS.keys()))
    if st.button("Load Sample Contract", use_container_width=True):
        st.session_state.contract_text = SAMPLE_CONTRACTS[selected_sample]
        st.rerun()

    st.divider()
    st.caption("FreelanceFlow AI v2.1 — Financial Risk Control, PayPal Sandbox Escrow & Cash-Flow Governance.")

# --- HEADER & TOP KPI METRIC STRIP ---
st.title("🛡️ FreelanceFlow AI")
st.caption("Automated Contract Risk Scoring, Cash-Flow Term Extraction & Milestone Escrow Governance")

df_m = st.session_state.milestones
total_contract = float(df_m["Amount ($)"].sum())
escrowed_amt = float(df_m.loc[df_m["Status"] == "Escrowed", "Amount ($)"].sum())
released_amt = float(df_m.loc[df_m["Status"] == "Released", "Amount ($)"].sum())
res = st.session_state.analysis_result

k1, k2, k3, k4 = st.columns(4)
k1.metric("Overall Risk Score", f"{res['risk_score']} / 100", res["risk_level"], delta_color="inverse")
k2.metric("Total Contract Value", f"${total_contract:,.2f}")
k3.metric("Active Escrow Hold", f"${escrowed_amt:,.2f}", "Protected Funds")
k4.metric("Released Payouts", f"${released_amt:,.2f}", f"{len(res['clauses'])} Clauses Flagged")

st.divider()

# --- MAIN WORKSPACE TABS ---
tab1, tab2, tab3 = st.tabs([
    "1️⃣ Contract Risk Analyzer",
    "2️⃣ Milestone Escrow & PayPal Sandbox",
    "3️⃣ Executive Risk & Remediation Brief"
])

with tab1:
    col_in, col_out = st.columns([1, 1.15], gap="large")

    with col_in:
        st.subheader("Contract Input")
        uploaded_file = st.file_uploader("Upload Contract (.txt)", type=["txt"])
        if uploaded_file is not None:
            st.session_state.contract_text = uploaded_file.read().decode("utf-8", errors="ignore")

        contract_input = st.text_area(
            "Review or edit contract clauses below:",
            value=st.session_state.contract_text,
            height=290,
        )
        st.session_state.contract_text = contract_input

        if st.button("🔍 Run Financial & Risk Audit", type="primary", use_container_width=True):
            if api_key and Groq is not None:
                with st.spinner("Auditing payment terms, IP triggers, and operational risk..."):
                    try:
                        st.session_state.analysis_result = analyze_contract_with_groq(contract_input, api_key)
                        st.success("Live AI risk audit completed.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Groq API error: {e}")
            else:
                st.info("Running in instant demo mode (add a Groq API key in the sidebar or Secrets for custom live audits).")

    with col_out:
        st.subheader("Key Commercial & Financial Controls")
        c1, c2, c3 = st.columns(3)
        c1.info(f"*Payment Terms*\n\n{res['payment_terms']}")
        c2.info(f"*IP Transfer Trigger*\n\n{res['ip_trigger']}")
        c3.info(f"*Scope / Revisions*\n\n{res['revision_cap']}")

        st.subheader("Flagged Clauses & Redline Recommendations")
        for clause in res["clauses"]:
            sev = clause["severity"]
            badge = "🔴 HIGH RISK" if sev == "High" else ("🟠 MEDIUM RISK" if sev == "Medium" else "🟢 LOW RISK")
            with st.expander(f"{badge} — {clause['title']}", expanded=(sev == "High")):
                st.markdown(f"*Exposure:* {clause['issue']}")
                st.markdown(f"*Recommended Redline:* {clause['redline']}")

with tab2:
    st.subheader("Milestone Escrow & Payout Governance")
    st.write("Manage milestone schedules below or execute a PayPal Sandbox escrow lock / release action:")

    edited_df = st.data_editor(
        st.session_state.milestones,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Amount ($)": st.column_config.NumberColumn(format="$%.2f", min_value=0.0),
            "Status": st.column_config.SelectboxColumn(
                options=["Pending", "Escrowed", "Approved", "Released"],
                required=True,
            ),
        },
    )
    st.session_state.milestones = edited_df

    st.markdown("#### 💳 PayPal Sandbox Escrow Action Trigger")
    if len(edited_df) > 0:
        act_col1, act_col2, act_col3 = st.columns([2, 1, 1])
        milestone_names = edited_df["Milestone"].tolist()
        target_ms = act_col1.selectbox("Select Milestone:", milestone_names)

        if act_col2.button("🔒 Lock Funds in Escrow", use_container_width=True):
            idx = edited_df.index[edited_df["Milestone"] == target_ms][0]
            amt = float(edited_df.loc[idx, "Amount ($)"])
            st.session_state.milestones.loc[idx, "Status"] = "Escrowed"
            ref_id = f"PP-SBX-{uuid.uuid4().hex[:6].upper()}"
            st.session_state.audit_log.insert(0, {
                "Timestamp (UTC)": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "Milestone": target_ms,
                "Action": f"Funds Locked in Escrow (${amt:,.2f})",
                "Reference ID": ref_id,
            })
            st.rerun()

        if act_col3.button("✅ Release Payout", type="primary", use_container_width=True):
            idx = edited_df.index[edited_df["Milestone"] == target_ms][0]
            amt = float(edited_df.loc[idx, "Amount ($)"])
            st.session_state.milestones.loc[idx, "Status"] = "Released"
            ref_id = f"PP-SBX-{uuid.uuid4().hex[:6].upper()}"
            st.session_state.audit_log.insert(0, {
                "Timestamp (UTC)": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "Milestone": target_ms,
                "Action": f"PayPal Sandbox Payout Released (${amt:,.2f})",
                "Reference ID": ref_id,
            })
            st.rerun()

    st.markdown("#### 🧾 Immutable Escrow Audit Trail")
    st.dataframe(pd.DataFrame(st.session_state.audit_log), use_container_width=True, hide_index=True)

    csv_data = edited_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export Escrow Ledger (CSV)",
        data=csv_data,
        file_name="freelanceflow_escrow_ledger.csv",
        mime="text/csv",
    )

with tab3:
    st.subheader("Executive Risk & Remediation Simulator")
    st.warning(f"*Executive Assessment:* {res['summary']}")

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        st.markdown("#### Financial Exposure Breakdown")
        pending_amt = float(edited_df.loc[edited_df["Status"] == "Pending", "Amount ($)"].sum())
        approved_amt = float(edited_df.loc[edited_df["Status"] == "Approved", "Amount ($)"].sum())
        summary_table = pd.DataFrame({
            "Stage": ["Released (Cleared)", "Approved (Ready for Payout)", "Escrowed (Protected)", "Pending (Unfunded)"],
            "Amount ($)": [released_amt, approved_amt, escrowed_amt, pending_amt],
        })
        st.dataframe(summary_table, use_container_width=True, hide_index=True)

    with col_b:
        st.markdown("#### Pre-Sign Redline Controls (Live Score Impact)")
        c_pay = st.checkbox("Enforce Net 15 milestone-tied payout schedule (-22 risk pts)", value=False)
        c_ip = st.checkbox("Restrict IP transfer until cleared final payment (-25 risk pts)", value=False)
        c_rev = st.checkbox("Cap revisions at 2 rounds + 7-day notice kill fee (-15 risk pts)", value=False)
        c_esc = st.checkbox("Require PayPal Escrow lock prior to kickoff (-8 risk pts)", value=True)

        reduction = (22 if c_pay else 0) + (25 if c_ip else 0) + (15 if c_rev else 0) + (8 if c_esc else 0)
        projected_score = max(5, int(res["risk_score"]) - reduction)
        st.metric(
            "Projected Post-Redline Risk Score",
            f"{projected_score} / 100",
            f"-{reduction} pts risk reduction",
            delta_color="normal",
        )

    # --- GENERATE DOWNLOADABLE EXECUTIVE BRIEF ---
    clause_lines = "\n".join(
        [f"- [{c['severity']}] {c['title']}: {c['issue']} | Redline: {c['redline']}" for c in res["clauses"]]
    )
    report_md = f"""# FreelanceFlow AI — Executive Contract & Escrow Audit Brief
Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

## 1. Risk Summary
- Baseline Risk Score: {res['risk_score']} / 100 ({res['risk_level']})
- Projected Post-Redline Score: {projected_score} / 100
- Payment Terms: {res['payment_terms']}
- IP Transfer Trigger: {res['ip_trigger']}
- Scope / Revision Cap: {res['revision_cap']}
- Executive Assessment: {res['summary']}

## 2. Escrow & Cash-Flow Position
- Total Contract Value: ${total_contract:,.2f}
- Released Payouts: ${released_amt:,.2f}
- Active Escrow Hold: ${escrowed_amt:,.2f}
- Unfunded / Pending: ${pending_amt:,.2f}

## 3. Flagged Clauses & Recommended Redlines
{clause_lines}
"""
    st.download_button(
        label="📄 Download Executive Risk Brief (.md)",
        data=report_md.encode("utf-8"),
        file_name="freelanceflow_executive_audit_brief.md",
        mime="text/markdown",
    )
 