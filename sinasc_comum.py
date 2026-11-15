"""
Configuração do SINASC (arquivos DNSP*.csv) para as análises de qualidade.

- Arquivos CSV, um por ano (DNSP2015.csv ... DNSP2024.csv); ano = 4 últimos caracteres.
- A coluna CONTADOR vem como "contador" (minúscula, 1ª posição) em 2015 e 2017;
  os nomes de coluna são normalizados para maiúsculas na leitura.
- O código de "Ignorado" muda por coluna: '9' em campos de 1 dígito, '99' em
  campos numéricos de 2 dígitos (ex.: em CONSPRENAT '9' = 9 consultas).
"""

import glob
import os

from qualidade_comum import ler_csv_texto

NOME = "SINASC"
DESCRICAO = "SINASC – Declarações de Nascido Vivo, mães residentes em SP (DNSP*.csv)"

# Mesmo recorte do SINAN (2020 em diante). O SINASC de 2025 ainda não foi publicado.
ANOS_ALVO = ["2020", "2021", "2022", "2023", "2024"]


def localizar_arquivos(pasta: str) -> dict:
    selecionados = {}
    for caminho in sorted(glob.glob(os.path.join(pasta, "*.csv"))):
        nome = os.path.splitext(os.path.basename(caminho))[0]
        if nome.upper().startswith("DN") and nome[-4:] in ANOS_ALVO:
            selecionados[nome[-4:]] = caminho
    return selecionados


def ler_arquivo(caminho: str, ano: str):
    return ler_csv_texto(caminho)


# ---------------------------------------------------------------- Código "Ignorado"
# Referência: "SINASC: Estrutura de 1996 a 2019 – Dicionário de Dados" (MS/SVS/CGIAE)
# https://diaad.s3.sa-east-1.amazonaws.com/sinasc/SINASC+-+Estrutura.pdf
#   DIC  = o código "Ignorado" está escrito no dicionário.
#   CONV = o dicionário não lista os valores do campo; usa-se a convenção do DATASUS
#          de 99 = ignorado em campos numéricos de 2 dígitos, conferida nos dados.
#   FORA = o código aparece nos dados mas não faz parte do domínio do dicionário.
DIC, CONV, FORA = "Dicionário", "Convenção DATASUS (não listado no dicionário)", "Fora do domínio do dicionário"

_MAPA = {
    "LOCNASC":    (["9"],      FORA),   # dicionário: 1 a 5, sem código de ignorado
    "IDADEMAE":   (["99"],     CONV),
    "ESTCIVMAE":  (["9"],      DIC),
    "ESCMAE":     (["9"],      DIC),
    "ESCMAE2010": (["9"],      DIC),
    "ESCMAEAGR1": (["09"],     DIC),    # 00-08 e 10-12 são níveis válidos
    "QTDFILVIVO": (["99"],     CONV),
    "QTDFILMORT": (["99"],     CONV),
    "QTDGESTANT": (["99"],     CONV),
    "QTDPARTNOR": (["99"],     CONV),
    "QTDPARTCES": (["99"],     CONV),
    "IDADEPAI":   (["99"],     CONV),
    "GESTACAO":   (["9"],      DIC),
    "GRAVIDEZ":   (["9"],      DIC),
    "PARTO":      (["9"],      DIC),
    "CONSULTAS":  (["9"],      DIC),
    "CONSPRENAT": (["99"],     CONV),   # '9' aqui = 9 consultas (valor válido)
    "MESPRENAT":  (["99"],     CONV),
    "TPMETESTIM": (["9"],      DIC),    # dicionário: 1, 2, 9; o '8' dos dados não consta
    "TPAPRESENT": (["9"],      DIC),
    "STTRABPART": (["9"],      DIC),    # 3 = não se aplica (válido)
    "STCESPARTO": (["9"],      DIC),    # 3 = não se aplica (válido)
    "TPNASCASSI": (["9"],      DIC),
    "TPROBSON":   (["11"],     CONV),   # 11 = não classificado por falta de informação
    "KOTELCHUCK": (["9"],      CONV),   # 9 = não classificado (informação insuficiente)
    "SEXO":       (["0", "I"], DIC),    # dicionário: 0 / I = ignorado
    "APGAR1":     (["99"],     CONV),   # dicionário: 00 a 10
    "APGAR5":     (["99"],     CONV),   # dicionário: 00 a 10
    "IDANOMAL":   (["9"],      DIC),
    # RACACOR e RACACORMAE: o dicionário não tem código de ignorado (1 a 5); só nulo técnico.
}
CODIGOS_IGNORADO = {v: c for v, (c, _) in _MAPA.items()}
FONTE_CODIGO = {v: f for v, (_, f) in _MAPA.items()}

# ---------------------------------------------------------------- Duplicidade
# O SINASC público não traz número da DN nem nome da mãe.
CRITERIOS_DUPLICIDADE = {
    "1_Linha_100pct_Identica": None,   # None = todas as colunas de dados
    "2_Mesma_DN_SINASC": ["DTNASC", "HORANASC", "CODESTAB", "CODMUNNASC", "SEXO", "PESO",
                          "DTNASCMAE", "IDADEMAE", "CODMUNRES", "DTCADASTRO"],
    "3_Mesmo_RN_Forte": ["DTNASC", "HORANASC", "SEXO", "PESO", "DTNASCMAE", "CODMUNRES"],
    "4_Mesmo_RN_Amplo": ["DTNASC", "SEXO", "DTNASCMAE", "CODMUNRES"],
}
CRITERIO_AMOSTRA = "3_Mesmo_RN_Forte"
EXCLUIR_DA_LINHA_IDENTICA = ["CONTADOR"]      # sequencial: diferente em toda linha
GRAVIDEZ_MULTIPLA = ("GRAVIDEZ", ["2", "3"])  # gêmeos compartilham mãe, data e local
