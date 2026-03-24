from __future__ import annotations

import json
from json import JSONDecodeError

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import MUNICIPAL_PROFILE_PATH, SAMPLE_PATH, SUMMARY_PATH
from src.pipeline import run_pipeline


st.set_page_config(
    page_title="Perfil cadastral com CadÚnico amostral",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background: #0b1020; color: #f4f7fb; }
    .stMetric { background: rgba(255,255,255,0.04); padding: 12px; border-radius: 14px; }
    </style>
    """,
    unsafe_allow_html=True,
)


REQUIRED_SAMPLE_COLUMNS = {
    "municipio",
    "faixa_renda",
    "situacao_cadastral",
    "arranjo_familiar",
    "qtd_pessoas",
    "qtd_criancas",
    "score_vulnerabilidade",
}

REQUIRED_PROFILE_COLUMNS = {
    "municipio",
    "familias_amostra",
    "pct_extrema_pobreza",
    "pct_cadastros_nao_atualizados",
    "indice_priorizacao_cadastral",
    "perfil_prioritario",
}


def load_data() -> tuple[dict[str, object], pd.DataFrame, pd.DataFrame]:
    if not SUMMARY_PATH.exists() or not SAMPLE_PATH.exists() or not MUNICIPAL_PROFILE_PATH.exists():
        run_pipeline()
    try:
        summary = json.loads(SUMMARY_PATH.read_text())
        sample_df = pd.read_csv(SAMPLE_PATH)
        profile_df = pd.read_csv(MUNICIPAL_PROFILE_PATH)
    except (FileNotFoundError, JSONDecodeError, ValueError, OSError):
        summary = run_pipeline()
        sample_df = pd.read_csv(SAMPLE_PATH)
        profile_df = pd.read_csv(MUNICIPAL_PROFILE_PATH)

    if not REQUIRED_SAMPLE_COLUMNS.issubset(sample_df.columns) or not REQUIRED_PROFILE_COLUMNS.issubset(profile_df.columns):
        summary = run_pipeline()
        sample_df = pd.read_csv(SAMPLE_PATH)
        profile_df = pd.read_csv(MUNICIPAL_PROFILE_PATH)

    return summary, sample_df, profile_df


summary, sample_df, profile_df = load_data()

st.title("Perfil cadastral com CadÚnico amostral")
st.caption(
    "Painel analítico inspirado nos microdados amostrais desidentificados do CadÚnico, com foco em renda, situação cadastral, vulnerabilidade e priorização territorial."
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Municípios", summary["municipios_cobertos"])
col2.metric("Famílias na amostra", f"{summary['familias_amostra']:,}".replace(",", "."))
col3.metric("% extrema pobreza", f"{summary['pct_extrema_pobreza']:.2f}%")
col4.metric("% não atualizados", f"{summary['pct_cadastros_nao_atualizados']:.2f}%")

tab1, tab2, tab3 = st.tabs(["Visão Geral", "Perfil Familiar", "Priorização Territorial"])

with tab1:
    renda_fig = px.histogram(
        sample_df,
        x="faixa_renda",
        color="faixa_renda",
        title="Distribuição da amostra por faixa de renda",
    )
    renda_fig.update_layout(paper_bgcolor="#0b1020", plot_bgcolor="#0b1020", font_color="#f4f7fb", showlegend=False)
    st.plotly_chart(renda_fig, use_container_width=True)

    situacao_fig = px.histogram(
        sample_df,
        x="situacao_cadastral",
        color="situacao_cadastral",
        title="Situação cadastral das famílias na amostra",
    )
    situacao_fig.update_layout(paper_bgcolor="#0b1020", plot_bgcolor="#0b1020", font_color="#f4f7fb", showlegend=False)
    st.plotly_chart(situacao_fig, use_container_width=True)

with tab2:
    familia_fig = px.box(
        sample_df,
        x="arranjo_familiar",
        y="qtd_pessoas",
        color="arranjo_familiar",
        title="Tamanho das famílias por arranjo familiar",
    )
    familia_fig.update_layout(paper_bgcolor="#0b1020", plot_bgcolor="#0b1020", font_color="#f4f7fb", showlegend=False)
    st.plotly_chart(familia_fig, use_container_width=True)

    vulnerabilidade_fig = px.scatter(
        sample_df.sample(min(len(sample_df), 6000), random_state=42),
        x="qtd_criancas",
        y="score_vulnerabilidade",
        color="faixa_renda",
        size="qtd_pessoas",
        title="Vulnerabilidade da amostra por presença de crianças",
        hover_data=["municipio", "situacao_cadastral"],
    )
    vulnerabilidade_fig.update_layout(paper_bgcolor="#0b1020", plot_bgcolor="#0b1020", font_color="#f4f7fb")
    st.plotly_chart(vulnerabilidade_fig, use_container_width=True)

with tab3:
    top_priority = profile_df.head(20)
    priority_fig = px.bar(
        top_priority,
        x="municipio",
        y="indice_priorizacao_cadastral",
        color="perfil_prioritario",
        title="Municípios prioritários para ação cadastral",
        hover_data=["pct_extrema_pobreza", "pct_cadastros_nao_atualizados"],
    )
    priority_fig.update_layout(paper_bgcolor="#0b1020", plot_bgcolor="#0b1020", font_color="#f4f7fb")
    st.plotly_chart(priority_fig, use_container_width=True)

    matrix_fig = px.scatter(
        profile_df,
        x="pct_cadastros_nao_atualizados",
        y="pct_extrema_pobreza",
        size="familias_amostra",
        color="perfil_prioritario",
        hover_data=["municipio", "vulnerabilidade_media"],
        title="Extrema pobreza vs desatualização cadastral",
    )
    matrix_fig.update_layout(paper_bgcolor="#0b1020", plot_bgcolor="#0b1020", font_color="#f4f7fb")
    st.plotly_chart(matrix_fig, use_container_width=True)

    st.dataframe(profile_df, use_container_width=True, hide_index=True)
