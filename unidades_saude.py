"""
================================================================================
CADASTRO OFICIAL DE UNIDADES DE SAÚDE NOTIFICADORAS - ITAPORÃ / MS
Gerência Municipal de Saúde - CNES, Endereços, Contatos e Georreferenciamento
================================================================================
Fonte Oficial: Prefeitura Municipal de Itaporã / Gerência de Saúde
Documento Oficial de Unidades de Saúde (2025/2028)
"""

from typing import Dict, Any, Optional, List
import pandas as pd

# Unidades Oficiais da Rede Municipal de Itaporã / MS
UNIDADES_SAUDE_ITAPORA: Dict[str, Dict[str, Any]] = {
    "2651505": {
        "cnes": "2651505",
        "nome": "Hospital Municipal Lourival Nascimento da Silva",
        "sigla": "Hospital Municipal",
        "tipo": "Hospital Geral / Urgência & Emergência",
        "horario": "24 Horas Ininterrupto",
        "telefones": "(67) 3451-1240 / 3451-1406",
        "email": "saudeitapora@hotmail.com",
        "responsavel": "Direção Clínica / Gerência de Saúde",
        "logradouro": "Rua José Teixeira da Silva, 1115",
        "bairro": "Centro",
        "cep": "79890-019",
        "municipio": "Itaporã - MS",
        "endereco_completo": "Rua José Teixeira da Silva, 1115, Centro, CEP 79890-019, Itaporã - MS",
        "lat": -22.0768,
        "lon": -54.7932,
        "is_rural": False,
        "cor_marcador": "#2563EB"
    },
    "6848028": {
        "cnes": "6848028",
        "nome": "ESF Central",
        "sigla": "ESF Central",
        "tipo": "Estratégia Saúde da Família (Atenção Básica)",
        "horario": "07:00 às 11:00 HS | 13:00 às 17:00 HS",
        "telefones": "(67) 3451-1456 / 99954-6966",
        "email": "saudeitapora@hotmail.com",
        "responsavel": "Irene Shizuka Miyamura",
        "logradouro": "Rua José Teixeira da Silva, 540",
        "bairro": "Centro",
        "cep": "79890-013",
        "municipio": "Itaporã - MS",
        "endereco_completo": "Rua José Teixeira da Silva, 540, Centro, CEP 79890-013, Itaporã - MS",
        "lat": -22.0792,
        "lon": -54.7905,
        "is_rural": False,
        "cor_marcador": "#38BDF8"
    },
    "7261179": {
        "cnes": "7261179",
        "nome": "ESF São Bento",
        "sigla": "ESF São Bento",
        "tipo": "Estratégia Saúde da Família (Atenção Básica)",
        "horario": "07:00 às 11:00 HS | 13:00 às 17:00 HS",
        "telefones": "(67) 3451-1524 / 99674-9469",
        "email": "saudeitapora@hotmail.com",
        "responsavel": "Vanessa Paiva Thiesen",
        "logradouro": "Rua Pedro José Tavares, 10",
        "bairro": "São Bento",
        "cep": "79891-002",
        "municipio": "Itaporã - MS",
        "endereco_completo": "Rua Pedro José Tavares, 10, São Bento, CEP 79891-002, Itaporã - MS",
        "lat": -22.0835,
        "lon": -54.7820,
        "is_rural": False,
        "cor_marcador": "#10B981"
    },
    "2360993": {
        "cnes": "2360993",
        "nome": "ESF Pioneira",
        "sigla": "ESF Pioneira",
        "tipo": "Estratégia Saúde da Família (Atenção Básica)",
        "horario": "07:00 às 11:00 HS | 13:00 às 17:00 HS",
        "telefones": "(67) 3451-5989 / 99926-2898",
        "email": "saudeitapora@hotmail.com",
        "responsavel": "Elisangela da Silva Oliveira Mendonça",
        "logradouro": "Rua Bartolo Cabulao (Antiga Projetada 3)",
        "bairro": "Nova Era",
        "cep": "79891-220",
        "municipio": "Itaporã - MS",
        "endereco_completo": "Rua Bartolo Cabulao (Antiga Projetada 3), Nova Era, CEP 79891-220, Itaporã - MS",
        "lat": -22.0740,
        "lon": -54.7860,
        "is_rural": False,
        "cor_marcador": "#F59E0B"
    },
    "2361450": {
        "cnes": "2361450",
        "nome": "ESF Copacabana",
        "sigla": "ESF Copacabana",
        "tipo": "Estratégia Saúde da Família (Atenção Básica)",
        "horario": "07:00 às 11:00 HS | 13:00 às 17:00 HS",
        "telefones": "(67) 3451-2340 / 99649-7556",
        "email": "saudeitapora@hotmail.com",
        "responsavel": "Josilaine Bronzati Fortes Frota",
        "logradouro": "Rua Primo Rondina, 80",
        "bairro": "Copacabana",
        "cep": "79890-314",
        "municipio": "Itaporã - MS",
        "endereco_completo": "Rua Primo Rondina, 80, Copacabana, CEP 79890-314, Itaporã - MS",
        "lat": -22.0860,
        "lon": -54.7940,
        "is_rural": False,
        "cor_marcador": "#8B5CF6"
    },
    "2361442": {
        "cnes": "2361442",
        "nome": "ESF COHAB",
        "sigla": "ESF COHAB",
        "tipo": "Estratégia Saúde da Família (Atenção Básica)",
        "horario": "07:00 às 11:00 HS | 13:00 às 17:00 HS",
        "telefones": "(67) 3451-1651 / 99934-6503",
        "email": "saudeitapora@hotmail.com",
        "responsavel": "Adila Vanessa Rodrigues Martins",
        "logradouro": "Rua João Rodrigues de Freitas",
        "bairro": "COHAB",
        "cep": "79893-066",
        "municipio": "Itaporã - MS",
        "endereco_completo": "Rua João Rodrigues de Freitas, COHAB, CEP 79893-066, Itaporã - MS",
        "lat": -22.0715,
        "lon": -54.7925,
        "is_rural": False,
        "cor_marcador": "#EC4899"
    },
    "2651483": {
        "cnes": "2651483",
        "nome": "ESF Montese e Piraporã",
        "sigla": "ESF Montese/Piraporã",
        "tipo": "Estratégia Saúde da Família (Atenção Básica - Rural)",
        "horario": "07:00 às 11:00 HS | 13:00 às 17:00 HS",
        "telefones": "(67) 3457-1236 / 98422-8095",
        "email": "saudeitapora@hotmail.com",
        "responsavel": "Clarice Faleiros Noda",
        "logradouro": "Rua Benjamim Constant, Duque de Caxias",
        "bairro": "Distrito de Montese",
        "cep": "79896-006",
        "municipio": "Itaporã - MS",
        "endereco_completo": "Rua Benjamim Constant, Duque de Caxias, Montese, CEP 79896-006, Itaporã - MS",
        "lat": -22.0420,
        "lon": -54.8350,
        "is_rural": True,
        "cor_marcador": "#06B6D4"
    },
    "2361434": {
        "cnes": "2361434",
        "nome": "ESF Carumbé e Santa Terezinha",
        "sigla": "ESF Carumbé/Sta Terezinha",
        "tipo": "Estratégia Saúde da Família (Atenção Básica - Rural)",
        "horario": "07:00 às 11:00 HS | 13:00 às 17:00 HS",
        "telefones": "(67) 99630-1998",
        "email": "saudeitapora@hotmail.com",
        "responsavel": "Dayane Dias Pereira dos Anjos",
        "logradouro": "Av. Manoel Simplício Aureno Cordeiro",
        "bairro": "Distrito de Santa Terezinha / Carumbé",
        "cep": "79896-504",
        "municipio": "Itaporã - MS",
        "endereco_completo": "Av. Manoel Simplício Aureno Cordeiro, Santa Terezinha, CEP 79896-504, Itaporã - MS",
        "lat": -22.0150,
        "lon": -54.9120,
        "is_rural": True,
        "cor_marcador": "#14B8A6"
    },
    "2651513": {
        "cnes": "2651513",
        "nome": "Unidade de Vigilância Sanitária de Itaporã",
        "sigla": "VISA Itaporã",
        "tipo": "Vigilância em Saúde / Sanitária / Epidemiológica",
        "horario": "07:00 às 11:00 HS | 13:00 às 17:00 HS",
        "telefones": "(67) 3451-4406",
        "email": "saudeitapora@hotmail.com",
        "responsavel": "Luciano Marcelo Bezerra Gonela",
        "logradouro": "Rua Dez de Dezembro, 1180",
        "bairro": "Bom Jesus",
        "cep": "79890-160",
        "municipio": "Itaporã - MS",
        "endereco_completo": "Rua Dez de Dezembro, 1180, Bom Jesus, CEP 79890-160, Itaporã - MS",
        "lat": -22.0805,
        "lon": -54.7890,
        "is_rural": False,
        "cor_marcador": "#EAB308"
    },
    "5830753": {
        "cnes": "5830753",
        "nome": "Laboratório Municipal Arsenio Santos Costa",
        "sigla": "Laboratório Municipal",
        "tipo": "Laboratório de Análises Clínicas",
        "horario": "06:00 às 11:00 HS | 13:00 às 17:00 HS",
        "telefones": "(67) 3451-4406",
        "email": "saudeitapora@hotmail.com",
        "responsavel": "Mayara Gonçalves Garcia",
        "logradouro": "Rua Pedro Celestino Corrêa da Costa, 719",
        "bairro": "Centro",
        "cep": "79890-005",
        "municipio": "Itaporã - MS",
        "endereco_completo": "Rua Pedro Celestino Corrêa da Costa, 719, Centro, CEP 79890-005, Itaporã - MS",
        "lat": -22.0775,
        "lon": -54.7885,
        "is_rural": False,
        "cor_marcador": "#A855F7"
    }
}

