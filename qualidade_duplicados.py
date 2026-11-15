"""
Verificação de registros duplicados por critério, consolidada e por ano.
Mesma lógica de verificacao_duplicados.py, para SINASC ou SINAN.

Uso:
    python qualidade_duplicados.py sinasc                  # lê data/raw/
    python qualidade_duplicados.py sinan "C:/pasta/csv"    # lê outra pasta
"""

import os
import sys

import pandas as pd

from qualidade_comum import (COLUNAS_TECNICAS, PASTA_SAIDA_PADRAO, caminho_relatorio,
                             carregar_todos, ler_argumentos, periodo)


def calcular_metricas(df_sub, cols_chave, ignorar_nulos, gravidez_multipla):
    """
    Envolvidos  = linhas que fazem parte de algum grupo duplicado (keep=False)
    Excedentes  = linhas que seriam removidas mantendo 1 por grupo (keep='first')
    Gravidez múltipla (só SINASC) = dos envolvidos, quantos são gêmeos/trigêmeos
    """
    total = len(df_sub)
    df_valido = df_sub.dropna(subset=cols_chave) if ignorar_nulos else df_sub
    envolvidos = df_valido.duplicated(subset=cols_chave, keep=False)
    excedentes = df_valido.duplicated(subset=cols_chave, keep="first")
    m = {
        "Total_Registros": total,
        "Registros_Envolvidos": int(envolvidos.sum()),
        "Pct_Envolvidos (%)": round(envolvidos.sum() / total * 100, 4) if total else 0.0,
        "Registros_Excedentes": int(excedentes.sum()),
        "Pct_Excedentes (%)": round(excedentes.sum() / total * 100, 4) if total else 0.0,
    }
    if gravidez_multipla:
        col, cods = gravidez_multipla
        m["Envolvidos_Gravidez_Multipla"] = int(df_valido.loc[envolvidos, col].isin(cods).sum())
    return m


if __name__ == "__main__":
    base, pasta = ler_argumentos(sys.argv)
    os.makedirs(PASTA_SAIDA_PADRAO, exist_ok=True)
    per = periodo(base)

    df = pd.concat(carregar_todos(base, pasta).values(), ignore_index=True)
    print(f"\nTotal consolidado ({per}): {len(df):,}\n")

    colunas_dados = [c for c in df.columns if c not in COLUNAS_TECNICAS + base.EXCLUIR_DA_LINHA_IDENTICA]
    criterios = {}
    for nome, cols in base.CRITERIOS_DUPLICIDADE.items():
        cols = colunas_dados if cols is None else [c for c in cols if c in df.columns]
        faltando = set(base.CRITERIOS_DUPLICIDADE[nome] or []) - set(cols)
        if faltando:
            print(f"[Aviso] Critério '{nome}': colunas ausentes na base: {sorted(faltando)}")
        if len(cols) >= 2:
            criterios[nome] = cols

    def linha(nome, cols, df_sub):
        ignorar_nulos = base.CRITERIOS_DUPLICIDADE[nome] is not None
        return calcular_metricas(df_sub, cols, ignorar_nulos, base.GRAVIDEZ_MULTIPLA)

    resumo = pd.DataFrame([{
        "Criterio_Analise": nome,
        "Colunas_Utilizadas": ", ".join(cols) if base.CRITERIOS_DUPLICIDADE[nome] is not None
        else f"Todas as {len(cols)} colunas" + (f" (exceto {', '.join(base.EXCLUIR_DA_LINHA_IDENTICA)})"
                                                 if base.EXCLUIR_DA_LINHA_IDENTICA else ""),
        **linha(nome, cols, df)} for nome, cols in criterios.items()])

    por_ano = pd.DataFrame([{"Ano": ano, "Criterio_Analise": nome, **linha(nome, cols, df_ano)}
                            for ano, df_ano in sorted(df.groupby("ANO_ARQUIVO"))
                            for nome, cols in criterios.items()])
    pivot = por_ano.pivot(index="Criterio_Analise", columns="Ano", values="Pct_Excedentes (%)").reset_index()

    amostra = pd.DataFrame()
    if base.CRITERIO_AMOSTRA in criterios:
        cols = criterios[base.CRITERIO_AMOSTRA]
        val = df.dropna(subset=cols)
        amostra = val[val.duplicated(subset=cols, keep=False)].sort_values(cols + ["ANO_ARQUIVO"]).head(500)

    saida = caminho_relatorio(base, "Duplicados")
    with pd.ExcelWriter(saida, engine="openpyxl") as writer:
        resumo.to_excel(writer, sheet_name="1_Resumo_Consolidado", index=False)
        pivot.to_excel(writer, sheet_name="2_Comparativo_Anual_Pct", index=False)
        por_ano.to_excel(writer, sheet_name="3_Detalhado_Por_Ano", index=False)
        if not amostra.empty:
            amostra.to_excel(writer, sheet_name="4_Amostra_Pares_Duplicados", index=False)

    print(resumo.drop(columns="Colunas_Utilizadas").to_string(index=False))
    print(f"\nRelatório gerado em: {saida}")
