import os
import glob
import pandas as pd
import numpy as np

# Configurações de caminhos e filtro de anos
# Pasta de entrada dos arquivos SINASC
pasta_arquivos = os.path.join("data", "raw")

# Pasta de saída dos relatórios
pasta_saida = os.path.join("data", "outputs")

# Criar pasta de saída caso não exista
os.makedirs(pasta_saida, exist_ok=True)

# Caminho do relatório final
arquivo_saida = os.path.join(
    pasta_saida,
    "Relatorio_Analise_Nulos_SINASC_2020_2024.xlsx"
)

anos_alvo = ["2020", "2021", "2022", "2023", "2024"]

# Código de "Ignorado" de cada variável do SINASC.
# Diferente do SINAN, o código muda por variável: em CONSPRENAT, por exemplo,
# '9' significa 9 consultas e o ignorado é '99'.
# Fonte: SINASC - Estrutura de 1996 a 2019 (dicionário de dados do Ministério da Saúde)
# https://diaad.s3.sa-east-1.amazonaws.com/sinasc/SINASC+-+Estrutura.pdf
codigos_ignorado = {
    "LOCNASC": ["9"], "ESTCIVMAE": ["9"], "ESCMAE": ["9"], "ESCMAE2010": ["9"],
    "GESTACAO": ["9"], "GRAVIDEZ": ["9"], "PARTO": ["9"], "CONSULTAS": ["9"],
    "TPMETESTIM": ["9"], "TPAPRESENT": ["9"], "STTRABPART": ["9"], "STCESPARTO": ["9"],
    "TPNASCASSI": ["9"], "KOTELCHUCK": ["9"], "IDANOMAL": ["9"],
    "SEXO": ["0", "I"],
    "ESCMAEAGR1": ["09"],
    "TPROBSON": ["11"],
    "IDADEMAE": ["99"], "IDADEPAI": ["99"], "QTDFILVIVO": ["99"], "QTDFILMORT": ["99"],
    "QTDGESTANT": ["99"], "QTDPARTNOR": ["99"], "QTDPARTCES": ["99"],
    "CONSPRENAT": ["99"], "MESPRENAT": ["99"], "APGAR1": ["99"], "APGAR5": ["99"],
}

def gerar_relatorio_completude(df_base: pd.DataFrame) -> pd.DataFrame:
    """Calcula as métricas de nulos técnicos (NaN) e ignorados para um DataFrame."""
    total_registros = len(df_base)
    resultados = []

    for col in df_base.columns:
        if col in ["ANO_ARQUIVO"]:
            continue

        qtd_nulos_tecnicos = df_base[col].isna().sum()
        pct_nulos_tecnicos = (qtd_nulos_tecnicos / total_registros) * 100 if total_registros > 0 else 0

        # Verifica o código de ignorado específico da variável
        if col in codigos_ignorado:
            qtd_ignorados = df_base[col].isin(codigos_ignorado[col]).sum()
        else:
            qtd_ignorados = 0

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
            "Total_Registros": total_registros,
            "Qtd_Nulos_NaN": qtd_nulos_tecnicos,
            "Pct_Nulos_NaN (%)": round(pct_nulos_tecnicos, 2),
            "Qtd_Ignorado": qtd_ignorados,
            "Pct_Ignorado (%)": round(pct_ignorados, 2),
            "Qtd_Perda_Total": qtd_perda_total,
            "Pct_Perda_Total (%)": round(pct_perda_total, 2),
            "Status_Qualidade": status
        })

    return pd.DataFrame(resultados).sort_values(by="Pct_Perda_Total (%)", ascending=False)


# Localizar e filtrar os arquivos pelos 4 últimos caracteres do nome (ex: DNSP2024)
todos_arquivos = sorted(glob.glob(os.path.join(pasta_arquivos, "DN*.csv")))
arquivos_selecionados = {}

for caminho in todos_arquivos:
    nome_sem_ext = os.path.splitext(os.path.basename(caminho))[0]
    ano = nome_sem_ext[-4:]
    if ano in anos_alvo:
        arquivos_selecionados[ano] = caminho

print(f"Arquivos selecionados ({len(arquivos_selecionados)}): {list(arquivos_selecionados.keys())}\n")

# Ler cada arquivo, limpar os dados e gerar relatórios individuais
dfs_por_ano = {}
relatorios_individuais = {}

for ano, caminho in sorted(arquivos_selecionados.items()):
    print(f"Processando {ano} -> {os.path.basename(caminho)}...")
    df_ano = pd.read_csv(caminho, dtype=str, encoding="utf-8-sig", keep_default_na=False)

    # Em alguns anos a coluna CONTADOR vem em minúsculas ("contador")
    df_ano.columns = [c.strip().upper() for c in df_ano.columns]

    # Limpeza de espaços e padronização de nulos
    df_ano = df_ano.apply(lambda col: col.str.strip())
    df_ano.replace({"": np.nan, "nan": np.nan, "None": np.nan, "NULL": np.nan}, inplace=True)
    df_ano["ANO_ARQUIVO"] = ano

    dfs_por_ano[ano] = df_ano
    relatorios_individuais[ano] = gerar_relatorio_completude(df_ano)
    print(f"   Registros em {ano}: {len(df_ano):,}")

# Consolidar todos os anos (2020 a 2024)
df_consolidado = pd.concat(dfs_por_ano.values(), ignore_index=True)
print(f"\nTotal de registros consolidados (2020-2024): {len(df_consolidado):,}")

df_relatorio_consolidado = gerar_relatorio_completude(df_consolidado)

# Criar Matriz Comparativa Lado a Lado (% Perda Total por Ano vs Consolidado)
df_matriz_evolucao = df_relatorio_consolidado[["Variavel_DBF", "Pct_Perda_Total (%)"]].rename(
    columns={"Pct_Perda_Total (%)": "Consolidado_2020_2024 (%)"}
)

for ano, df_rel_ano in sorted(relatorios_individuais.items()):
    df_temp = df_rel_ano[["Variavel_DBF", "Pct_Perda_Total (%)"]].rename(
        columns={"Pct_Perda_Total (%)": f"Perda_{ano} (%)"}
    )
    df_matriz_evolucao = pd.merge(df_matriz_evolucao, df_temp, on="Variavel_DBF", how="outer")

# Exportar tudo para um único Excel com múltiplas abas
with pd.ExcelWriter(arquivo_saida, engine="openpyxl") as writer:
    # Aba 1: Resumo geral somando 2020 a 2024
    df_relatorio_consolidado.to_excel(writer, sheet_name="Consolidado_2020_2024", index=False)

    # Aba 2: Matriz lado a lado para comparar a evolução de nulos ano a ano
    df_matriz_evolucao.to_excel(writer, sheet_name="Matriz_Evolucao_Anual", index=False)

    # Abas 3 a 7: Um relatório individual para cada ano
    for ano, df_rel_ano in sorted(relatorios_individuais.items()):
        df_rel_ano.to_excel(writer, sheet_name=f"Ano_{ano}", index=False)

print(f"\nRelatório único gerado com sucesso em: {arquivo_saida}")