# Unidades Regionais / Referência Externa (Dourados e Macrorregião de Saúde)
UNIDADES_REGIONAIS: Dict[str, Dict[str, Any]] = {
    "6201059": {
        "cnes": "6201059",
        "nome": "Hospital da Vida (Dourados)",
        "sigla": "Hospital da Vida",
        "tipo": "Hospital Regional / Urgência Macrorregional",
        "horario": "24 Horas",
        "telefones": "(67) 3411-7700",
        "email": "-",
        "responsavel": "Direção Hospitalar",
        "logradouro": "Rua Toshinobu Katayama, 620",
        "bairro": "Vila Planalto",
        "cep": "79805-030",
        "municipio": "Dourados - MS",
        "endereco_completo": "Rua Toshinobu Katayama, 620, Vila Planalto, Dourados - MS",
        "lat": -22.2215,
        "lon": -54.8055,
        "is_rural": False,
        "cor_marcador": "#64748B"
    },
    "2371324": {
        "cnes": "2371324",
        "nome": "Hospital Universitário da UFGD (Dourados)",
        "sigla": "HU-UFGD",
        "tipo": "Hospital Terciário de Alta Complexidade / Federal",
        "horario": "24 Horas",
        "telefones": "(67) 3410-3000",
        "email": "-",
        "responsavel": "Superintendência EBSERH",
        "logradouro": "Rua Ivo Alves da Rocha, 558",
        "bairro": "Altos do Indaiá",
        "cep": "79823-501",
        "municipio": "Dourados - MS",
        "endereco_completo": "Rua Ivo Alves da Rocha, 558, Altos do Indaiá, Dourados - MS",
        "lat": -22.2270,
        "lon": -54.8380,
        "is_rural": False,
        "cor_marcador": "#64748B"
    },
    "3074889": {
        "cnes": "3074889",
        "nome": "UPA 24 Horas de Dourados",
        "sigla": "UPA Dourados",
        "tipo": "Unidade de Pronto Atendimento 24h",
        "horario": "24 Horas",
        "telefones": "(67) 3411-7140",
        "email": "-",
        "responsavel": "Coordenação UPA",
        "logradouro": "Rua Coronel Ponciano, 900",
        "bairro": "Parque dos Jequitibás",
        "cep": "79830-070",
        "municipio": "Dourados - MS",
        "endereco_completo": "Rua Coronel Ponciano, 900, Parque dos Jequitibás, Dourados - MS",
        "lat": -22.2340,
        "lon": -54.7890,
        "is_rural": False,
        "cor_marcador": "#64748B"
    },
    "834718": {
        "cnes": "834718",
        "nome": "Hospital CASSEMS Dourados",
        "sigla": "CASSEMS Dourados",
        "tipo": "Hospital Privado / Convênio",
        "horario": "24 Horas",
        "telefones": "(67) 3411-8500",
        "email": "-",
        "responsavel": "Direção Médica CASSEMS",
        "logradouro": "Rua Monte Alegre, 2070",
        "bairro": "Vila Lili",
        "cep": "79825-040",
        "municipio": "Dourados - MS",
        "endereco_completo": "Rua Monte Alegre, 2070, Vila Lili, Dourados - MS",
        "lat": -22.2150,
        "lon": -54.8080,
        "is_rural": False,
        "cor_marcador": "#64748B"
    },
    "2371375": {
        "cnes": "2371375",
        "nome": "Hospital Evangélico Dr. e Sra. Goldsby King",
        "sigla": "Hospital Evangélico",
        "tipo": "Hospital Geral / Filantrópico",
        "horario": "24 Horas",
        "telefones": "(67) 3421-4000",
        "email": "-",
        "responsavel": "Direção Geral",
        "logradouro": "Rua Firmino Vieira de Matos, 1105",
        "bairro": "Centro",
        "cep": "79801-020",
        "municipio": "Dourados - MS",
        "endereco_completo": "Rua Firmino Vieira de Matos, 1105, Centro, Dourados - MS",
        "lat": -22.2245,
        "lon": -54.8030,
        "is_rural": False,
        "cor_marcador": "#64748B"
    }
}


