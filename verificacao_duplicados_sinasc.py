import os
import glob
import pandas as pd
import numpy as np

# Configurações de entrada e saída
# Pasta onde estão os arquivos originais do SINASC
pasta_arquivos = os.path.join("data", "raw")

# Pasta onde será salvo o relatório
pasta_saida = os.path.join("data", "outputs")

# Cria a pasta de saída caso ela ainda não exista
os.makedirs(pasta_saida, exist_ok=True)

# Caminho completo do arquivo de saída
arquivo_saida = os.path.join(
    pasta_saida,
    "Relatorio_Duplicados_SINASC_2020_2024.xlsx"
)

anos_alvo = ["2020", "2021", "2022", "2023", "2024"]

# Localizar e ler os arquivos de 2020 a 2024 (pelos 4 últimos caracteres do nome, ex: DNSP2024)
todos_arquivos = sorted(glob.glob(os.path.join(pasta_arquivos, "DN*.csv")))
arquivos_selecionados = {}

for caminho in todos_arquivos:
    nome_sem_ext = os.path.splitext(os.path.basename(caminho))[0]
    ano = nome_sem_ext[-4:]
    if ano in anos_alvo:
        arquivos_selecionados[ano] = caminho

print(f"Arquivos encontrados ({len(arquivos_selecionados)}): {list(arquivos_selecionados.keys())}\n")

lista_dfs = []
for ano, caminho in sorted(arquivos_selecionados.items()):
    print(f"Lendo {ano} ({os.path.basename(caminho)})...")
    df_ano = pd.read_csv(caminho, dtype=str, encoding="utf-8-sig", keep_default_na=False)
    # Em alguns anos a coluna CONTADOR vem em minúsculas ("contador")
    df_ano.columns = [c.strip().upper() for c in df_ano.columns]
    df_ano["ANO_ARQUIVO"] = ano
    lista_dfs.append(df_ano)

df = pd.concat(lista_dfs, ignore_index=True)

# Padronização básica de strings vazias (sem alterar dados originais)
df = df.apply(lambda col: col.str.strip())
df.replace({"": np.nan, "nan": np.nan, "None": np.nan, "NULL": np.nan}, inplace=True)

print(f"\nTotal de registros carregados (2020-2024): {len(df):,}\n")

# Definição das chaves de verificação de duplicidade
# O SINASC não tem número da DN; CONTADOR é sequencial (diferente em toda linha) e fica de fora.
# Gêmeos têm mesma mãe, data e local: hora e peso ajudam a separar gêmeos de duplicados.
colunas_dados = [c for c in df.columns if c not in ["ANO_ARQUIVO", "CONTADOR"]]

criterios_duplicidade = {
    "1_Linha_100pct_Identica": colunas_dados,
    "2_Mesma_DN_SINASC": ["DTNASC", "HORANASC", "CODESTAB", "CODMUNNASC", "SEXO", "PESO",
                          "DTNASCMAE", "IDADEMAE", "CODMUNRES", "DTCADASTRO"],
    "3_Mesmo_RN_Forte": ["DTNASC", "HORANASC", "SEXO", "PESO", "DTNASCMAE", "CODMUNRES"],
    "4_Mesmo_RN_Amplo": ["DTNASC", "SEXO", "DTNASCMAE", "CODMUNRES"]
}

# Valida quais colunas de cada critério existem no DataFrame
criterios_validos = {}
for nome_crit, cols in criterios_duplicidade.items():
    cols_existentes = [c for c in cols if c in df.columns]
    if len(cols_existentes) >= 2:
        criterios_validos[nome_crit] = cols_existentes
    else:
        print(f"[Aviso] Critério '{nome_crit}' ignorado por falta de colunas na base.")


