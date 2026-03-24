from __future__ import annotations

import json

import numpy as np
import pandas as pd

from .config import MUNICIPAL_PROFILE_PATH, PROCESSED_DIR, RAW_MUNICIPALITIES_PATH, SAMPLE_PATH, SUMMARY_PATH, YEAR_REFERENCE


def load_municipalities() -> pd.DataFrame:
    raw_df = pd.read_csv(RAW_MUNICIPALITIES_PATH)
    municipalities = raw_df[["co_mun", "no_mun"]].drop_duplicates().rename(
        columns={"co_mun": "codigo_municipio", "no_mun": "municipio"}
    )
    municipalities["codigo_municipio"] = municipalities["codigo_municipio"].astype(str)
    return municipalities.sort_values("municipio").reset_index(drop=True)


def build_synthetic_cadunico_sample(seed: int = 42, year_reference: int = YEAR_REFERENCE) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    municipalities = load_municipalities()

    renda_faixas = [
        "Extrema pobreza",
        "Pobreza",
        "Baixa renda",
        "Acima da faixa prioritária",
    ]
    renda_probs = [0.33, 0.28, 0.26, 0.13]

    situacoes = ["Cadastro atualizado", "Cadastro desatualizado", "Averiguação cadastral"]
    situacao_probs = [0.68, 0.22, 0.10]

    arranjos = [
        "Casal com filhos",
        "Monoparental feminina",
        "Pessoa sozinha",
        "Família extensa",
    ]
    arranjo_probs = [0.36, 0.29, 0.15, 0.20]

    area_probs = [0.72, 0.28]

    records: list[dict[str, object]] = []
    for idx, row in municipalities.iterrows():
        municipal_factor = 0.8 + (idx / len(municipalities)) * 1.9
        target_households = int(max(250, rng.normal(1100 * municipal_factor, 110)))

        for household_idx in range(target_households):
            renda = rng.choice(renda_faixas, p=renda_probs)
            situacao = rng.choice(situacoes, p=situacao_probs)
            arranjo = rng.choice(arranjos, p=arranjo_probs)
            area = rng.choice(["Urbana", "Rural"], p=area_probs)
            pessoas = int(np.clip(rng.normal(loc=3.4 if arranjo != "Pessoa sozinha" else 1.0, scale=1.1), 1, 8))
            criancas = int(np.clip(rng.poisson(1.4 if arranjo != "Pessoa sozinha" else 0.1), 0, pessoas))
            idosos = int(np.clip(rng.poisson(0.45), 0, pessoas))
            pcd = int(rng.random() < (0.12 if renda in {"Extrema pobreza", "Pobreza"} else 0.07))
            cnis = int(rng.random() < 0.58)
            saneamento_precario = int(rng.random() < (0.41 if area == "Rural" else 0.19))
            trabalho_informal = int(rng.random() < (0.64 if renda in {"Extrema pobreza", "Pobreza"} else 0.38))

            score = (
                (3 if renda == "Extrema pobreza" else 2 if renda == "Pobreza" else 1 if renda == "Baixa renda" else 0)
                + (1.2 if situacao != "Cadastro atualizado" else 0)
                + (1.1 if trabalho_informal else 0)
                + (1.0 if saneamento_precario else 0)
                + (0.8 if pcd else 0)
                + (0.5 if criancas >= 3 else 0)
            )

            records.append(
                {
                    "ano_referencia": year_reference,
                    "codigo_municipio": row["codigo_municipio"],
                    "municipio": row["municipio"],
                    "id_familia": f"{row['codigo_municipio']}-{household_idx:05d}",
                    "faixa_renda": renda,
                    "situacao_cadastral": situacao,
                    "arranjo_familiar": arranjo,
                    "area_domicilio": area,
                    "qtd_pessoas": pessoas,
                    "qtd_criancas": criancas,
                    "qtd_idosos": idosos,
                    "possui_pcd": pcd,
                    "possui_cnis": cnis,
                    "saneamento_precario": saneamento_precario,
                    "trabalho_informal_predominante": trabalho_informal,
                    "score_vulnerabilidade": round(score, 2),
                }
            )

    return pd.DataFrame(records)


