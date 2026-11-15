"""
Partes comuns às análises de qualidade (nulos e duplicados) do SINASC e do SINAN.

Cada base tem um módulo de configuração (sinasc_comum.py, sinan_comum.py) com a
mesma interface:

    NOME, DESCRICAO, ANOS_ALVO
    localizar_arquivos(pasta) -> {ano: caminho}
    ler_arquivo(caminho, ano) -> DataFrame (texto, nulos padronizados)
    CODIGOS_IGNORADO, FONTE_CODIGO
    CRITERIOS_DUPLICIDADE, CRITERIO_AMOSTRA
    EXCLUIR_DA_LINHA_IDENTICA      (colunas sequenciais que não entram no critério 1)
    GRAVIDEZ_MULTIPLA              ((coluna, códigos) ou None)
"""

import importlib
import os
import sys

import numpy as np
import pandas as pd

PASTA_ARQUIVOS_PADRAO = os.path.join("data", "raw")
PASTA_SAIDA_PADRAO = os.path.join("data", "outputs")
COLUNAS_TECNICAS = ["ANO_ARQUIVO", "ARQUIVO_ORIGEM"]
BASES = {"sinasc": "sinasc_comum", "sinan": "sinan_comum"}


def ler_argumentos(argv):
    """python script.py <sinasc|sinan> [pasta_dos_csv]  ->  (módulo da base, pasta)."""
    if len(argv) < 2 or argv[1].lower() not in BASES:
        sys.exit(f"Uso: python {os.path.basename(argv[0])} <sinasc|sinan> [pasta_dos_csv]")
    base = importlib.import_module(BASES[argv[1].lower()])
    pasta = argv[2] if len(argv) > 2 else PASTA_ARQUIVOS_PADRAO
    return base, pasta


def periodo(base) -> str:
    return f"{base.ANOS_ALVO[0]}_{base.ANOS_ALVO[-1]}"


def caminho_relatorio(base, tipo: str) -> str:
    """tipo = 'Nulos' ou 'Duplicados'."""
    nome = "Analise_Nulos" if tipo == "Nulos" else "Duplicados"
    return os.path.join(PASTA_SAIDA_PADRAO, f"Relatorio_{nome}_{base.NOME}_{periodo(base)}.xlsx")


def ler_csv_texto(caminho: str) -> pd.DataFrame:
    """Lê um CSV do DATASUS como texto, com nomes de coluna em maiúsculas e nulos padronizados."""
    df = pd.read_csv(caminho, dtype=str, encoding="utf-8-sig", keep_default_na=False)
    df.columns = [c.strip().upper() for c in df.columns]
    for col in df.columns:
        df[col] = df[col].str.strip()
    return df.replace({"": np.nan, "nan": np.nan, "None": np.nan, "NULL": np.nan})


def carregar_todos(base, pasta: str) -> dict:
    """Lê todos os arquivos da base no período. Retorna {ano: DataFrame}."""
    arquivos = base.localizar_arquivos(pasta)
    print(f"[{base.NOME}] Arquivos selecionados ({len(arquivos)}): {list(arquivos.keys())}\n")
    if not arquivos:
        sys.exit(f"Nenhum arquivo de {base.NOME} ({base.ANOS_ALVO}) encontrado em: {os.path.abspath(pasta)}")
    dfs = {}
    for ano, caminho in sorted(arquivos.items()):
        df = base.ler_arquivo(caminho, ano)
        df["ANO_ARQUIVO"] = ano
        df["ARQUIVO_ORIGEM"] = os.path.basename(caminho)
        dfs[ano] = df
        print(f"   {ano} ({os.path.basename(caminho)}): {len(df):,} registros")
    return dfs
