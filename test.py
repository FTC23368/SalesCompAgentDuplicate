import streamlit as st
import pinecone
print(pinecone.__file__)
# Inject custom CSS for pill-shaped buttons
st.markdown("""
    <style>
    div.stButton > button {
        border-radius: 20px;
        padding: 6px 16px;
        margin: 5px 5px 10px 0;
        font-weight: 500;
        font-size: 0.9rem;
        border: 1px solid;
        background-color: transparent;
        cursor: pointer;
    }
    .policy-btn { color: #4CAF50; border-color: #4CAF50; }
    .commission-btn { color: #2196F3; border-color: #2196F3; }
    .data-btn { color: #FF9800; border-color: #FF9800; }
    .plan-btn { color: #E91E63; border-color: #E91E63; }
    .research-btn { color: #9C27B0; border-color: #9C27B0; }
    </style>
""", unsafe_allow_html=True)
# Custom button layout using columns
cols = st.columns(5)
if cols[0].button("Policy Questions", key="policy"):
    st.markdown('<style>div[data-testid=“stButton”] button {color: #4CAF50;}</style>', unsafe_allow_html=True)
    st.success("Policy Questions clicked")
elif cols[1].button("Commission Calculation", key="commission"):
    st.markdown('<style>div[data-testid=“stButton”] button {color: #2196F3;}</style>', unsafe_allow_html=True)
    st.success("Commission Calculation clicked")
elif cols[2].button("Data Analysis", key="data"):
    st.markdown('<style>div[data-testid=“stButton”] button {color: #FF9800;}</style>', unsafe_allow_html=True)
    st.success("Data Analysis clicked")
elif cols[3].button("Plan Design", key="plan"):
    st.markdown('<style>div[data-testid=“stButton”] button {color: #E91E63;}</style>', unsafe_allow_html=True)
    st.success("Plan Design clicked")
elif cols[4].button("Research", key="research"):
    st.markdown('<style>div[data-testid=“stButton”] button {color: #9C27B0;}</style>', unsafe_allow_html=True)
    st.success("Research clicked")