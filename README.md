# Perfil cadastral com CadÚnico amostral

Projeto em `Python + Streamlit` para reproduzir uma leitura de perfil cadastral inspirada nos microdados amostrais desidentificados do CadÚnico, com foco em renda, situação cadastral, vulnerabilidade familiar e priorização territorial.

## Para que serve

Este projeto foi desenhado para responder perguntas como:

- qual é a distribuição das famílias por faixa de renda;
- onde há maior concentração de cadastros não atualizados;
- quais municípios combinam maior extrema pobreza com maior vulnerabilidade;
- como priorizar territórios para ação cadastral e proteção social.

## O que é o CadÚnico

O Cadastro Único é o principal instrumento de identificação e caracterização socioeconômica das famílias de baixa renda no Brasil. Ele é usado como base para seleção e acompanhamento de políticas públicas, programas sociais e benefícios.

## Fonte e desenho dos dados

Este projeto se inspira nos **microdados amostrais desidentificados do CadÚnico** disponibilizados pelo MDS. Como o objetivo aqui é construir um case reproduzível de portfólio, a solução usa uma **base sintética alinhada às variáveis analíticas públicas**, combinando:

- uma base territorial pública de municípios de Alagoas;
- um desenho amostral inspirado nas dimensões mais comuns do CadÚnico;
- variáveis familiares, de renda, atualização cadastral e vulnerabilidade.

Referência institucional:

- [Microdados do MDS](https://www.gov.br/mds/pt-br/servicos/sagi/microdados)
- [Portal Analítico do Cadastro Único - FAQ](https://www.gov.br/mds/pt-br/acoes-e-programas/cadastro-unico/perguntas-frequentes-cadastro-unico/portal-analitico-do-cadastro-unico)

## O que os dados representam

Cada linha da amostra representa uma **família sintética**, não uma pessoa individual. As principais variáveis usadas no projeto são:

- `faixa_renda`
- `situacao_cadastral`
- `arranjo_familiar`
- `area_domicilio`
- `qtd_pessoas`
- `qtd_criancas`
- `qtd_idosos`
- `possui_pcd`
- `possui_cnis`
- `saneamento_precario`
- `trabalho_informal_predominante`
- `score_vulnerabilidade`

Essas variáveis foram escolhidas porque ajudam a reproduzir leituras comuns em gestão social:

- perfil de renda;
- composição familiar;
- fragilidade cadastral;
- vulnerabilidade multidimensional;
- necessidade de priorização municipal.

## Técnicas usadas

- `pandas`
  Para geração, transformação e agregação dos dados.
- `numpy`
  Para simulação reprodutível da amostra.
- **simulação calibrada**
  Para reproduzir um cenário plausível de famílias do CadÚnico.
- **engenharia de indicadores**
  Para criar métricas municipais e um índice de priorização cadastral.
- `Streamlit`
  Para o painel interativo.
- `Plotly`
  Para visualizações exploratórias e territoriais.

## Como cada técnica foi utilizada

### 1. Simulação amostral

O projeto gera uma amostra sintética de famílias para os 102 municípios de Alagoas. Cada município recebe um volume diferente de famílias e combinações distintas de:

- renda;
- situação cadastral;
- arranjo familiar;
- presença de crianças, idosos e PCD;
- vulnerabilidades adicionais.

### 2. Engenharia de vulnerabilidade

O campo `score_vulnerabilidade` é calculado combinando fatores como:

- extrema pobreza;
- cadastro não atualizado;
- trabalho informal predominante;
- saneamento precário;
- presença de PCD;
- maior número de crianças.

Esse score não é um modelo supervisionado; ele é um índice sintético para priorização analítica.

### 3. Agregação territorial

Depois, o pipeline agrega a amostra por município para gerar indicadores como:

- `pct_extrema_pobreza`
- `pct_cadastros_nao_atualizados`
- `taxa_pcd_pct`
- `taxa_cnis_pct`
- `taxa_saneamento_precario_pct`
- `taxa_trabalho_informal_pct`
- `indice_priorizacao_cadastral`

### 4. Classificação rule-based

O projeto classifica os municípios como:

- `alto`
- `moderado`
- `baixo`

de acordo com o índice de priorização cadastral.

## Como executar

```bash
git clone https://github.com/flaviagaia/perfil-cadastral-CadUnico.git
cd perfil-cadastral-CadUnico
python3 main.py
streamlit run app.py
```

## Testes

```bash
python3 -m unittest discover -s tests -v
```

## English

### Purpose

This project reproduces a CadÚnico-style household profiling workflow, focused on income, registration quality, family composition, vulnerability, and territorial prioritization.

### Data

It uses a synthetic household-level sample inspired by the public de-identified CadÚnico sample logic and a real municipal territorial base for Alagoas.

### Techniques and tools

- `pandas` for transformation and aggregation
- `numpy` for reproducible synthetic sampling
- rule-based vulnerability scoring
- municipal prioritization indicators
- `Streamlit` and `Plotly` for the dashboard
