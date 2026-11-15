"""
Configuração do SINAN – Sífilis Congênita (arquivos SIFCBR*.csv) para as análises de qualidade.

Mesma análise de verificacao_nulos.py / verificacao_duplicados.py (Eduarda), com
três ajustes para rodar nos CSVs do projeto:

1. Leitura: CSV (SIFCBR20.csv ... SIFCBR25.csv) em vez de .xlsx; ano = "20" + 2 últimos caracteres.
2. Código "Ignorado" das escolaridades (ESCOLMAE, CS_ESCOL_N): o valor vem com zero à
   esquerda ('09'). A regra original ('9' ou '99') não pegava esses registros.
   CS_SEXO usa 'I' (Ignorado), que a regra original também não pegava.
3. Duplicidade: os CSVs não têm NU_NOTIFIC nem ID_UNIDADE, e DT_NASC só existe em 2023.
   As chaves foram trocadas por colunas presentes em todos os anos (ver CRITERIOS_DUPLICIDADE).
"""

import glob
import os

from qualidade_comum import ler_csv_texto

NOME = "SINAN"
DESCRICAO = "SINAN – Sífilis Congênita, notificações do Brasil inteiro (SIFCBR*.csv)"

# Mesmo recorte da análise original (2020 a 2025; 2025 é ano parcial).
ANOS_ALVO = ["2020", "2021", "2022", "2023", "2024", "2025"]


def localizar_arquivos(pasta: str) -> dict:
    selecionados = {}
    for caminho in sorted(glob.glob(os.path.join(pasta, "*.csv"))):
        nome = os.path.splitext(os.path.basename(caminho))[0]
        if nome.upper().startswith("SIFC") and f"20{nome[-2:]}" in ANOS_ALVO:
            selecionados[f"20{nome[-2:]}"] = caminho
    return selecionados


def ler_arquivo(caminho: str, ano: str):
    return ler_csv_texto(caminho)


# ---------------------------------------------------------------- Código "Ignorado"
ORIG = "Análise original do SINAN (código 9)"
AJUSTE = "Ajuste: código com zero à esquerda / letra"

# Mesma lista de colunas da análise original, com código 9 ...
_COLUNAS_COD9 = [
    "CS_GESTANT", "CS_RACA", "ANT_RACA", "ANT_PRE_NA", "ANTSIFIL_N",
    "LAB_PARTO", "LAB_CONF", "TRA_ESQUEM", "ANT_TRATAD",
    "LABC_SANGU", "LABC_IGG", "LABC_LIQUO", "LABC_TITUL",
    "LABC_EVIDE", "LABC_LIQ_1", "TRA_DIAG_T", "TRA_DIAG_C",
    "CLI_ICTERI", "CLI_RINITE", "CLI_ANEMIA", "CLI_ESPLEN",
    "HEPATO", "CLI_OSTEO", "LESOES", "CLI_OUTRO", "CLI_PSEUDO",
    "TRA_ESQU_1", "EVOLUCAO",
]
CODIGOS_IGNORADO = {c: ["9"] for c in _COLUNAS_COD9}
FONTE_CODIGO = {c: ORIG for c in _COLUNAS_COD9}

# ... e os campos em que o código não é '9'.
CODIGOS_IGNORADO.update({
    "CS_SEXO": ["I"],               # M / F / I (Ignorado)
    "ESCOLMAE": ["09", "9"],        # 00-08 níveis; 09 = Ignorado; 10 = Não se aplica
    "CS_ESCOL_N": ["09", "9"],      # idem (o caso é a criança: quase tudo é 10)
})
FONTE_CODIGO.update({"CS_SEXO": AJUSTE, "ESCOLMAE": AJUSTE, "CS_ESCOL_N": AJUSTE})

# ---------------------------------------------------------------- Duplicidade
CRITERIOS_DUPLICIDADE = {
    "1_Linha_100pct_Identica": None,   # None = todas as colunas de dados
    # Substitui "Mesma_Ficha_SINAN" (NU_NOTIFIC, ID_UNIDADE não existem nos CSVs)
    "2_Mesma_Notificacao": ["DT_NOTIFIC", "ID_MUNICIP", "DT_DIAG", "NU_IDADE_N", "CS_SEXO",
                            "ID_MN_RESI", "ANT_IDADE", "ESCOLMAE"],
    # DT_NASC (só em 2023) trocado por DT_DIAG, presente em todos os anos
    "3_Mesmo_Paciente_Forte": ["DT_DIAG", "CS_SEXO", "CS_RACA", "ID_MN_RESI", "ANT_IDADE", "ESCOLMAE"],
    "4_Mesmo_Paciente_Amplo": ["DT_DIAG", "CS_SEXO", "ID_MN_RESI", "ANT_IDADE"],
}
CRITERIO_AMOSTRA = "3_Mesmo_Paciente_Forte"
EXCLUIR_DA_LINHA_IDENTICA = []
GRAVIDEZ_MULTIPLA = None   # o SINAN não informa gravidez múltipla
