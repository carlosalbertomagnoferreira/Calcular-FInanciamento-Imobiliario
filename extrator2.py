import pdfplumber
import re
import pandas as pd

regex = re.compile(
    r"(\d{2}/\d{2}/\d{4})\s+"
    r"([\d.,]+)\s+"
    r"([\d.,]+)\s+"
    r"([\d.,]+)\s+"
    r"([\d.,]+)\s+"
    r"([\d.,]+)\s+"
    r"([\d.,]+)\s+"
    r"([\d.,]+)\s+"
    r"([\d.,]+)\s+"
    r"([\d.,]+)\s+"
    r"([\d.,]+)"
)

linhas = []

with pdfplumber.open("extrato319405086.pdf") as pdf:
    for pagina in pdf.pages:
        texto = pagina.extract_text()

        for linha in texto.split("\n"):
            m = regex.match(linha)

            if m:
                linhas.append(m.groups())

colunas = [
    "Data",
    "Saldo Devedor",
    "Correção Monetária",
    "Saldo Atualizado",
    "Prestação",
    "Capital",
    "Juros",
    "Acessórios",
    "Correção Prestação",
    "Encargos",
    "Valor Pago",
]

df = pd.DataFrame(linhas, columns=colunas)

df.to_excel("extrato.xlsx", index=False)

df.to_csv("extrato.csv", index=False, sep=";", decimal=",", encoding="utf-8-sig")


print(df)
