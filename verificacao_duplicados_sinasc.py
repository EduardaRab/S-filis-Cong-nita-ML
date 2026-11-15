"""
Verificação de registros duplicados no SINASC, 2020 a 2024.
Mesma lógica de verificacao_duplicados.py (SINAN), adaptada para os DNSP*.csv.

O SINASC público não traz o número da DN nem o nome da mãe, então os critérios
usam a combinação de campos que identificam um nascimento: data/hora do
nascimento, estabelecimento, sexo, peso e data de nascimento da mãe.

Atenção a gêmeos: dois irmãos gêmeos têm a mesma mãe, data e local, e podem ter
mesmo sexo e (raramente) mesmo peso. Por isso os critérios 3 e 4 trazem também
quantos dos registros envolvidos são de gravidez múltipla (GRAVIDEZ 2 ou 3).

Uso:
    python verificacao_duplicados_sinasc.py                 # lê data/raw/
    python verificacao_duplicados_sinasc.py "C:/pasta/csv"  # lê outra pasta
"""

import os
import sys
import pandas as pd

from sinasc_comum import (
    ANOS_ALVO, COLUNAS_TECNICAS, PASTA_SAIDA_PADRAO,
    obter_pasta_dados, localizar_arquivos, ler_arquivo_sinasc,
)

pasta_arquivos = obter_pasta_dados(sys.argv)
pasta_saida = PASTA_SAIDA_PADRAO
os.makedirs(pasta_saida, exist_ok=True)

periodo = f"{ANOS_ALVO[0]}_{ANOS_ALVO[-1]}"
arquivo_saida = os.path.join(pasta_saida, f"Relatorio_Duplicados_SINASC_{periodo}.xlsx")

arquivos_selecionados = localizar_arquivos(pasta_arquivos)
print(f"Arquivos encontrados ({len(arquivos_selecionados)}): {list(arquivos_selecionados.keys())}\n")
if not arquivos_selecionados:
    sys.exit(f"Nenhum DNSP*.csv de {ANOS_ALVO} encontrado em: {os.path.abspath(pasta_arquivos)}")

lista_dfs = []
for ano, caminho in sorted(arquivos_selecionados.items()):
    print(f"Lendo {ano} ({os.path.basename(caminho)})...")
    lista_dfs.append(ler_arquivo_sinasc(caminho, ano))

df = pd.concat(lista_dfs, ignore_index=True)
del lista_dfs
print(f"\nTotal de registros carregados ({ANOS_ALVO[0]}-{ANOS_ALVO[-1]}): {len(df):,}\n")

# CONTADOR é um sequencial do arquivo (diferente em toda linha); se entrasse na
# comparação, nenhuma linha jamais seria "100% idêntica".
colunas_dados = [c for c in df.columns if c not in COLUNAS_TECNICAS + ["CONTADOR"]]

criterios_duplicidade = {
    "1_Linha_100pct_Identica": colunas_dados,
    "2_Mesma_DN_SINASC": ["DTNASC", "HORANASC", "CODESTAB", "CODMUNNASC", "SEXO", "PESO",
                          "DTNASCMAE", "IDADEMAE", "CODMUNRES", "DTCADASTRO"],
    "3_Mesmo_RN_Forte": ["DTNASC", "HORANASC", "SEXO", "PESO", "DTNASCMAE", "CODMUNRES"],
    "4_Mesmo_RN_Amplo": ["DTNASC", "SEXO", "DTNASCMAE", "CODMUNRES"],
}

criterios_validos = {}
for nome_crit, cols in criterios_duplicidade.items():
    cols_existentes = [c for c in cols if c in df.columns]
    if len(cols_existentes) >= 2:
        criterios_validos[nome_crit] = cols_existentes
    else:
        print(f"[Aviso] Critério '{nome_crit}' ignorado por falta de colunas na base.")