def calcular_metricas_duplicidade(df_sub: pd.DataFrame, cols_chave: list, ignorar_nulos_na_chave: bool = True) -> dict:
    """
    Calcula:
    - Registros_Envolvidos: total de linhas que fazem parte de algum grupo duplicado (keep=False)
    - Registros_Excedentes: quantas linhas seriam removidas se mantivéssemos 1 por grupo (keep='first')
    """
    total = len(df_sub)
    if total == 0:
        return {"Total_Registros": 0, "Registros_Envolvidos": 0, "Pct_Envolvidos (%)": 0.0,
                "Registros_Excedentes": 0, "Pct_Excedentes (%)": 0.0}

    # Para chaves de identificação, evita considerar dois registros com DTNASCMAE nulo como "mesmo RN"
    if ignorar_nulos_na_chave:
        df_valido = df_sub.dropna(subset=cols_chave)
    else:
        df_valido = df_sub

    mask_envolvidos = df_valido.duplicated(subset=cols_chave, keep=False)
    mask_excedentes = df_valido.duplicated(subset=cols_chave, keep="first")

    qtd_envolvidos = int(mask_envolvidos.sum())
    qtd_excedentes = int(mask_excedentes.sum())

    return {
        "Total_Registros": total,
        "Registros_Envolvidos": qtd_envolvidos,
        "Pct_Envolvidos (%)": round((qtd_envolvidos / total) * 100, 4),
        "Registros_Excedentes": qtd_excedentes,
        "Pct_Excedentes (%)": round((qtd_excedentes / total) * 100, 4)
    }


# Gerar Resumo Consolidado (2020-2024)
resumo_geral = []
for nome_crit, cols_chave in criterios_validos.items():
    ignorar_nulos = (nome_crit != "1_Linha_100pct_Identica")
    metricas = calcular_metricas_duplicidade(df, cols_chave, ignorar_nulos_na_chave=ignorar_nulos)
    resumo_geral.append({
        "Criterio_Analise": nome_crit,
        "Colunas_Utilizadas": ", ".join(cols_chave) if len(cols_chave) <= 10 else f"Todas as {len(cols_chave)} colunas",
        **metricas
    })

df_resumo_geral = pd.DataFrame(resumo_geral)

# Gerar Evolução de Duplicados por Ano
resumo_por_ano = []
for ano, df_ano in sorted(df.groupby("ANO_ARQUIVO")):
    for nome_crit, cols_chave in criterios_validos.items():
        ignorar_nulos = (nome_crit != "1_Linha_100pct_Identica")
        metricas = calcular_metricas_duplicidade(df_ano, cols_chave, ignorar_nulos_na_chave=ignorar_nulos)
        resumo_por_ano.append({
            "Ano": ano,
            "Criterio_Analise": nome_crit,
            **metricas
        })

df_resumo_ano = pd.DataFrame(resumo_por_ano)

# Tabela pivô para facilitar a leitura do grupo (% de registros excedentes por ano e critério)
df_pivot_ano = df_resumo_ano.pivot(
    index="Criterio_Analise",
    columns="Ano",
    values="Pct_Excedentes (%)"
).reset_index()

# Extrair Amostra dos Casos Duplicados (Critério 3 - Mesmo RN Forte) para inspeção visual do grupo
df_amostra_duplicados = pd.DataFrame()
if "3_Mesmo_RN_Forte" in criterios_validos:
    cols_c3 = criterios_validos["3_Mesmo_RN_Forte"]
    df_validos_c3 = df.dropna(subset=cols_c3).copy()
    mask_dup_c3 = df_validos_c3.duplicated(subset=cols_c3, keep=False)

    # Ordena pelas colunas da chave para os pares duplicados aparecerem um abaixo do outro no Excel
    df_amostra_duplicados = (
        df_validos_c3[mask_dup_c3]
        .sort_values(by=cols_c3 + ["ANO_ARQUIVO"])
        .head(500)  # Limita às primeiras 500 linhas para o Excel não ficar pesado
    )

# Exportar para um único Excel
with pd.ExcelWriter(arquivo_saida, engine="openpyxl") as writer:
    df_resumo_geral.to_excel(writer, sheet_name="1_Resumo_Consolidado", index=False)
    df_pivot_ano.to_excel(writer, sheet_name="2_Comparativo_Anual_Pct", index=False)
    df_resumo_ano.to_excel(writer, sheet_name="3_Detalhado_Por_Ano", index=False)
    if not df_amostra_duplicados.empty:
        df_amostra_duplicados.to_excel(writer, sheet_name="4_Amostra_Pares_Duplicados", index=False)

print("=== RESUMO CONSOLIDADO DE DUPLICIDADES (2020-2024) ===")
print(df_resumo_geral[["Criterio_Analise", "Total_Registros", "Registros_Envolvidos", "Registros_Excedentes", "Pct_Excedentes (%)"]].to_string(index=False))
print(f"\nRelatório completo salvo em: {arquivo_saida}")