def obter_unidade_por_cnes(cnes_raw: Any) -> Dict[str, Any]:
    """
    Retorna o cadastro detalhado da unidade a partir do código CNES (numérico ou texto).
    Se a unidade for de Itaporã ou da regional cadastrada, retorna dados completos.
    Caso contrário, padroniza com categoria de unidade externa.
    """
    if cnes_raw is None or pd.isna(cnes_raw):
        return {
            "cnes": "NÃO INFORMADO",
            "nome": "Unidade Não Informada",
            "sigla": "Não Informado",
            "tipo": "Não Especificado",
            "horario": "-",
            "telefones": "-",
            "email": "-",
            "responsavel": "-",
            "logradouro": "Município de Itaporã",
            "bairro": "Itaporã",
            "cep": "79890-000",
            "municipio": "Itaporã - MS",
            "endereco_completo": "Município de Itaporã - MS",
            "lat": -22.0803,
            "lon": -54.7892,
            "is_rural": False,
            "cor_marcador": "#71717A"
        }

    cnes_str = str(cnes_raw).strip().split(".")[0]
    
    # 1. Unidades municipais de Itaporã (prioritárias)
    if cnes_str in UNIDADES_SAUDE_ITAPORA:
        return UNIDADES_SAUDE_ITAPORA[cnes_str]

    # 2. Unidades regionais conhecidas
    if cnes_str in UNIDADES_REGIONAIS:
        return UNIDADES_REGIONAIS[cnes_str]

    # 3. Unidade externa não catalogada
    return {
        "cnes": cnes_str,
        "nome": f"Unidade Externa (CNES {cnes_str})",
        "sigla": f"CNES {cnes_str}",
        "tipo": "Outro Município / Privada",
        "horario": "-",
        "telefones": "-",
        "email": "-",
        "responsavel": "-",
        "logradouro": "Atendimento Externo",
        "bairro": "Regional",
        "cep": "-",
        "municipio": "MS",
        "endereco_completo": f"Unidade Notificadora Externa - CNES {cnes_str}",
        "lat": -22.2215,
        "lon": -54.8055,
        "is_rural": False,
        "cor_marcador": "#71717A"
    }


def obter_catalogo_unidades_itapora_df() -> pd.DataFrame:
    """
    Retorna um DataFrame estruturado de todas as unidades de saúde oficiais de Itaporã
    com endereços, telefones, horários e responsáveis para exibição em tabelas e relatórios.
    """
    records = []
    for cnes, info in UNIDADES_SAUDE_ITAPORA.items():
        records.append({
            "CNES": cnes,
            "Unidade": info["nome"],
            "Sigla": info["sigla"],
            "Tipo / Nível": info["tipo"],
            "Endereço": info["logradouro"],
            "Bairro": info["bairro"],
            "CEP": info["cep"],
            "Horário de Atendimento": info["horario"],
            "Telefones": info["telefones"],
            "E-mail": info["email"],
            "Responsável": info["responsavel"],
            "Latitude": info["lat"],
            "Longitude": info["lon"],
            "Rural": "Sim" if info["is_rural"] else "Não"
        })
    return pd.DataFrame(records)


def enriquecer_dataframe_com_unidades(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona colunas padronizadas de CNES, Nome, Endereço Completo,
    Telefone, Responsável, Horário e Coordenadas de Notificação no DataFrame SINAN.
    """
    if df is None or df.empty or "ID_UNIDADE" not in df.columns:
        return df

    cnes_col = df["ID_UNIDADE"]
    nomes = []
    siglas = []
    enderecos = []
    telefones = []
    responsaveis = []
    horarios = []
    lats_notif = []
    lons_notif = []

    cache_unidades = {}

    for cnes_val in cnes_col:
        key = str(cnes_val).strip().split(".")[0] if pd.notna(cnes_val) else "NAN"
        if key not in cache_unidades:
            cache_unidades[key] = obter_unidade_por_cnes(cnes_val)
        
        u = cache_unidades[key]
        nomes.append(u["nome"])
        siglas.append(u["sigla"])
        enderecos.append(u["endereco_completo"])
        telefones.append(u["telefones"])
        responsaveis.append(u["responsavel"])
        horarios.append(u["horario"])
        lats_notif.append(u["lat"])
        lons_notif.append(u["lon"])

    df["CNES_UNIDADE"] = cnes_col.astype(str).str.split(".").str[0].str.strip()
    df["NM_UNIDADE_NOTIF"] = nomes
    df["SIGLA_UNIDADE_NOTIF"] = siglas
    df["ENDERECO_UNIDADE"] = enderecos
    df["TELEFONE_UNIDADE"] = telefones
    df["RESPONSAVEL_UNIDADE"] = responsaveis
    df["HORARIO_UNIDADE"] = horarios
    df["LAT_NOTIF"] = lats_notif
    df["LON_NOTIF"] = lons_notif

    return df
