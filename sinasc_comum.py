"""
Utilitários comuns para as análises de qualidade do SINASC (arquivos DNSP*.csv).

Equivalente, para o SINASC, ao que os scripts verificacao_nulos.py e
verificacao_duplicados.py fazem para o SINAN. Diferenças principais em relação
ao SINAN:

- Os arquivos são CSV (um por ano, DNSP2015.csv ... DNSP2024.csv), não Excel.
- O ano vem nos 4 últimos caracteres do nome (DNSP2024 -> 2024).
- A coluna CONTADOR aparece como "contador" (minúscula, 1ª posição) em 2015 e
  2017; por isso os nomes de coluna são normalizados para maiúsculas.
- O código de "Ignorado" NÃO é o mesmo em todas as colunas: em campos de 1 dígito
  é '9', em campos de 2 dígitos costuma ser '99' (ex.: IDADEMAE, CONSPRENAT,
  MESPRENAT, APGAR1). Em CONSPRENAT, por exemplo, '9' significa 9 consultas,
  então não dá para usar a regra única "9 ou 99" do SINAN.
"""

import os
import glob
import pandas as pd
import numpy as np

# Pastas padrão (mesma estrutura do repositório). Pode ser sobrescrita pela
# variável de ambiente PASTA_DADOS_SINASC ou pelo 1º argumento da linha de comando.
PASTA_ARQUIVOS_PADRAO = os.path.join("data", "raw")
PASTA_SAIDA_PADRAO = os.path.join("data", "outputs")

# Mesmo recorte temporal usado na análise do SINAN (2020 em diante).
# O SINASC disponível vai só até 2024 (2025 ainda não publicado).
ANOS_ALVO = ["2020", "2021", "2022", "2023", "2024"]

# Colunas técnicas adicionadas pelo script (não fazem parte da base)
COLUNAS_TECNICAS = ["ANO_ARQUIVO", "ARQUIVO_ORIGEM"]

# Código(s) que significam "Ignorado" / "Não informado" em cada variável do SINASC.
#
# Referência: "SINASC: Estrutura de 1996 a 2019 – Dicionário de Dados" (MS/SVS/CGIAE)
# https://diaad.s3.sa-east-1.amazonaws.com/sinasc/SINASC+-+Estrutura.pdf
#
# Cada variável tem uma fonte (FONTE_CODIGO):
#   DIC   = o código "Ignorado" está escrito no dicionário.
#   CONV  = o dicionário não lista os valores do campo (só "Idade da mãe", "Número de
#           consultas" etc.); usa-se a convenção do DATASUS de 99 = ignorado em campos
#           numéricos de 2 dígitos, conferida nos dados (99 é impossível como valor real).
#   FORA  = o código aparece nos dados mas não faz parte do domínio do dicionário;
#           contado como informação perdida.
DIC, CONV, FORA = "Dicionário", "Convenção DATASUS (não listado no dicionário)", "Fora do domínio do dicionário"

_MAPA = {
    # variável:     (códigos,      fonte)
    "LOCNASC":    (["9"],        FORA),   # dicionário: 1 a 5, sem código de ignorado
    "IDADEMAE":   (["99"],       CONV),
    "ESTCIVMAE":  (["9"],        DIC),
    "ESCMAE":     (["9"],        DIC),
    "ESCMAE2010": (["9"],        DIC),
    "ESCMAEAGR1": (["09"],       DIC),    # 00-08 e 10-12 são níveis válidos
    "QTDFILVIVO": (["99"],       CONV),
    "QTDFILMORT": (["99"],       CONV),
    "QTDGESTANT": (["99"],       CONV),
    "QTDPARTNOR": (["99"],       CONV),
    "QTDPARTCES": (["99"],       CONV),
    "IDADEPAI":   (["99"],       CONV),
    "GESTACAO":   (["9"],        DIC),
    "GRAVIDEZ":   (["9"],        DIC),
    "PARTO":      (["9"],        DIC),
    "CONSULTAS":  (["9"],        DIC),
    "CONSPRENAT": (["99"],       CONV),   # '9' aqui = 9 consultas (valor válido)
    "MESPRENAT":  (["99"],       CONV),
    "TPMETESTIM": (["9"],        DIC),    # dicionário: 1, 2, 9; o '8' dos dados não consta
    "TPAPRESENT": (["9"],        DIC),
    "STTRABPART": (["9"],        DIC),    # 3 = não se aplica (válido)
    "STCESPARTO": (["9"],        DIC),    # 3 = não se aplica (válido)
    "TPNASCASSI": (["9"],        DIC),
    "TPROBSON":   (["11"],       CONV),   # 11 = não classificado por falta de informação
    "KOTELCHUCK": (["9"],        CONV),   # 9 = não classificado (informação insuficiente)
    "SEXO":       (["0", "I"],   DIC),    # dicionário: 0 / I = ignorado
    "APGAR1":     (["99"],       CONV),   # dicionário: 00 a 10
    "APGAR5":     (["99"],       CONV),   # dicionário: 00 a 10
    "IDANOMAL":   (["9"],        DIC),
    # RACACOR e RACACORMAE: o dicionário não tem código de ignorado (1 a 5); só nulo técnico.
}

CODIGOS_IGNORADO = {var: cod for var, (cod, _) in _MAPA.items()}
FONTE_CODIGO = {var: fonte for var, (_, fonte) in _MAPA.items()}


def obter_pasta_dados(argv) -> str:
    """Pasta dos CSVs: argumento da linha de comando > variável de ambiente > data/raw."""
    if len(argv) > 1:
        return argv[1]
    return os.environ.get("PASTA_DADOS_SINASC", PASTA_ARQUIVOS_PADRAO)


def localizar_arquivos(pasta_arquivos: str, anos_alvo=ANOS_ALVO) -> dict:
    """Retorna {ano: caminho} para os DNSP*.csv cujo ano (4 últimos caracteres) está em anos_alvo."""
    selecionados = {}
    for caminho in sorted(glob.glob(os.path.join(pasta_arquivos, "*.csv"))):
        nome_sem_ext = os.path.splitext(os.path.basename(caminho))[0]
        if not nome_sem_ext.upper().startswith("DN"):
            continue
        ano = nome_sem_ext[-4:]
        if ano in anos_alvo:
            selecionados[ano] = caminho
    return selecionados


def ler_arquivo_sinasc(caminho: str, ano: str) -> pd.DataFrame:
    """Lê um DNSP*.csv como texto, normaliza nomes de coluna e padroniza nulos."""
    df = pd.read_csv(caminho, dtype=str, encoding="utf-8-sig", keep_default_na=False)

    # 'contador' (2015, 2017) -> 'CONTADOR'; leitura sempre por nome, nunca por posição
    df.columns = [c.strip().upper() for c in df.columns]

    # Limpeza de espaços e padronização de nulos (mesma regra do SINAN)
    for col in df.columns:
        df[col] = df[col].str.strip()
    df = df.replace({"": np.nan, "nan": np.nan, "None": np.nan, "NULL": np.nan})

    df["ANO_ARQUIVO"] = ano
    df["ARQUIVO_ORIGEM"] = os.path.basename(caminho)
    return df
