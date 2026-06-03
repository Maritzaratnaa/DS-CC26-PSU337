import streamlit as st
import os
import pandas as pd
import ast
import plotly.express as px
from collections import Counter

BASE_DIR = os.path.dirname(__file__)
file_path = os.path.join(BASE_DIR, "data_preprocessed.csv")

df = pd.read_csv(file_path)

st.set_page_config(
    page_title="Dashboard Analisis Skill Lowongan IT",
    layout="wide"
)

def convert_to_list(x):
    if isinstance(x, list):
        return x

    try:
        return ast.literal_eval(x)
    except:
        return []

df["deskripsi"] = df["deskripsi"].apply(convert_to_list)

total_lowongan = len(df)

jumlah_posisi = df["posisi"].nunique()

all_skills = set()

for skills in df["deskripsi"]:
    all_skills.update(skills)

jumlah_skill_unik = len(all_skills)

avg_skill_per_job = (
    df["deskripsi"]
    .apply(len)
    .mean()
)

st.title("Dashboard Analisis Skill Lowongan IT")

st.markdown("""
Dashboard ini menyajikan analisis kebutuhan skill pada beberapa posisi IT berdasarkan dataset lowongan kerja.
Pengguna dapat mengeksplorasi distribusi posisi, membandingkan kebutuhan skill antar posisi, serta melihat relevansi suatu skill terhadap berbagai posisi pekerjaan.
""")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="**Total Lowongan**",
        value=f"{total_lowongan:,}"
    )

with col2:
    st.metric(
        label="**Jumlah Posisi**",
        value=jumlah_posisi
    )

with col3:
    st.metric(
        label="**Jumlah Skill Unik**",
        value=jumlah_skill_unik
    )
    
with col4:
    st.metric(
        label="**Avg Skill per Lowongan**",
        value=f"{avg_skill_per_job:.1f}"
    )

tab1, tab2, tab3 = st.tabs([
    "**Dataset Overview**",
    "**Position Comparison**",
    "**Skill Explorer**"
])
 
with tab1:
    st.subheader("Overview Dataset")
    st.info(
        "Gambaran umum mengenai distribusi data lowongan berdasarkan posisi dan level pekerjaan."
    )

    selected_level = st.selectbox(
        "**Filter Level**",
        ["Semua", "Entry", "Middle", "Senior", "Unspecified"]
    )

    if selected_level == "Semua":
        filtered_df = df.copy()
    else:
        filtered_df = df[
            df["level"].str.lower() == selected_level.lower()
        ]
    
    chart_col1, chart_col2 = st.columns([3, 2])
    
    with chart_col1:
    
        st.markdown("### Distribusi Lowongan per Posisi")

        position_counts = (
            filtered_df["posisi"]
            .value_counts()
            .sort_values()
        )

        fig = px.bar(
            x=position_counts.values,
            y=position_counts.index,
            orientation="h",
            text=position_counts.values,
            labels={
                "x": "Jumlah Lowongan",
                "y": "Posisi"
            }
        )

        fig.update_traces(
            texttemplate="%{text:.0f}",
            textposition="outside"
        )

        fig.update_layout(
            height=max(600, len(position_counts) * 30),
            yaxis_title="",
            xaxis_title="Jumlah Lowongan",
            margin=dict(r=80)
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
        
    with chart_col2:
    
        st.markdown("### Distribusi Level")

        level_counts = (
            filtered_df["level"]
            .value_counts()
            .reset_index()
        )

        level_counts.columns = [
            "Level",
            "Jumlah"
        ]

        fig_level = px.pie(
            level_counts,
            names="Level",
            values="Jumlah",
            hole=0.5
        )

        fig_level.update_layout(
            height=500
        )

        st.plotly_chart(
            fig_level,
            use_container_width=True
        )
        
        st.markdown("### Top 5 Skill")

        counter = Counter()

        for skills in filtered_df["deskripsi"]:

            unique_skills = set(skills)

            counter.update(unique_skills)

        total_jobs = len(filtered_df)

        skill_percentage = []

        for skill, count in counter.items():

            skill_percentage.append({
                "Skill": skill,
                "Persentase": (count / total_jobs) * 100
            })

        top_skill_df = (
            pd.DataFrame(skill_percentage)
            .sort_values(
                "Persentase",
                ascending=False
            )
            .head(5)
        )

        fig_skill = px.bar(
            top_skill_df.sort_values("Persentase"),
            x="Persentase",
            y="Skill",
            orientation="h",
            text="Persentase"
        )

        fig_skill.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )

        fig_skill.update_layout(
            height=250,
            xaxis_title="Persentase Lowongan (%)",
            yaxis_title="",
            margin=dict(
                l=10,
                r=10,
                t=10,
                b=10
            )
        )

        st.plotly_chart(
            fig_skill,
            use_container_width=True
        )
    
    st.markdown("### Dataset")

    st.caption(
        f"Menampilkan {len(filtered_df):,} lowongan."
    )
    st.dataframe(
        filtered_df,
        use_container_width=True
    )
        