def calcular_metricas_duplicidade(df_sub: pd.DataFrame, cols_chave: list, ignorar_nulos_na_chave: bool = True) -> dict:
    """
    - Registros_Envolvidos: linhas que fazem parte de algum grupo duplicado (keep=False)
    - Registros_Excedentes: linhas que seriam removidas mantendo 1 por grupo (keep='first')
    - Envolvidos_Gravidez_Multipla: dos envolvidos, quantos são gêmeos/trigêmeos (GRAVIDEZ 2/3)
    """
    total = len(df_sub)
    if total == 0:
        return {"Total_Registros": 0, "Registros_Envolvidos": 0, "Pct_Envolvidos (%)": 0.0,
                "Registros_Excedentes": 0, "Pct_Excedentes (%)": 0.0,
                "Envolvidos_Gravidez_Multipla": 0}

    # Evita tratar dois registros com chave nula como "mesmo nascimento"
    df_valido = df_sub.dropna(subset=cols_chave) if ignorar_nulos_na_chave else df_sub

    mask_envolvidos = df_valido.duplicated(subset=cols_chave, keep=False)
    mask_excedentes = df_valido.duplicated(subset=cols_chave, keep="first")

    qtd_envolvidos = int(mask_envolvidos.sum())
    qtd_excedentes = int(mask_excedentes.sum())
    qtd_multipla = int(df_valido.loc[mask_envolvidos, "GRAVIDEZ"].isin(["2", "3"]).sum()) \
        if "GRAVIDEZ" in df_valido.columns else 0

    return {
        "Total_Registros": total,
        "Registros_Envolvidos": qtd_envolvidos,
        "Pct_Envolvidos (%)": round((qtd_envolvidos / total) * 100, 4),
        "Registros_Excedentes": qtd_excedentes,
        "Pct_Excedentes (%)": round((qtd_excedentes / total) * 100, 4),
        "Envolvidos_Gravidez_Multipla": qtd_multipla,
    }


# Resumo consolidado
resumo_geral = []
for nome_crit, cols_chave in criterios_validos.items():
    ignorar_nulos = (nome_crit != "1_Linha_100pct_Identica")
    metricas = calcular_metricas_duplicidade(df, cols_chave, ignorar_nulos_na_chave=ignorar_nulos)
    resumo_geral.append({
        "Criterio_Analise": nome_crit,
        "Colunas_Utilizadas": ", ".join(cols_chave) if len(cols_chave) <= 10
        else f"Todas as {len(cols_chave)} colunas (exceto CONTADOR)",
        **metricas,
    })
df_resumo_geral = pd.DataFrame(resumo_geral)

# Evolução por ano (duplicidade dentro de cada ano)
resumo_por_ano = []
for ano, df_ano in sorted(df.groupby("ANO_ARQUIVO")):
    for nome_crit, cols_chave in criterios_validos.items():
        ignorar_nulos = (nome_crit != "1_Linha_100pct_Identica")
        metricas = calcular_metricas_duplicidade(df_ano, cols_chave, ignorar_nulos_na_chave=ignorar_nulos)
        resumo_por_ano.append({"Ano": ano, "Criterio_Analise": nome_crit, **metricas})
df_resumo_ano = pd.DataFrame(resumo_por_ano)

df_pivot_ano = df_resumo_ano.pivot(
    index="Criterio_Analise", columns="Ano", values="Pct_Excedentes (%)"
).reset_index()

# Amostra dos pares duplicados (critério 3) para inspeção visual
df_amostra_duplicados = pd.DataFrame()
if "3_Mesmo_RN_Forte" in criterios_validos:
    cols_c3 = criterios_validos["3_Mesmo_RN_Forte"]
    df_validos_c3 = df.dropna(subset=cols_c3)
    mask_dup_c3 = df_validos_c3.duplicated(subset=cols_c3, keep=False)
    df_amostra_duplicados = (
        df_validos_c3[mask_dup_c3]
        .sort_values(by=cols_c3 + ["ANO_ARQUIVO"])
        .head(500)
    )

with pd.ExcelWriter(arquivo_saida, engine="openpyxl") as writer:
    df_resumo_geral.to_excel(writer, sheet_name="1_Resumo_Consolidado", index=False)
    df_pivot_ano.to_excel(writer, sheet_name="2_Comparativo_Anual_Pct", index=False)
    df_resumo_ano.to_excel(writer, sheet_name="3_Detalhado_Por_Ano", index=False)
    if not df_amostra_duplicados.empty:
        df_amostra_duplicados.to_excel(writer, sheet_name="4_Amostra_Pares_Duplicados", index=False)

print(f"=== RESUMO CONSOLIDADO DE DUPLICIDADES ({ANOS_ALVO[0]}-{ANOS_ALVO[-1]}) ===")
print(df_resumo_geral[["Criterio_Analise", "Total_Registros", "Registros_Envolvidos",
                       "Registros_Excedentes", "Pct_Excedentes (%)",
                       "Envolvidos_Gravidez_Multipla"]].to_string(index=False))
print(f"\nRelatório completo salvo em: {arquivo_saida}")
