import streamlit as st
import pandas as pd
from rapidfuzz import fuzz
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(page_title="Org Matching Tool", layout="wide")
st.title("🏢 Organization Matching & Hierarchy Tool")

# Upload CSV
uploaded_file = st.file_uploader("Upload your organization CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("📄 Uploaded Data")
    st.dataframe(df)

    # Fuzzy Matching Section
    st.subheader("🔍 Duplicate Name Detection (Fuzzy Matching)")
    threshold = st.slider("Fuzzy match threshold (0-100)", min_value=0, max_value=100, value=85)

    matches = []
    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            name1 = df.iloc[i]['org_name']
            name2 = df.iloc[j]['org_name']
            score = fuzz.ratio(name1.lower(), name2.lower())
            if score >= threshold:
                matches.append((name1, name2, score))

    if matches:
        st.success(f"Found {len(matches)} possible duplicates:")
        for m in matches:
            st.write(f"🔁 **{m[0]}** ↔ **{m[1]}** (score: {m[2]})")
    else:
        st.info("No potential duplicates found at the selected threshold.")

    # Org Hierarchy Graph
    st.subheader("📊 Organization Hierarchy Graph")

    if 'org_code' in df.columns and 'parent_code' in df.columns:
        G = nx.DiGraph()

        for _, row in df.iterrows():
            org = row['org_code']
            parent = row['parent_code']
            if pd.notna(parent):
                G.add_edge(parent, org)

        pos = nx.spring_layout(G)
        fig, ax = plt.subplots(figsize=(12, 6))
        nx.draw(G, pos, with_labels=True, node_size=1500, node_color="skyblue", font_size=10, font_weight="bold", arrows=True)
        st.pyplot(fig)
    else:
        st.warning("CSV must contain 'org_code' and 'parent_code' columns to show hierarchy.")
else:
    st.info("Upload a CSV file to begin.")

