import os
import glob
import pandas as pd
import numpy as np

# Configurações de caminhos e filtro de anos
# Pasta de entrada dos arquivos SINAN
pasta_arquivos = os.path.join("data", "raw")

# Pasta de saída dos relatórios
pasta_saida = os.path.join("data", "outputs")

# Criar pasta de saída caso não exista
os.makedirs(pasta_saida, exist_ok=True)

# Caminho do relatório final
arquivo_saida = os.path.join(
    pasta_saida,
    "Relatorio_Analise_Nulos_SINAN_2020_2025.xlsx"
)

anos_alvo = ["20", "21", "22", "23", "24", "25"]

# Variáveis categóricas do SINAN onde o código '9' (ou '99') significa "Ignorado"
colunas_com_codigo_ignorado = [
    "CS_SEXO", "CS_GESTANT", "CS_RACA", "CS_ESCOL_N",
    "ANT_RACA", "ESCOLMAE", "ANT_PRE_NA", "ANTSIFIL_N",
    "LAB_PARTO", "LAB_CONF", "TRA_ESQUEM", "ANT_TRATAD",
    "LABC_SANGU", "LABC_IGG", "LABC_LIQUO", "LABC_TITUL",
    "LABC_EVIDE", "LABC_LIQ_1", "TRA_DIAG_T", "TRA_DIAG_C",
    "CLI_ICTERI", "CLI_RINITE", "CLI_ANEMIA", "CLI_ESPLEN",
    "HEPATO", "CLI_OSTEO", "LESOES", "CLI_OUTRO", "CLI_PSEUDO",
    "TRA_ESQU_1", "EVOLUCAO"
]

def gerar_relatorio_completude(df_base: pd.DataFrame) -> pd.DataFrame:
    """Calcula as métricas de nulos técnicos (NaN) e ignorados ('9') para um DataFrame."""
    total_registros = len(df_base)
    resultados = []

    for col in df_base.columns:
        if col in ["ABA_ORIGEM", "ANO_ARQUIVO"]:
            continue

        qtd_nulos_tecnicos = df_base[col].isna().sum()
        pct_nulos_tecnicos = (qtd_nulos_tecnicos / total_registros) * 100 if total_registros > 0 else 0

        # Verifica código '9' (e '99' caso apareça em campos de 2 dígitos como CS_ESCOL_N/ESCOLMAE)
        if col in colunas_com_codigo_ignorado:
            qtd_ignorados = df_base[col].isin(["9", "99"]).sum()
        else:
            qtd_ignorados = 0

        pct_ignorados = (qtd_ignorados / total_registros) * 100 if total_registros > 0 else 0

        # Perda total de informação útil = Nulo Técnico (NaN) + Ignorado ('9'/'99')
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
            "Qtd_Ignorado_Cod9": qtd_ignorados,
            "Pct_Ignorado_Cod9 (%)": round(pct_ignorados, 2),
            "Qtd_Perda_Total": qtd_perda_total,
            "Pct_Perda_Total (%)": round(pct_perda_total, 2),
            "Status_Qualidade": status
        })

    return pd.DataFrame(resultados).sort_values(by="Pct_Perda_Total (%)", ascending=False)


# Localizar e filtrar os arquivos pelos 2 últimos caracteres do nome (sem extensão)
todos_arquivos = sorted(glob.glob(os.path.join(pasta_arquivos, "*.xlsx")))
arquivos_selecionados = {}

for caminho in todos_arquivos:
    nome_sem_ext = os.path.splitext(os.path.basename(caminho))[0]
    
    # Ignora arquivos temporários do Excel (~$) e o próprio arquivo de saída
    if nome_sem_ext.startswith("~$") or "Relatorio_Analise_Nulos" in nome_sem_ext:
        continue

    sufixo_ano = nome_sem_ext[-2:]  # Extrai os dois últimos caracteres (ex: '20', '21', ..., '25')
    if sufixo_ano in anos_alvo:
        ano_completo = f"20{sufixo_ano}"
        arquivos_selecionados[ano_completo] = caminho

print(f"Arquivos selecionados ({len(arquivos_selecionados)}): {list(arquivos_selecionados.keys())}\n")

# Ler cada arquivo, limpar os dados e gerar relatórios individuais
dfs_por_ano = {}
relatorios_individuais = {}

for ano, caminho in sorted(arquivos_selecionados.items()):
    print(f"Processando {ano} -> {os.path.basename(caminho)}...")
    xls = pd.ExcelFile(caminho)
    
    lista_abas = []
    for aba in xls.sheet_names:
        df_aba = pd.read_excel(xls, sheet_name=aba, dtype=str)
        df_aba["ABA_ORIGEM"] = aba
        lista_abas.append(df_aba)
        
    df_ano = pd.concat(lista_abas, ignore_index=True)
    
    # Limpeza de espaços e padronização de nulos
    df_ano = df_ano.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
    df_ano.replace({"": np.nan, "nan": np.nan, "None": np.nan, "NULL": np.nan}, inplace=True)
    df_ano["ANO_ARQUIVO"] = ano
    
    dfs_por_ano[ano] = df_ano
    relatorios_individuais[ano] = gerar_relatorio_completude(df_ano)
    print(f"   Registros em {ano}: {len(df_ano):,}")

# Consolidar todos os anos (2020 a 2025)
df_consolidado = pd.concat(dfs_por_ano.values(), ignore_index=True)
print(f"\nTotal de registros consolidados (2020-2025): {len(df_consolidado):,}")

df_relatorio_consolidado = gerar_relatorio_completude(df_consolidado)

# Criar Matriz Comparativa Lado a Lado (% Perda Total por Ano vs Consolidado)
df_matriz_evolucao = df_relatorio_consolidado[["Variavel_DBF", "Pct_Perda_Total (%)"]].rename(
    columns={"Pct_Perda_Total (%)": "Consolidado_2020_2025 (%)"}
)

for ano, df_rel_ano in sorted(relatorios_individuais.items()):
    df_temp = df_rel_ano[["Variavel_DBF", "Pct_Perda_Total (%)"]].rename(
        columns={"Pct_Perda_Total (%)": f"Perda_{ano} (%)"}
    )
    df_matriz_evolucao = pd.merge(df_matriz_evolucao, df_temp, on="Variavel_DBF", how="outer")

# Exportar tudo para um único Excel com múltiplas abas
with pd.ExcelWriter(arquivo_saida, engine="openpyxl") as writer:
    # Aba 1: Resumo geral somando 2020 a 2025
    df_relatorio_consolidado.to_excel(writer, sheet_name="Consolidado_2020_2025", index=False)
    
    # Aba 2: Matriz lado a lado para comparar a evolução de nulos ano a ano
    df_matriz_evolucao.to_excel(writer, sheet_name="Matriz_Evolucao_Anual", index=False)
    
    # Abas 3 a 8: Um relatório individual para cada ano
    for ano, df_rel_ano in sorted(relatorios_individuais.items()):
        df_rel_ano.to_excel(writer, sheet_name=f"Ano_{ano}", index=False)

print(f"\nRelatório único gerado com sucesso em: {arquivo_saida}")