def build_municipal_profile(sample_df: pd.DataFrame) -> pd.DataFrame:
    municipal_df = (
        sample_df.groupby(["codigo_municipio", "municipio"], as_index=False)
        .agg(
            familias_amostra=("id_familia", "count"),
            media_pessoas=("qtd_pessoas", "mean"),
            media_criancas=("qtd_criancas", "mean"),
            media_idosos=("qtd_idosos", "mean"),
            taxa_pcd_pct=("possui_pcd", lambda s: s.mean() * 100),
            taxa_cnis_pct=("possui_cnis", lambda s: s.mean() * 100),
            taxa_saneamento_precario_pct=("saneamento_precario", lambda s: s.mean() * 100),
            taxa_trabalho_informal_pct=("trabalho_informal_predominante", lambda s: s.mean() * 100),
            vulnerabilidade_media=("score_vulnerabilidade", "mean"),
        )
    )

    renda_extrema = (
        sample_df.assign(flag_extrema=sample_df["faixa_renda"].eq("Extrema pobreza").astype(int))
        .groupby(["codigo_municipio", "municipio"], as_index=False)["flag_extrema"]
        .mean()
    )
    renda_extrema["pct_extrema_pobreza"] = (renda_extrema["flag_extrema"] * 100).round(2)
    renda_extrema = renda_extrema.drop(columns=["flag_extrema"])

    desatualizado = (
        sample_df.assign(flag_desatualizado=sample_df["situacao_cadastral"].ne("Cadastro atualizado").astype(int))
        .groupby(["codigo_municipio", "municipio"], as_index=False)["flag_desatualizado"]
        .mean()
    )
    desatualizado["pct_cadastros_nao_atualizados"] = (desatualizado["flag_desatualizado"] * 100).round(2)
    desatualizado = desatualizado.drop(columns=["flag_desatualizado"])

    profile_df = municipal_df.merge(renda_extrema, on=["codigo_municipio", "municipio"]).merge(
        desatualizado, on=["codigo_municipio", "municipio"]
    )

    profile_df["indice_priorizacao_cadastral"] = (
        (
            profile_df["pct_extrema_pobreza"] / profile_df["pct_extrema_pobreza"].mean()
            + profile_df["pct_cadastros_nao_atualizados"] / profile_df["pct_cadastros_nao_atualizados"].mean()
            + profile_df["taxa_saneamento_precario_pct"] / profile_df["taxa_saneamento_precario_pct"].mean()
            + profile_df["taxa_trabalho_informal_pct"] / profile_df["taxa_trabalho_informal_pct"].mean()
        )
        / 4
        * 100
    ).round(2)

    profile_df["perfil_prioritario"] = profile_df["indice_priorizacao_cadastral"].map(
        lambda v: "alto" if v >= 120 else "moderado" if v >= 95 else "baixo"
    )
    numeric_cols = [
        "media_pessoas",
        "media_criancas",
        "media_idosos",
        "taxa_pcd_pct",
        "taxa_cnis_pct",
        "taxa_saneamento_precario_pct",
        "taxa_trabalho_informal_pct",
        "vulnerabilidade_media",
    ]
    profile_df[numeric_cols] = profile_df[numeric_cols].round(2)
    return profile_df.sort_values("indice_priorizacao_cadastral", ascending=False).reset_index(drop=True)


def build_summary_dict(sample_df: pd.DataFrame, profile_df: pd.DataFrame) -> dict[str, object]:
    top_priority = profile_df.sort_values("indice_priorizacao_cadastral", ascending=False).iloc[0]
    top_extreme = profile_df.sort_values("pct_extrema_pobreza", ascending=False).iloc[0]
    return {
        "ano_referencia": YEAR_REFERENCE,
        "municipios_cobertos": int(profile_df["codigo_municipio"].nunique()),
        "familias_amostra": int(sample_df["id_familia"].nunique()),
        "pct_extrema_pobreza": float(round(sample_df["faixa_renda"].eq("Extrema pobreza").mean() * 100, 2)),
        "pct_cadastros_nao_atualizados": float(round(sample_df["situacao_cadastral"].ne("Cadastro atualizado").mean() * 100, 2)),
        "vulnerabilidade_media": float(round(sample_df["score_vulnerabilidade"].mean(), 2)),
        "municipio_maior_priorizacao": str(top_priority["municipio"]),
        "municipio_maior_extrema_pobreza": str(top_extreme["municipio"]),
    }


def run_pipeline() -> dict[str, object]:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    sample_df = build_synthetic_cadunico_sample()
    profile_df = build_municipal_profile(sample_df)
    summary = build_summary_dict(sample_df, profile_df)
    sample_df.to_csv(SAMPLE_PATH, index=False)
    profile_df.to_csv(MUNICIPAL_PROFILE_PATH, index=False)
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary
