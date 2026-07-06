"""
Consulta de Estruturas Elétricas - Neoenergia Elektro
DIS-NOR-013 | DIS-NOR-014 | DIS-NOR-018

Usa os 3 PDFs originais de cada norma separadamente (PDF_PATHS),
evitando o problema de página trocada que ocorria com o PDF resumo combinado.
Coloque os arquivos DIS-NOR-013.pdf, DIS-NOR-014.pdf e DIS-NOR-018.pdf
na mesma pasta deste script.

Para rodar: streamlit run app_estruturas.py
"""

import io, subprocess, tempfile, os, glob
import streamlit as st
from PIL import Image

PDF_PATHS = {
    "DIS-NOR-013": "DIS-NOR-013.pdf",
    "DIS-NOR-014": "DIS-NOR-014.pdf",
    "DIS-NOR-018": "DIS-NOR-018.pdf",
}
DPI = 150

# ─────────────────────────────────────────────────────────────────
# MAPA DE ESTRUTURAS  {código_exibido: (página_no_PDF_da_norma, título_completo, norma)}
# A página agora se refere ao PDF ORIGINAL de cada norma (PDF_PATHS[norma]),
# e não a um arquivo combinado. Os números foram extraídos e conferidos
# diretamente do conteúdo de cada PDF (evita o erro de página trocada).
# ─────────────────────────────────────────────────────────────────
ESTRUTURAS = {
    # ── DIS-NOR-013 ─────────────────────────────────────────────
    "AT Condutor Ext (013)": (159, "Est.40 – Aterramento com Condutor Externo", "DIS-NOR-013"),
    "AT Condutor Int (013)": (162, "Est.41 – Aterramento com Condutor Interno", "DIS-NOR-013"),
    "B3.CE3": (120, "Est.27 – B3.CE3", "DIS-NOR-013"),
    "B3.CE3 SUI": (123, "Est.28 – B3.CE3 SUI", "DIS-NOR-013"),
    "Bifásica CF": (175, "Est.45 – Bifásica para Instalação de Chaves", "DIS-NOR-013"),
    "Bifásica Derivação": (173, "Est.43 – Bifásicas de Derivação", "DIS-NOR-013"),
    "Bifásica Para-raios": (176, "Est.46 – Bifásica para Instalação de Para-raios", "DIS-NOR-013"),
    "Bifásica TR Fim Rede": (178, "Est.48 – Bifásica TR em Fim de Rede", "DIS-NOR-013"),
    "Bifásica TR sem CF": (179, "Est.49 – Bifásica TR sem Chaves Fusíveis", "DIS-NOR-013"),
    "Bifásica TR sob Rede": (177, "Est.47 – Bifásica TR sob a Rede", "DIS-NOR-013"),
    "Bifásicas Básicas": (172, "Est.42 – Estruturas Bifásicas Básicas", "DIS-NOR-013"),
    "Bifásica Transição": (174, "Est.44 – Bifásicas de Transição de Redes", "DIS-NOR-013"),
    "CE1": (42, "Est.1 – CE1", "DIS-NOR-013"),
    "CE1A": (45, "Est.2 – CE1A", "DIS-NOR-013"),
    "CE1A-PU": (48, "Est.3 – CE1A-PU", "DIS-NOR-013"),
    "CE2": (57, "Est.6 – CE2", "DIS-NOR-013"),
    "CE2 DS": (105, "Est.22 – CE2 DS", "DIS-NOR-013"),
    "CE2 PR": (132, "Est.31 – CE2 PR", "DIS-NOR-013"),
    "CE2 TR": (147, "Est.36 – CE2 TR", "DIS-NOR-013"),
    "CE2-CE3": (93, "Est.18 – CE2-CE3", "DIS-NOR-013"),
    "CE2-CE3 CF": (96, "Est.19 – CE2-CE3 CF", "DIS-NOR-013"),
    "CE2-CE3 CF LP": (99, "Est.20 – CE2-CE3 CF LP", "DIS-NOR-013"),
    "CE2-N3 CF": (102, "Est.21 – CE2-N3 CF", "DIS-NOR-013"),
    "CE2-PU": (60, "Est.7 – CE2-PU", "DIS-NOR-013"),
    "CE2.3": (87, "Est.16 – CE2.3", "DIS-NOR-013"),
    "CE2.CE3": (90, "Est.17 – CE2.CE3", "DIS-NOR-013"),
    "CE3": (69, "Est.10 – CE3", "DIS-NOR-013"),
    "CE3 DS": (108, "Est.23 – CE3 DS", "DIS-NOR-013"),
    "CE3 TR": (150, "Est.37 – CE3 TR", "DIS-NOR-013"),
    "CE3 TRSC": (153, "Est.38 – CE3 TRSC", "DIS-NOR-013"),
    "CE3-CE3": (81, "Est.14 – CE3-CE3", "DIS-NOR-013"),
    "CE3-I": (126, "Est.29 – CE3-I", "DIS-NOR-013"),
    "CE3-I SUI": (129, "Est.30 – CE3-I SUI", "DIS-NOR-013"),
    "CE3-PU": (72, "Est.11 – CE3-PU", "DIS-NOR-013"),
    "CE3PU-CE3PU": (84, "Est.15 – CE3PU-CE3PU", "DIS-NOR-013"),
    "CE4": (75, "Est.12 – CE4", "DIS-NOR-013"),
    "CE4 CF": (135, "Est.32 – CE4 CF", "DIS-NOR-013"),
    "CE4 CF SAH": (138, "Est.33 – CE4 CF SAH", "DIS-NOR-013"),
    "CE4 SUH": (141, "Est.34 – CE4 SUH", "DIS-NOR-013"),
    "CE4 SUI": (144, "Est.35 – CE4 SUI", "DIS-NOR-013"),
    "CE4 TR": (156, "Est.39 – CE4 TR", "DIS-NOR-013"),
    "CE4-PU": (78, "Est.13 – CE4-PU", "DIS-NOR-013"),
    "CEJ1": (51, "Est.4 – CEJ1", "DIS-NOR-013"),
    "CEJ1 SAH": (54, "Est.5 – CEJ1 SAH", "DIS-NOR-013"),
    "CEJ2": (63, "Est.8 – CEJ2", "DIS-NOR-013"),
    "CEJ2 SAH": (66, "Est.9 – CEJ2 SAH", "DIS-NOR-013"),
    "Monofásicas Básicas": (180, "Est.50 – Estruturas Monofásicas Básicas", "DIS-NOR-013"),
    "Monofásicas Derivação": (181, "Est.51 – Monofásicas de Derivação", "DIS-NOR-013"),
    "N3.CE3": (111, "Est.24 – N3.CE3", "DIS-NOR-013"),
    "N3.CE3 SUH": (114, "Est.25 – N3.CE3 SUH", "DIS-NOR-013"),
    "N3.CE3 SUI": (117, "Est.26 – N3.CE3 SUI", "DIS-NOR-013"),
    # ── DIS-NOR-014 ─────────────────────────────────────────────
    "AT Condutor Ext (014)": (34, "Est.18 – Aterramento: Condutor Externo", "DIS-NOR-014"),
    "AT Condutor Int (014)": (35, "Est.19 – Aterramento: Condutor Interno", "DIS-NOR-014"),
    "CAB": (32, "Est.16 – CAB – Cruzamento Aéreo Multiplexado", "DIS-NOR-014"),
    "FLABIT": (17, "Est.3 – FLABIT", "DIS-NOR-014"),
    "FLABIDM": (20, "Est.6 – FLABIDM", "DIS-NOR-014"),
    "FLABIDT": (19, "Est.5 – FLABIDT", "DIS-NOR-014"),
    "FLABIM": (18, "Est.4 – FLABIM", "DIS-NOR-014"),
    "FLBIM": (22, "Est.8 – FLBIM", "DIS-NOR-014"),
    "FLBIM NI": (24, "Est.10 – FLBIM NI", "DIS-NOR-014"),
    "FLBIT": (21, "Est.7 – FLBIT", "DIS-NOR-014"),
    "FLBIT NI": (23, "Est.9 – FLBIT NI", "DIS-NOR-014"),
    "IBI": (33, "Est.17 – IBI – Interligação Nu/Multiplexado", "DIS-NOR-014"),
    "IT-R": (37, "Est.21 – IT-R", "DIS-NOR-014"),
    "ITF-R": (38, "Est.22 – ITF-R", "DIS-NOR-014"),
    "LCM": (36, "Est.20 – LCM – Ligação Consumidores Multiderivações", "DIS-NOR-014"),
    "SAB": (31, "Est.15 – SAB – Seccionamento Aéreo", "DIS-NOR-014"),
    "SDBIM": (27, "Est.12 – SDBIM", "DIS-NOR-014"),
    "SDBIT": (25, "Est.11 – SDBIT", "DIS-NOR-014"),
    "SDANI": (29, "Est.13 – SDANI", "DIS-NOR-014"),
    "SMBI": (16, "Est.2 – SMBI", "DIS-NOR-014"),
    "SPBI": (30, "Est.14 – SPBI", "DIS-NOR-014"),
    "STBI": (15, "Est.1 – STBI", "DIS-NOR-014"),
    # ── DIS-NOR-018 ─────────────────────────────────────────────
    "AT Descida Ext (018)": (172, "Est.109 – Aterramento Primária Condutor Externo", "DIS-NOR-018"),
    "AT Descida Int (018)": (173, "Est.110 – Aterramento Primária Condutor Interno", "DIS-NOR-018"),
    "B1": (31, "Est.17 – B1", "DIS-NOR-018"),
    "B3 (018)": (32, "Est.18 – B3", "DIS-NOR-018"),
    "B4": (33, "Est.19 – B4", "DIS-NOR-018"),
    "CFU 1º NÍVEL": (34, "Est.20 – CFU 1º Nível", "DIS-NOR-018"),
    "ESTAI CONTRAPOSTE": (37, "Est.23 – Estaiamento de Contraposte", "DIS-NOR-018"),
    "ESTAI NORMAL": (35, "Est.21 – Estai em Terreno Normal", "DIS-NOR-018"),
    "ESTAI ROCHA": (36, "Est.22 – Estai em Rochas e Pântanos", "DIS-NOR-018"),
    "HTC": (50, "Est.34 – HTC", "DIS-NOR-018"),
    "HTC FIM REDE": (51, "Est.35 – HTC Fim de Rede", "DIS-NOR-018"),
    "HTE": (48, "Est.32 – HTE", "DIS-NOR-018"),
    "HTE FIM REDE": (49, "Est.33 – HTE Fim de Rede", "DIS-NOR-018"),
    "HTC-1 Deriv N3": (162, "Est.103 – Derivação HTC-1 N3", "DIS-NOR-018"),
    "HTC-2 Deriv N3": (164, "Est.104 – Derivação HTC-2 N3", "DIS-NOR-018"),
    "HTE-1 Deriv N3": (158, "Est.101 – Derivação HTE-1 N3", "DIS-NOR-018"),
    "HTE-2 Deriv N3": (160, "Est.102 – Derivação HTE-2 N3", "DIS-NOR-018"),
    "HTE-2XN3": (56, "Est.40 – HTE-2XN3", "DIS-NOR-018"),
    "HTE-N3": (54, "Est.38 – HTE-N3", "DIS-NOR-018"),
    "HTC-2XN3": (57, "Est.41 – HTC-2XN3", "DIS-NOR-018"),
    "HTC-N3": (55, "Est.39 – HTC-N3", "DIS-NOR-018"),
    "LDE": (52, "Est.36 – LDE", "DIS-NOR-018"),
    "M1-N2 FR Chaves": (58, "Est.42 – M1-N2 Fim de Rede com Chaves Fusíveis", "DIS-NOR-018"),
    "M1-N3": (53, "Est.37 – M1-N3", "DIS-NOR-018"),
    "M1-N3 FR Chaves": (59, "Est.43 – M1-N3 Fim de Rede com Chaves Fusíveis", "DIS-NOR-018"),
    "M-N2BFR": (197, "Est.125 – Derivação M-N2BFR", "DIS-NOR-018"),
    "M-N3B": (199, "Est.126 – Derivação M-N3B", "DIS-NOR-018"),
    "N1": (16, "Est.6 – N1", "DIS-NOR-018"),
    "N1-TT": (21, "Est.11 – N1-TT", "DIS-NOR-018"),
    "N3 (018)": (17, "Est.7 – N3", "DIS-NOR-018"),
    "N3-N3 (018)": (19, "Est.9 – N3-N3", "DIS-NOR-018"),
    "N3-TT": (23, "Est.12 – N3-TT", "DIS-NOR-018"),
    "N3-TT-SOB": (26, "Est.13 – N3-TT-SOB", "DIS-NOR-018"),
    "N4": (18, "Est.8 – N4", "DIS-NOR-018"),
    "N4 COM CRUZETA": (44, "Est.28 – N4 com Cruzeta de Ferro", "DIS-NOR-018"),
    "N4-CFU": (28, "Est.14 – N4-CFU", "DIS-NOR-018"),
    "N4-N3 (018)": (20, "Est.10 – N4-N3", "DIS-NOR-018"),
    "N4-N3-CFU": (29, "Est.15 – N4-N3-CFU", "DIS-NOR-018"),
    "PARA-RAIOS 2ºNÍV": (38, "Est.24 – Para-raios em 2º Nível", "DIS-NOR-018"),
    "PT Est.M1": (174, "Est.111 – Posto de Transformação Estrutura M1", "DIS-NOR-018"),
    "PT Est.N3": (176, "Est.112 – Posto de Transformação Estrutura N3", "DIS-NOR-018"),
    "PT Est.N3 FimRede": (178, "Est.113 – Posto de Transformação N3 Fim de Rede", "DIS-NOR-018"),
    "PT Est.U1": (190, "Est.120 – Posto de Transformação Estrutura U1", "DIS-NOR-018"),
    "PT N3 2+ Clientes": (121, "Est.79 – PT Ligação 2 ou Mais Clientes", "DIS-NOR-018"),
    "PT N3 sem Chaves": (117, "Est.77 – PT N3 sem Chaves", "DIS-NOR-018"),
    "PT N3 sem Chaves 2": (119, "Est.78 – PT N3 sem Chaves (var.2)", "DIS-NOR-018"),
    "PT N3 com Chaves": (115, "Est.76 – PT N3 com Chaves", "DIS-NOR-018"),
    "TE": (30, "Est.16 – TE", "DIS-NOR-018"),
    "TE FIM REDE": (47, "Est.31 – TE Fim de Rede", "DIS-NOR-018"),
    "U1": (11, "Est.1 – U1", "DIS-NOR-018"),
    "U1-U3 c/Chaves": (182, "Est.116 – U1-U3 Ramal com Chaves", "DIS-NOR-018"),
    "U1-U3 s/Chaves": (181, "Est.115 – U1-U3 Ramal sem Chaves", "DIS-NOR-018"),
    "U2": (12, "Est.2 – U2", "DIS-NOR-018"),
    "U3": (13, "Est.3 – U3", "DIS-NOR-018"),
    "U3-3": (14, "Est.4 – U3-3", "DIS-NOR-018"),
    "U4": (15, "Est.5 – U4", "DIS-NOR-018"),
}

# ─────────────────────────────────────────────────────────────────
# BANCO DE NOTAS (Exemplos extraídos do novo PDF)
# ─────────────────────────────────────────────────────────────────
NOTAS_ESTRUTURAS = {
    "AT Condutor Ext (013)": [
        "A estrutura tipo AT Condutor Externo é utilizada para aterramento de condutor externo;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "AT Condutor Int (013)": [
        "A estrutura tipo AT Condutor Interno é utilizada para aterramento de condutor interno;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "B3.CE3": [
        "A estrutura tipo B3.CE3 é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "B3.CE3 SUI": [
        "A estrutura tipo B3.CE3 SUI é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "Bifásica CF": [
        "A estrutura tipo Bifásica CF é utilizada para instalação de chaves fusíveis;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "Bifásica Derivação": [
        "A estrutura tipo Bifásica Derivação é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "Bifásica Para-raios": [
        "A estrutura tipo Bifásica Para-raios é utilizada para instalação de para-raios;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "Bifásica TR Fim Rede": [
        "A estrutura tipo Bifásica TR Fim Rede é utilizada para instalação de transformadores em fim de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "Bifásica TR sem CF": [
        "A estrutura tipo Bifásica TR sem CF é utilizada para instalação de transformadores sem chaves fusíveis;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "Bifásica TR sob Rede": [
        "A estrutura tipo Bifásica TR sob Rede é utilizada para instalação de transformadores sob a rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "Bifásicas Básicas": [
        "As estruturas tipo Bifásicas Básicas são utilizadas em redes bifásicas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "Bifásica Transição": [
        "A estrutura tipo Bifásica Transição é utilizada em transições de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE1": [
        "A estrutura tipo CE1 é utilizada em tangentes e deflexões da rede até 6º;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE1A": [
        "A estrutura tipo CE1A é utilizada, a cada 200 m de rede, em longos trechos com várias estruturas tipo CE1;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE1A-PU": [
        "A estrutura tipo CE1A-PU é utilizada, a cada 200 m de rede, em longos trechos com várias estruturas tipo CE1;",
        "Esta estrutura deve ser utilizada preferencialmente em postes já instalados onde há necessidade de elevação do nível da rede primária, como por exemplo em circuitos duplos;",
        "Deve ser respeitada as distancias de segurança estabelecidas neste normativo;",
        "Esta estrutura não se aplica em redes de 34,5 kV.",
        "A Estrutura CE1A-PU possibilita a elevar a altura da rede em 0,5 m quando comparada com a CE1A."
    ],
    "CE2": [
        "A estrutura tipo CE2 é utilizada nos casos de deflexão da rede de 7º à 60º para cabos de seções 35 mm² e 70 mm² e 7º à 45º para cabos de seções 185 mm² e 240 mm²;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE2 DS": [
        "A estrutura tipo CE2 DS é utilizada em derivações subterrâneas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE2 PR": [
        "A estrutura tipo CE2 PR é utilizada para instalação de para-raios;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE2 TR": [
        "A estrutura tipo CE2 TR é utilizada para instalação de transformadores;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE2-CE3": [
        "A estrutura tipo CE2-CE3 é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE2-CE3 CF": [
        "A estrutura tipo CE2-CE3 CF é utilizada em derivações de rede com chaves fusíveis;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE2-CE3 CF LP": [
        "A estrutura tipo CE2-CE3 CF LP é utilizada em derivações de rede com chaves fusíveis e para-raios;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE2-N3 CF": [
        "A estrutura tipo CE2-N3 CF é utilizada em derivações de rede com chaves fusíveis;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE2-PU": [
        "A estrutura tipo CE2-PU é utilizada em tangentes e deflexões da rede até 6º;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE2.3": [
        "A estrutura tipo CE2.3 é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE2.CE3": [
        "A estrutura tipo CE2.CE3 é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE3": [
        "A estrutura tipo CE3 é utilizada em fim de rede e em ângulos de deflexão de 60º a 90º;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE3 DS": [
        "A estrutura tipo CE3 DS é utilizada em derivações subterrâneas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE3 TR": [
        "A estrutura tipo CE3 TR é utilizada para instalação de transformadores;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE3 TRSC": [
        "A estrutura tipo CE3 TRSC é utilizada para instalação de transformadores;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE3-CE3": [
        "A estrutura tipo CE3-CE3 é utilizada em fim de rede e em ângulos de deflexão de 60º a 90º;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE3-I": [
        "A estrutura tipo CE3-I é utilizada em transições de rede convencional para rede isolada;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE3-I SUI": [
        "A estrutura tipo CE3-I SUI é utilizada em transições de rede convencional para rede isolada;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE3-PU": [
        "A estrutura tipo CE3-PU é utilizada em fim de rede e em ângulos de deflexão de 60º a 90º;",
        "Esta estrutura deve ser utilizada preferencialmente em postes já instalados onde há necessidade de elevação do nível da rede primária, como por exemplo em circuitos duplos;",
        "Deve ser respeitada as distancias de segurança estabelecidas neste normativo;",
        "Esta estrutura não se aplica em redes de 34,5 kV.",
        "A Estrutura CE3-PU possibilita a elevar a altura da rede em 0,5 m quando comparada com a CE3."
    ],
    "CE3PU-CE3PU": [
        "A estrutura tipo CE3PU-CE3PU é utilizada em fim de rede e em ângulos de deflexão de 60º a 90º;",
        "Esta estrutura deve ser utilizada preferencialmente em postes já instalados onde há necessidade de elevação do nível da rede primária, como por exemplo em circuitos duplos;",
        "Deve ser respeitada as distancias de segurança estabelecidas neste normativo;",
        "Esta estrutura não se aplica em redes de 34,5 kV.",
        "A Estrutura CE3PU-CE3PU possibilita a elevar a altura da rede em 0,5 m quando comparada com a CE3-CE3."
    ],
    "CE4": [
        "A estrutura tipo CE4 é utilizada em fim de rede e em ângulos de deflexão de 60º a 90º;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE4 CF": [
        "A estrutura tipo CE4 CF é utilizada para instalação de chaves fusíveis;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE4 CF SAH": [
        "A estrutura tipo CE4 CF SAH é utilizada para instalação de chaves fusíveis;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE4 SUH": [
        "A estrutura tipo CE4 SUH é utilizada para instalação de chaves fusíveis;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE4 SUI": [
        "A estrutura tipo CE4 SUI é utilizada para instalação de chaves fusíveis;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE4 TR": [
        "A estrutura tipo CE4 TR é utilizada para instalação de transformadores;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE4-PU": [
        "A estrutura tipo CE4-PU é utilizada em fim de rede e em ângulos de deflexão de 60º a 90º;",
        "Esta estrutura deve ser utilizada preferencialmente em postes já instalados onde há necessidade de elevação do nível da rede primária, como por exemplo em circuitos duplos;",
        "Deve ser respeitada as distancias de segurança estabelecidas neste normativo;",
        "Esta estrutura não se aplica em redes de 34,5 kV.",
        "A Estrutura CE4-PU possibilita a elevar a altura da rede em 0,5 m quando comparada com a CE4."
    ],
    "CEJ1": [
        "A estrutura tipo CEJ1 é utilizada com o objetivo de afastar os condutores de edificações;",
        "A estrutura tipo CEJ1 não deve ser utilizada em postes de 200 daN quando a bitola dos condutores forem iguais ou superiores a 185 mm² para classe de tensão de 15 kV e iguais ou superiores a 70 mm² para classe de tensão de 36 kV;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CEJ1 SAH": [
        "A estrutura tipo CEJ1 SAH é utilizada com o objetivo de afastar os condutores de edificações;",
        "A estrutura tipo CEJ1 SAH não deve ser utilizada em postes de 200 daN quando a bitola dos condutores forem iguais ou superiores a 185 mm² para classe de tensão de 15 kV e iguais ou superiores a 70 mm² para classe de tensão de 36 kV;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CEJ2": [
        "A estrutura tipo CEJ2 é utilizada nos casos de deflexão da rede de 7º à 60º para cabos de seções 35 mm² e 70 mm² e 7º à 45º para cabos de seções 185 mm² e 240 mm²;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CEJ2 SAH": [
        "A estrutura tipo CEJ2 SAH é utilizada nos casos de deflexão da rede de 7º à 60º para cabos de seções 35 mm² e 70 mm² e 7º à 45º para cabos de seções 185 mm² e 240 mm²;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "Monofásicas Básicas": [
        "As estruturas tipo Monofásicas Básicas são utilizadas em redes monofásicas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "Monofásicas Derivação": [
        "As estruturas tipo Monofásicas de Derivação são utilizadas em derivações de redes monofásicas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N3.CE3": [
        "A estrutura tipo N3.CE3 é utilizada em transições de rede convencional para rede isolada;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N3.CE3 SUH": [
        "A estrutura tipo N3.CE3 SUH é utilizada em transições de rede convencional para rede isolada;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N3.CE3 SUI": [
        "A estrutura tipo N3.CE3 SUI é utilizada em transições de rede convencional para rede isolada;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    # ── DIS-NOR-014 ─────────────────────────────────────────────
    "AT Condutor Ext (014)": [
        "A estrutura tipo AT Condutor Externo é utilizada para aterramento de condutor externo;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "AT Condutor Int (014)": [
        "A estrutura tipo AT Condutor Interno é utilizada para aterramento de condutor interno;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CAB": [
        "A estrutura tipo CAB é utilizada para cruzamento aéreo multiplexado;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "FLABIT": [
        "A estrutura tipo FLABIT é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "FLABIDM": [
        "A estrutura tipo FLABIDM é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "FLABIDT": [
        "A estrutura tipo FLABIDT é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "FLABIM": [
        "A estrutura tipo FLABIM é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "FLBIM": [
        "A estrutura tipo FLBIM é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "FLBIM NI": [
        "A estrutura tipo FLBIM NI é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "FLBIT": [
        "A estrutura tipo FLBIT é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "FLBIT NI": [
        "A estrutura tipo FLBIT NI é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "IBI": [
        "A estrutura tipo IBI é utilizada para interligação nu/multiplexado;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "IT-R": [
        "A estrutura tipo IT-R é utilizada para instalação de transformadores;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "ITF-R": [
        "A estrutura tipo ITF-R é utilizada para instalação de transformadores;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "LCM": [
        "A estrutura tipo LCM é utilizada para ligação de consumidores multiderivações;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "SAB": [
        "A estrutura tipo SAB é utilizada para seccionamento aéreo;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "SDBIM": [
        "A estrutura tipo SDBIM é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "SDBIT": [
        "A estrutura tipo SDBIT é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "SDANI": [
        "A estrutura tipo SDANI é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "SMBI": [
        "A estrutura tipo SMBI é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "SPBI": [
        "A estrutura tipo SPBI é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "STBI": [
        "A estrutura tipo STBI é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    # ── DIS-NOR-018 ─────────────────────────────────────────────
    "AT Descida Ext (018)": [
        "A estrutura tipo AT Descida Ext é utilizada para aterramento de descida externa;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "AT Descida Int (018)": [
        "A estrutura tipo AT Descida Int é utilizada para aterramento de descida interna;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "B1": [
        "A estrutura tipo B1 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "B3 (018)": [
        "A estrutura tipo B3 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "B4": [
        "A estrutura tipo B4 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CFU 1º NÍVEL": [
        "A estrutura tipo CFU 1º Nível é utilizada para chaves fusíveis em 1º nível;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "ESTAI CONTRAPOSTE": [
        "A estrutura tipo ESTAI CONTRAPOSTE é utilizada para estaiamento de contraposte;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "ESTAI NORMAL": [
        "A estrutura tipo ESTAI NORMAL é utilizada para estai em terreno normal;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "ESTAI ROCHA": [
        "A estrutura tipo ESTAI ROCHA é utilizada para estai em rochas e pântanos;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "HTC": [
        "A estrutura tipo HTC é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "HTC FIM REDE": [
        "A estrutura tipo HTC FIM REDE é utilizada em fim de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "HTE": [
        "A estrutura tipo HTE é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "HTE FIM REDE": [
        "A estrutura tipo HTE FIM REDE é utilizada em fim de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "HTC-1 Deriv N3": [
        "A estrutura tipo HTC-1 Deriv N3 é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "HTC-2 Deriv N3": [
        "A estrutura tipo HTC-2 Deriv N3 é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "HTE-1 Deriv N3": [
        "A estrutura tipo HTE-1 Deriv N3 é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "HTE-2 Deriv N3": [
        "A estrutura tipo HTE-2 Deriv N3 é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "HTE-2XN3": [
        "A estrutura tipo HTE-2XN3 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "HTE-N3": [
        "A estrutura tipo HTE-N3 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "HTC-2XN3": [
        "A estrutura tipo HTC-2XN3 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "HTC-N3": [
        "A estrutura tipo HTC-N3 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "LDE": [
        "A estrutura tipo LDE é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "M1-N2 FR Chaves": [
        "A estrutura tipo M1-N2 FR Chaves é utilizada em fim de rede com chaves fusíveis;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "M1-N3": [
        "A estrutura tipo M1-N3 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "M1-N3 FR Chaves": [
        "A estrutura tipo M1-N3 FR Chaves é utilizada em fim de rede com chaves fusíveis;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "M-N2BFR": [
        "A estrutura tipo M-N2BFR é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "M-N3B": [
        "A estrutura tipo M-N3B é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N1": [
        "A estrutura tipo N1 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N1-TT": [
        "A estrutura tipo N1-TT é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N3 (018)": [
        "A estrutura tipo N3 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N3-N3 (018)": [
        "A estrutura tipo N3-N3 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N3-TT": [
        "A estrutura tipo N3-TT é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N3-TT-SOB": [
        "A estrutura tipo N3-TT-SOB é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N4": [
        "A estrutura tipo N4 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N4 COM CRUZETA": [
        "A estrutura tipo N4 COM CRUZETA é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N4-CFU": [
        "A estrutura tipo N4-CFU é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N4-N3 (018)": [
        "A estrutura tipo N4-N3 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N4-N3-CFU": [
        "A estrutura tipo N4-N3-CFU é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "PARA-RAIOS 2ºNÍV": [
        "A estrutura tipo PARA-RAIOS 2ºNÍV é utilizada para para-raios em 2º nível;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "PT Est.M1": [
        "A estrutura tipo PT Est.M1 é utilizada para posto de transformação;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "PT Est.N3": [
        "A estrutura tipo PT Est.N3 é utilizada para posto de transformação;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "PT Est.N3 FimRede": [
        "A estrutura tipo PT Est.N3 FimRede é utilizada para posto de transformação em fim de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "PT Est.U1": [
        "A estrutura tipo PT Est.U1 é utilizada para posto de transformação;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "PT N3 2+ Clientes": [
        "A estrutura tipo PT N3 2+ Clientes é utilizada para ligação de 2 ou mais clientes;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "PT N3 sem Chaves": [
        "A estrutura tipo PT N3 sem Chaves é utilizada para posto de transformação sem chaves;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "PT N3 sem Chaves 2": [
        "A estrutura tipo PT N3 sem Chaves 2 é utilizada para posto de transformação sem chaves;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "PT N3 com Chaves": [
        "A estrutura tipo PT N3 com Chaves é utilizada para posto de transformação com chaves;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "TE": [
        "A estrutura tipo TE é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "TE FIM REDE": [
        "A estrutura tipo TE FIM REDE é utilizada em fim de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "U1": [
        "A estrutura tipo U1 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "U1-U3 c/Chaves": [
        "A estrutura tipo U1-U3 c/Chaves é utilizada em ramal com chaves;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "U1-U3 s/Chaves": [
        "A estrutura tipo U1-U3 s/Chaves é utilizada em ramal sem chaves;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "U2": [
        "A estrutura tipo U2 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "U3": [
        "A estrutura tipo U3 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "U3-3": [
        "A estrutura tipo U3-3 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "U4": [
        "A estrutura tipo U4 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
}

CORES_NORMA = {
    "DIS-NOR-013": "#1e6b3c",
    "DIS-NOR-014": "#1a4f8a",
    "DIS-NOR-018": "#8a3a1a",
}

# ─────────────────────────────────────────────────────────────────
# FUNÇÕES
# ─────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner="Carregando desenho...")
def extrair_imagem(pdf_path: str, pagina: int, dpi: int = 150) -> bytes:
    with tempfile.TemporaryDirectory() as tmpdir:
        prefix = os.path.join(tmpdir, "pag")
        subprocess.run(
            ["pdftoppm", "-jpeg", "-r", str(dpi),
             "-f", str(pagina), "-l", str(pagina),
             pdf_path, prefix],
            check=True, capture_output=True,
        )
        arquivos = sorted(glob.glob(f"{prefix}-*.jpg"))
        if not arquivos:
            raise FileNotFoundError("pdftoppm não gerou imagem.")
        img = Image.open(arquivos[0])

    w, h = img.size
    # Cortar cabeçalho (13% do topo)
    img = img.crop((0, int(h * 0.13), w, h))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def extrair_notas_dinamicamente(pdf_path, pagina_inicio):
    """Tenta extrair notas do PDF próximo à página da estrutura."""
    import pdfplumber
    import re
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Procura na página do desenho e nas 3 seguintes
            for p_idx in range(pagina_inicio - 1, min(pagina_inicio + 3, len(pdf.pages))):
                page = pdf.pages[p_idx]
                text = page.extract_text()
                if not text: continue
                if "Notas:" in text or "Nota:" in text:
                    lines = text.split('\n')
                    start_collecting = False
                    found_notes = []
                    for line in lines:
                        if re.search(r'Nota(s)?:', line, re.IGNORECASE):
                            start_collecting = True
                            continue
                        if start_collecting:
                            match = re.match(r'^\s*(\d+)\.\s+(.*)', line)
                            if match:
                                found_notes.append(match.group(2).strip())
                            elif found_notes and line.strip():
                                if any(x in line for x in ["TÍTULO:", "CÓDIGO:", "APROVADOR:", "PÁG.:"]): continue
                                found_notes[-1] = found_notes[-1] + " " + line.strip()
                            elif found_notes and not line.strip():
                                break
                    if found_notes: return found_notes
    except:
        pass
    return None

# ─────────────────────────────────────────────────────────────────
# TEMA / IDENTIDADE VISUAL
# ─────────────────────────────────────────────────────────────────
INK      = "#132A3A"   # navy de prancha técnica
INK_2    = "#1D3E54"   # navy um tom mais claro (hover/cards na sidebar)
PAPER    = "#F4F6F5"   # papel técnico frio (não creme)
PAPER_2  = "#FFFFFF"   # cartão sobre o papel
LINE     = "#D7DEDC"   # linha/traço sutil sobre o papel
AMBER    = "#F2A900"   # âmbar de sinalização elétrica (destaque único)
TEXT     = "#16232B"

st.set_page_config(
    page_title="Estruturas Elétricas – Neoenergia Elektro",
    page_icon="⚡",
    layout="wide",
)

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'IBM Plex Sans', sans-serif;
    color: {TEXT};
}}

/* Fundo geral: papel técnico com grade de pontos sutil */
.stApp {{
    background-color: {PAPER};
    background-image: radial-gradient({LINE} 1px, transparent 1px);
    background-size: 22px 22px;
}}

.block-container {{
    padding-top: 2rem;
    max-width: 1200px;
}}

/* ---- Sidebar: painel de índice, estilo prancha ---- */
section[data-testid="stSidebar"] {{
    background-color: {INK};
    border-right: 3px solid {AMBER};
}}
section[data-testid="stSidebar"] * {{
    color: #E7EEF2 !important;
}}
section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] small {{
    color: #93A9B8 !important;
}}
.sidebar-brand {{
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 700;
    font-size: 1.05rem;
    letter-spacing: 0.02em;
    color: #FFFFFF !important;
    margin-bottom: 0;
}}
.sidebar-sub {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: {AMBER} !important;
}}
.norma-heading {{
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    font-size: 11px;
    letter-spacing: 0.08em;
    margin-top: 14px;
    margin-bottom: 2px;
    padding-bottom: 3px;
    border-bottom: 1px dashed rgba(255,255,255,0.25);
}}

/* Botões da lista de estruturas */
section[data-testid="stSidebar"] .stButton>button {{
    background-color: transparent;
    border: none;
    border-left: 3px solid transparent;
    border-radius: 0;
    text-align: left;
    padding: 6px 10px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    font-weight: 500;
    color: #C9D6DD !important;
    transition: all 0.12s ease;
}}
section[data-testid="stSidebar"] .stButton>button:hover {{
    background-color: {INK_2};
    color: #FFFFFF !important;
    border-left: 3px solid {AMBER};
}}
section[data-testid="stSidebar"] .stSelectbox label {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: {AMBER} !important;
}}

/* ---- Carimbo / title block da estrutura selecionada ---- */
.title-block {{
    background: {PAPER_2};
    border: 1px solid {LINE};
    border-left: 6px solid var(--accent);
    border-radius: 6px;
    padding: 18px 22px;
    margin-bottom: 20px;
    box-shadow: 0 1px 2px rgba(19,42,58,0.05);
}}
.title-block .eyebrow {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent);
    font-weight: 600;
    margin-bottom: 4px;
}}
.title-block h2 {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.4rem;
    font-weight: 600;
    margin: 0 0 8px 0;
    color: {TEXT};
}}
.norma-stamp {{
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.04em;
    color: var(--accent);
    border: 1.5px solid var(--accent);
    border-radius: 4px;
    padding: 2px 10px;
}}

/* ---- Cartões da área principal ---- */
.panel {{
    background: {PAPER_2};
    border: 1px solid {LINE};
    border-radius: 6px;
    padding: 18px 20px;
}}
.panel h3, .panel-title {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #4E6472;
    margin-top: 0;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid {LINE};
}}
.note-row {{
    display: flex;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px dashed {LINE};
    font-size: 14.5px;
    line-height: 1.5;
}}
.note-row:last-child {{ border-bottom: none; }}
.note-num {{
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 700;
    color: {AMBER};
    min-width: 20px;
}}
.empty-hero {{
    background: {PAPER_2};
    border: 1px dashed {LINE};
    border-radius: 8px;
    padding: 48px 32px;
    text-align: center;
}}
.empty-hero .big {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.6rem;
    font-weight: 600;
    color: {INK};
}}
.empty-hero .sub {{
    color: #5B6E79;
    margin-top: 6px;
}}

div[data-testid="stImage"] img {{
    border: 1px solid {LINE};
    border-radius: 6px;
    background: white;
}}
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<p class="sidebar-brand">⚡ Estruturas Elétricas</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-sub">Neoenergia Elektro</p>', unsafe_allow_html=True)
    st.divider()

    norma_filtro = st.selectbox(
        "Filtrar por norma",
        ["Todas", "DIS-NOR-013", "DIS-NOR-014", "DIS-NOR-018"],
        index=0,
    )
    st.divider()

    if "estrutura_ativa" not in st.session_state:
        st.session_state["estrutura_ativa"] = None

    codigos_ordenados = sorted(ESTRUTURAS.keys())
    normas = ["DIS-NOR-013", "DIS-NOR-014", "DIS-NOR-018"]
    for norma in normas:
        if norma_filtro != "Todas" and norma_filtro != norma: continue
        st.markdown(f'<div class="norma-heading">{norma}</div>', unsafe_allow_html=True)
        for codigo in codigos_ordenados:
            pag, titulo, n = ESTRUTURAS[codigo]
            if n != norma: continue
            ativo = st.session_state["estrutura_ativa"] == codigo
            label = f"▶ {codigo}" if ativo else codigo
            if st.button(label, key=f"btn_{codigo}", use_container_width=True):
                st.session_state["estrutura_ativa"] = codigo
                st.rerun()

# Área principal
selecionada = st.session_state.get("estrutura_ativa")

if not selecionada:
    st.markdown(f"""
    <div class="empty-hero">
        <div class="big">⚡ Estruturas Elétricas — Neoenergia Elektro</div>
        <div class="sub">Selecione uma estrutura na lista à esquerda para abrir a prancha técnica.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    pagina, titulo, norma = ESTRUTURAS[selecionada]
    cor = CORES_NORMA[norma]

    st.markdown(f"""
    <div class="title-block" style="--accent: {cor};">
        <div class="eyebrow">Ficha técnica · {selecionada}</div>
        <h2>{titulo}</h2>
        <span class="norma-stamp">{norma}</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2.5, 1])

    with col1:
        try:
            pdf_path = PDF_PATHS[norma]
            img_bytes = extrair_imagem(pdf_path, pagina, DPI)
            st.image(img_bytes, use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ Erro ao carregar imagem: {e}")

    with col2:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">📌 Notas</div>', unsafe_allow_html=True)

        # 1. Tenta pegar do banco estático
        notas = NOTAS_ESTRUTURAS.get(selecionada)

        # 2. Se não tiver no banco, tenta extrair dinamicamente (com cache opcional)
        if not notas:
            with st.spinner("Buscando notas no PDF..."):
                notas = extrair_notas_dinamicamente(PDF_PATHS[norma], pagina)

        if notas:
            for i, nota in enumerate(notas, 1):
                st.markdown(f'<div class="note-row"><span class="note-num">{i}</span><span>{nota}</span></div>', unsafe_allow_html=True)
        else:
            st.write("Nenhuma nota encontrada para esta estrutura.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.write("")
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">📋 Relação de Materiais</div>', unsafe_allow_html=True)
        st.caption("Consulte o PDF completo da norma para a relação detalhada de materiais desta estrutura.")
        st.markdown('</div>', unsafe_allow_html=True)
