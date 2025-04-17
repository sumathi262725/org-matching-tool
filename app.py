import streamlit as st
import pandas as pd
from rapidfuzz import fuzz
from io import StringIO

def normalize_name(name):
    import re
    name = str(name).lower()
    name = re.sub(r'[^a-z0-9\s]', '', name)
    name = re.sub(r'\b(inc|ltd|llc|co|corp|group|plc|limited)\b', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

st.title("🏢 Org Matching Tool")

uploaded_file = st.file_uploader("📁 Upload your orgs CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("### Original Data", df.head())

    df['normalized_name'] = df['org_name'].apply(normalize_name)

    threshold = st.slider("🧠 Match Similarity Threshold", 80, 100, 90)
    matches = []
    orgs = df['normalized_name'].tolist()

    for i in range(len(orgs)):
        for j in range(i+1, len(orgs)):
            score = fuzz.ratio(orgs[i], orgs[j])
            if score >= threshold:
                matches.append({
                    'Org A': df.iloc[i]['org_name'],
                    'Org B': df.iloc[j]['org_name'],
                    'Match Score': score
                })

    st.subheader("🔍 Potential Duplicate Matches")
    st.write(pd.DataFrame(matches))

    if 'org_code' in df.columns and 'parent_code' in df.columns:
        code_to_name = dict(zip(df['org_code'], df['org_name']))
        df['parent_name'] = df['parent_code'].map(code_to_name)
        st.subheader("🏗️ Org Hierarchy")
        st.write(df[['org_code', 'org_name', 'parent_code', 'parent_name']])
