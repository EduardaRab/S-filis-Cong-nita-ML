"""
Análise de completude (nulos + ignorados) do SINASC, 2020 a 2024.
Mesma lógica de verificacao_nulos.py (SINAN), adaptada para os DNSP*.csv.

Uso:
    python verificacao_nulos_sinasc.py                 # lê data/raw/
    python verificacao_nulos_sinasc.py "C:/pasta/csv"  # lê outra pasta
"""

import os
import sys
import pandas as pd

from sinasc_comum import (
    ANOS_ALVO, CODIGOS_IGNORADO, COLUNAS_TECNICAS, PASTA_SAIDA_PADRAO,
    obter_pasta_dados, localizar_arquivos, ler_arquivo_sinasc,
)

pasta_arquivos = obter_pasta_dados(sys.argv)
pasta_saida = PASTA_SAIDA_PADRAO
os.makedirs(pasta_saida, exist_ok=True)

periodo = f"{ANOS_ALVO[0]}_{ANOS_ALVO[-1]}"
arquivo_saida = os.path.join(pasta_saida, f"Relatorio_Analise_Nulos_SINASC_{periodo}.xlsx")


def gerar_relatorio_completude(df_base: pd.DataFrame) -> pd.DataFrame:
    """Calcula nulos técnicos (NaN) e ignorados (código específico de cada variável)."""
    total_registros = len(df_base)
    resultados = []

    for col in df_base.columns:
        if col in COLUNAS_TECNICAS:
            continue

        qtd_nulos_tecnicos = int(df_base[col].isna().sum())
        pct_nulos_tecnicos = (qtd_nulos_tecnicos / total_registros) * 100 if total_registros > 0 else 0

        codigos = CODIGOS_IGNORADO.get(col, [])
        qtd_ignorados = int(df_base[col].isin(codigos).sum()) if codigos else 0
        pct_ignorados = (qtd_ignorados / total_registros) * 100 if total_registros > 0 else 0

        # Perda total de informação útil = Nulo Técnico (NaN) + Ignorado
        qtd_perda_total = qtd_nulos_tecnicos + qtd_ignorados
        pct_perda_total = (qtd_perda_total / total_registros) * 100 if total_registros > 0 else 0

        if pct_perda_total >= 50:
            status = "Crítico (>= 50% ausente/ignorado)"
        elif pct_perda_total >= 20:
            status = "Atenção (20% a 49.9%)"
        elif pct_perda_total > 0:
            status = "Aceitável (< 20%)"
        else:
            status = "Completo (0%)"

        resultados.append({
            "Variavel_DBF": col,
            "Codigo_Ignorado": ", ".join(codigos) if codigos else "-",
            "Total_Registros": total_registros,
            "Qtd_Nulos_NaN": qtd_nulos_tecnicos,
            "Pct_Nulos_NaN (%)": round(pct_nulos_tecnicos, 2),
            "Qtd_Ignorado": qtd_ignorados,
            "Pct_Ignorado (%)": round(pct_ignorados, 2),
            "Qtd_Perda_Total": qtd_perda_total,
            "Pct_Perda_Total (%)": round(pct_perda_total, 2),
            "Status_Qualidade": status,
        })

    return pd.DataFrame(resultados).sort_values(by="Pct_Perda_Total (%)", ascending=False)


arquivos_selecionados = localizar_arquivos(pasta_arquivos)
print(f"Arquivos selecionados ({len(arquivos_selecionados)}): {list(arquivos_selecionados.keys())}\n")
if not arquivos_selecionados:
    sys.exit(f"Nenhum DNSP*.csv de {ANOS_ALVO} encontrado em: {os.path.abspath(pasta_arquivos)}")

# Ler cada ano e gerar o relatório individual
dfs_por_ano = {}
relatorios_individuais = {}

for ano, caminho in sorted(arquivos_selecionados.items()):
    print(f"Processando {ano} -> {os.path.basename(caminho)}...")
    df_ano = ler_arquivo_sinasc(caminho, ano)
    dfs_por_ano[ano] = df_ano
    relatorios_individuais[ano] = gerar_relatorio_completude(df_ano)
    print(f"   Registros em {ano}: {len(df_ano):,}")

# Consolidar todos os anos
df_consolidado = pd.concat(dfs_por_ano.values(), ignore_index=True)
print(f"\nTotal de registros consolidados ({ANOS_ALVO[0]}-{ANOS_ALVO[-1]}): {len(df_consolidado):,}")

df_relatorio_consolidado = gerar_relatorio_completude(df_consolidado)

# Matriz comparativa lado a lado (% Perda Total por ano vs consolidado)
df_matriz_evolucao = df_relatorio_consolidado[["Variavel_DBF", "Pct_Perda_Total (%)"]].rename(
    columns={"Pct_Perda_Total (%)": f"Consolidado_{periodo} (%)"}
)
for ano, df_rel_ano in sorted(relatorios_individuais.items()):
    df_temp = df_rel_ano[["Variavel_DBF", "Pct_Perda_Total (%)"]].rename(
        columns={"Pct_Perda_Total (%)": f"Perda_{ano} (%)"}
    )
    df_matriz_evolucao = pd.merge(df_matriz_evolucao, df_temp, on="Variavel_DBF", how="left")

# Exportar tudo para um único Excel com múltiplas abas
with pd.ExcelWriter(arquivo_saida, engine="openpyxl") as writer:
    df_relatorio_consolidado.to_excel(writer, sheet_name=f"Consolidado_{periodo}", index=False)
    df_matriz_evolucao.to_excel(writer, sheet_name="Matriz_Evolucao_Anual", index=False)
    for ano, df_rel_ano in sorted(relatorios_individuais.items()):
        df_rel_ano.to_excel(writer, sheet_name=f"Ano_{ano}", index=False)

print(f"\nRelatório único gerado com sucesso em: {arquivo_saida}")