with tab2:

    st.subheader("Position Comparison")
    st.info(
        "Bandingkan dua posisi untuk melihat tingkat kemiripan kebutuhan skill, skill yang paling membedakan, serta skill yang paling sering muncul pada kedua posisi."
    )
    
    level_filter = st.selectbox(
        "**Level**",
        ["Semua", "Entry", "Middle", "Senior"]
    )

    if level_filter == "Semua":
        filtered_df = df.copy()
    else:
        filtered_df = df[
            df["level"].str.lower()
            == level_filter.lower()
        ]

    col1, col2 = st.columns(2)

    posisi_list = sorted(
        filtered_df["posisi"].unique()
    )
    
    if len(posisi_list) < 2:
        st.warning(
            "Tidak cukup posisi pada level yang dipilih."
        )
        st.stop()

    with col1:
        posisi_a = st.selectbox(
            "**Posisi A**",
            posisi_list,
            index=0
        )

    with col2:
        posisi_b = st.selectbox(
            "**Posisi B**",
            posisi_list,
            index=1
        )
        
    def get_skill_set(data, posisi):

        temp = data[data["posisi"] == posisi]

        skills = set()

        for row in temp["deskripsi"]:
            skills.update(row)

        return skills

    skills_a = get_skill_set(filtered_df, posisi_a)
    skills_b = get_skill_set(filtered_df, posisi_b)
    
    intersection = skills_a.intersection(skills_b)
    only_a = skills_a - skills_b
    only_b = skills_b - skills_a
    union = skills_a.union(skills_b)
    
    def get_skill_percentage(data, posisi):

        temp = data[data["posisi"] == posisi]

        total_jobs = len(temp)
        if total_jobs == 0:
            return {}

        counter = Counter()

        for skills in temp["deskripsi"]:

            unique_skills = set(skills)

            counter.update(unique_skills)

        percentage = {
            skill: (count / total_jobs) * 100
            for skill, count in counter.items()
        }

        return percentage
    
    freq_a = get_skill_percentage(filtered_df, posisi_a)
    freq_b = get_skill_percentage(filtered_df, posisi_b)
    
    all_skills_weighted = (
        set(freq_a.keys())
        .union(freq_b.keys())
    )

    numerator = 0
    denominator = 0

    for skill in all_skills_weighted:

        a = freq_a.get(skill, 0)
        b = freq_b.get(skill, 0)

        numerator += min(a, b)
        denominator += max(a, b)

    weighted_jaccard = (
        numerator / denominator
        if denominator > 0
        else 0
    )
    
    all_skills = (
        set(freq_a.keys())
        .union(freq_b.keys())
    )

    comparison = []

    for skill in all_skills:

        comparison.append({
            "Skill": skill,
            posisi_a: freq_a.get(skill, 0),
            posisi_b: freq_b.get(skill, 0)
        })

    comparison_df = pd.DataFrame(comparison)
    
    top_skill_df = comparison_df.copy()

    top_skill_df["Total"] = (
        top_skill_df[posisi_a]
        + top_skill_df[posisi_b]
    )

    top_skill_df = (
        top_skill_df
        .sort_values("Total", ascending=False)
        .head(10)
    )
    
    gap_df = comparison_df.copy()

    gap_df["Gap"] = (
        gap_df[posisi_a]
        - gap_df[posisi_b]
    )

    gap_df = (
        gap_df
        .reindex(
            gap_df["Gap"]
            .abs()
            .sort_values(ascending=False)
            .index
        )
        .head(15)
    )
    
    col1, col2 = st.columns([1,2])
    
    with col1:
        st.markdown("### Weighted Jaccard Similarity")
        st.caption(
            "Mengukur kemiripan kebutuhan skill antar posisi berdasarkan persentase kemunculan skill."
        )

        st.metric(
            "Kemiripan Skill",
            f"{weighted_jaccard*100:.2f}%"
        )

        st.progress(float(weighted_jaccard))
        st.caption("Nilai yang lebih tinggi menunjukkan kebutuhan skill yang semakin mirip.")
        
    with col2:
        st.markdown("### Skill Gap Analysis")
        st.caption(
            "Nilai positif menunjukkan skill lebih dominan pada Posisi A, sedangkan nilai negatif menunjukkan skill lebih dominan pada Posisi B."
        )

        fig_gap = px.bar(
            gap_df.sort_values("Gap"),
            x="Gap",
            y="Skill",
            orientation="h",
            text="Gap"
        )
        
        fig_gap.update_layout(
            height=400,
            xaxis_title="Perbedaan Persentase Kemunculan Skill (%)",
            yaxis_title="",
            showlegend=False
        )
        
        fig_gap.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside"
        )
        
        st.plotly_chart(
            fig_gap,
            use_container_width=True
        )
        
    
    st.markdown("### Top 10 Skill Comparison")
    st.caption(
        "Menampilkan 10 skill dengan tingkat kemunculan tertinggi pada kedua posisi yang dibandingkan."
    )

    fig = px.bar(
        top_skill_df,
        y="Skill",
        x=[posisi_a, posisi_b],
        orientation="h",
        barmode="group",
        labels={
            "value": "Persentase Kemunculan (%)"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    
with tab3:

    st.subheader("Skill Explorer")
    st.info(
        "Visualisasi persentase lowongan pada setiap posisi yang membutuhkan skill atau kombinasi skill yang dipilih. Persentase dihitung terhadap total lowongan pada masing-masing posisi."
    )

    all_skills = sorted({
        skill
        for skills in df["deskripsi"]
        for skill in skills
    })

    selected_skills = st.multiselect(
        "**Pilih Skill**",
        all_skills,
        placeholder="Pilih satu atau lebih skill"
    )

    result = []
    
    if not selected_skills:
        st.stop()

    for posisi in sorted(df["posisi"].unique()):

        temp = df[df["posisi"] == posisi]

        total_jobs = len(temp)

        skill_jobs = temp[
            temp["deskripsi"].apply(
                lambda x: all(
                    skill in x
                    for skill in selected_skills
                )
            )
        ]

        skill_count = len(skill_jobs)

        percentage = (
            skill_count / total_jobs * 100
            if total_jobs > 0
            else 0
        )

        result.append({
            "Posisi": posisi,
            "Persentase": percentage,
            "Jumlah Skill": skill_count,
            "Total Lowongan": total_jobs
        })

    skill_df = pd.DataFrame(result)

    skill_df = skill_df.sort_values(
        "Persentase",
        ascending=False
    )

    fig = px.bar(
        skill_df,
        x="Persentase",
        y="Posisi",
        orientation="h",
        custom_data=[
            "Jumlah Skill",
            "Total Lowongan"
        ]
    )

    fig.update_traces(
        hovertemplate=
        "<b>%{y}</b><br>" +
        "Persentase: %{x:.1f}%<br>" +
        "Mengandung Skill: %{customdata[0]}<br>" +
        "Total Lowongan: %{customdata[1]}" +
        "<extra></extra>"
    )

    skill_label = ", ".join(selected_skills)

    fig.update_layout(
        height=800,
        xaxis_title=f"Persentase Lowongan yang Membutuhkan: {skill_label}",
        yaxis_title=""
    )
    
    fig.update_yaxes(
        autorange="reversed"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    
        