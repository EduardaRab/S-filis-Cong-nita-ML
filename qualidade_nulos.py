"""
Análise de completude (nulos técnicos + ignorados) por variável, consolidada e por ano.
Mesma lógica de verificacao_nulos.py, para SINASC ou SINAN.

Uso:
    python qualidade_nulos.py sinasc                  # lê data/raw/
    python qualidade_nulos.py sinan "C:/pasta/csv"    # lê outra pasta
"""

import os
import sys

import pandas as pd

from qualidade_comum import (COLUNAS_TECNICAS, PASTA_SAIDA_PADRAO, caminho_relatorio,
                             carregar_todos, ler_argumentos, periodo)


def gerar_relatorio_completude(df_base: pd.DataFrame, codigos_ignorado: dict) -> pd.DataFrame:
    total = len(df_base)
    resultados = []
    for col in df_base.columns:
        if col in COLUNAS_TECNICAS:
            continue
        qtd_nulos = int(df_base[col].isna().sum())
        codigos = codigos_ignorado.get(col, [])
        qtd_ign = int(df_base[col].isin(codigos).sum()) if codigos else 0
        qtd_perda = qtd_nulos + qtd_ign
        pct = lambda q: round(q / total * 100, 2) if total else 0.0
        pct_perda = pct(qtd_perda)
        if pct_perda >= 50:
            status = "Crítico (>= 50% ausente/ignorado)"
        elif pct_perda >= 20:
            status = "Atenção (20% a 49.9%)"
        elif pct_perda > 0:
            status = "Aceitável (< 20%)"
        else:
            status = "Completo (0%)"
        resultados.append({
            "Variavel_DBF": col,
            "Codigo_Ignorado": ", ".join(codigos) if codigos else "-",
            "Total_Registros": total,
            "Qtd_Nulos_NaN": qtd_nulos, "Pct_Nulos_NaN (%)": pct(qtd_nulos),
            "Qtd_Ignorado": qtd_ign, "Pct_Ignorado (%)": pct(qtd_ign),
            "Qtd_Perda_Total": qtd_perda, "Pct_Perda_Total (%)": pct_perda,
            "Status_Qualidade": status,
        })
    return pd.DataFrame(resultados).sort_values(by="Pct_Perda_Total (%)", ascending=False)


if __name__ == "__main__":
    base, pasta = ler_argumentos(sys.argv)
    os.makedirs(PASTA_SAIDA_PADRAO, exist_ok=True)
    per = periodo(base)

    dfs_por_ano = carregar_todos(base, pasta)
    relatorios_ano = {ano: gerar_relatorio_completude(df, base.CODIGOS_IGNORADO)
                      for ano, df in dfs_por_ano.items()}

    df_consolidado = pd.concat(dfs_por_ano.values(), ignore_index=True)
    print(f"\nTotal consolidado ({per}): {len(df_consolidado):,}")
    rel_consolidado = gerar_relatorio_completude(df_consolidado, base.CODIGOS_IGNORADO)

    # Matriz lado a lado (% perda total por ano vs consolidado). Colunas que só existem
    # em alguns anos (ex.: DT_NASC, só no SINAN 2023) ficam vazias nos demais anos.
    matriz = rel_consolidado[["Variavel_DBF", "Pct_Perda_Total (%)"]].rename(
        columns={"Pct_Perda_Total (%)": f"Consolidado_{per} (%)"})
    for ano, rel in sorted(relatorios_ano.items()):
        matriz = pd.merge(matriz, rel[["Variavel_DBF", "Pct_Perda_Total (%)"]].rename(
            columns={"Pct_Perda_Total (%)": f"Perda_{ano} (%)"}), on="Variavel_DBF", how="left")

    saida = caminho_relatorio(base, "Nulos")
    with pd.ExcelWriter(saida, engine="openpyxl") as writer:
        rel_consolidado.to_excel(writer, sheet_name=f"Consolidado_{per}", index=False)
        matriz.to_excel(writer, sheet_name="Matriz_Evolucao_Anual", index=False)
        for ano, rel in sorted(relatorios_ano.items()):
            rel.to_excel(writer, sheet_name=f"Ano_{ano}", index=False)
    print(f"Relatório gerado em: {saida}")
