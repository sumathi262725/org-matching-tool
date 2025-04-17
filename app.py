import streamlit as st
import pandas as pd
from rapidfuzz import fuzz
import networkx as nx
import matplotlib.pyplot as plt
from io import StringIO

st.set_page_config(page_title="Org Matching Tool", layout="wide")
st.title("🏢 Organization Matching & Hierarchy Tool")

# Upload CSV
uploaded_file = st.file_uploader("Upload your organization CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("📄 Uploaded Data")
    st.dataframe(df)

    # Normalize org name for matching
    df['org_name_clean'] = df['org_name'].str.lower().str.replace(r'[^\w\s]', '', regex=True).str.strip()

    st.subheader("🔍 Duplicate Name Detection (Fuzzy Matching)")
    threshold = st.slider("Fuzzy match threshold (0–100)", min_value=0, max_value=100, value=80)

    matches = []
    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            name1 = df.iloc[i]['org_name_clean']
            name2 = df.iloc[j]['org_name_clean']
            score = fuzz.token_sort_ratio(name1, name2)
            if score >= threshold:
                matches.append({
                    "Org 1": df.iloc[i]['org_name'],
                    "Org 2": df.iloc[j]['org_name'],
                    "Match Score": score
                })

    if matches:
        matches_df = pd.DataFrame(matches).sort_values(by="Match Score", ascending=False)
        st.success(f"Found {len(matches_df)} potential duplicates:")
        st.dataframe(matches_df)

        # Download button
        csv = matches_df.to_csv(index=False)
        st.download_button("📥 Download Matches CSV", csv, "duplicate_matches.csv", "text/csv")
    else:
        st.info("No duplicates found at the current threshold.")

    # Filter/Search
    st.subheader("🔎 Search Organization Names")
    search_query = st.text_input("Type to search org names:")
    if search_query:
        results = df[df['org_name'].str.contains(search_query, case=False, na=False)]
        st.write(f"🔍 Found {len(results)} matching results:")
        st.dataframe(results)

    # Missing Parents
    st.subheader("⚠️ Orgs Missing Valid Parent Code")
    if 'org_code' in df.columns and 'parent_code' in df.columns:
        missing_parents = df[df['parent_code'].notna() & ~df['parent_code'].isin(df['org_code'])]
        st.warning(f"{len(missing_parents)} org(s) have invalid or missing parent codes:")
        st.dataframe(missing_parents)

    # Clustering similar names (basic)
    st.subheader("🔗 Similarity Clusters")
    cluster_threshold = st.slider("Cluster threshold", 70, 100, 85)
    clusters = []
    used = set()

    for i in range(len(df)):
        if i in used:
            continue
        group = [df.iloc[i]['org_name']]
        used.add(i)
        for j in range(i + 1, len(df)):
            if j not in used:
                score = fuzz.token_sort_ratio(df.iloc[i]['org_name_clean'], df.iloc[j]['org_name_clean'])
                if score >= cluster_threshold:
                    group.append(df.iloc[j]['org_name'])
                    used.add(j)
        if len(group) > 1:
            clusters.append(group)

    if clusters:
        for idx, cluster in enumerate(clusters, start=1):
            st.write(f"🧠 Cluster {idx}:")
            st.write(", ".join(cluster))
    else:
        st.info("No clusters found at this threshold.")

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
        nx.draw(G, pos, with_labels=True, node_size=1500, node_color="lightblue", font_size=10, font_weight="bold", arrows=True)
        st.pyplot(fig)
    else:
        st.warning("CSV must contain 'org_code' and 'parent_code' columns to show hierarchy.")
else:
    st.info("Upload a CSV file to begin.")
