"""
Módulo Estatístico e Preditivo: Canal Endêmico, Holt-Winters / ARIMA e Matriz de Risco Epidemiológico
"""

from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA

POPULACAO_ITAPORA = 24137


def calculate_endemic_channel(df: pd.DataFrame, target_year: int, historical_years: Optional[list] = None) -> pd.DataFrame:
    """
    Calcula o Canal Endêmico (Diagrama de Controle) por Semana Epidemiológica (1 a 53)
    seguindo a metodologia preconizada pela OPAS / Ministério da Saúde:
    - Anos anteriores ao ano alvo compõem a série histórica.
    - Faixas:
        * Limite Inferior (Zona de Êxito): Média - 1.96 * Desvio Padrão (ou Q1)
        * Média Histórica: Linha central
        * Limiar Epidêmico (Zona de Alerta/Epidemia): Média + 1.96 * Desvio Padrão (ou Q3)
    """
    if historical_years is None:
        all_years = sorted(df["NU_ANO"].dropna().unique())
        historical_years = [y for y in all_years if y < target_year]

    if not historical_years:
        # Se não houver anos anteriores suficientes, usa anos disponíveis exceto o target
        historical_years = [y for y in df["NU_ANO"].dropna().unique() if y != target_year]
        if not historical_years:
            historical_years = [target_year]

    # Agrupa casos por ano e semana epidemiológica
    # Considera casos notificados ou confirmados (conforme parâmetro)
    hist_df = df[df["NU_ANO"].isin(historical_years)]
    
    matrix = pd.DataFrame(index=range(1, 54), columns=historical_years).fillna(0)
    for y in historical_years:
        counts = hist_df[hist_df["NU_ANO"] == y].groupby("SE_NUM").size()
        for se, c in counts.items():
            if 1 <= se <= 53:
                matrix.loc[se, y] = c

    # Estatísticas por SE
    means = matrix.mean(axis=1)
    stds = matrix.std(axis=1).fillna(0)
    q1 = matrix.quantile(0.25, axis=1)
    q3 = matrix.quantile(0.75, axis=1)

    # Limiares
    upper_limit = np.maximum(means + 1.96 * stds, q3)
    lower_limit = np.maximum(0, means - 1.96 * stds)

    # Casos observados no ano alvo
    target_df = df[df["NU_ANO"] == target_year]
    target_counts = target_df.groupby("SE_NUM").size()

    result = pd.DataFrame({
        "SE": range(1, 54),
        "Limite_Inferior_Exito": lower_limit.round(1),
        "Media_Historica": means.round(1),
        "Limiar_Epidemico_Superior": upper_limit.round(1),
        "Casos_Observados": [target_counts.get(se, np.nan) for se in range(1, 54)]
    })

    return result


def forecast_cases(df: pd.DataFrame, steps_ahead: int = 6) -> Dict[str, Any]:
    """
    Gera previsão de casos para as próximas semanas epidemiológicas (4 a 8 semanas à frente)
    com base na série histórica semanal agregada.
    Utiliza Holt-Winters (Exponential Smoothing) com fallback para ARIMA.
    """
    # Cria chave Ano-SE ordenada
    grouped = df.groupby(["NU_ANO", "SE_NUM"]).size().reset_index(name="Casos")
    grouped = grouped.sort_values(by=["NU_ANO", "SE_NUM"]).reset_index(drop=True)

    if len(grouped) < 6:
        # Poucos dados para ajuste de modelo de série temporal complexo
        last_val = grouped["Casos"].iloc[-1] if len(grouped) > 0 else 0
        forecast_idx = [f"SE {i+1}" for i in range(steps_ahead)]
        return {
            "historical": grouped,
            "forecast_labels": forecast_idx,
            "forecast_values": [last_val] * steps_ahead,
            "lower_80": [max(0, last_val * 0.7)] * steps_ahead,
            "upper_80": [last_val * 1.3] * steps_ahead,
            "lower_95": [max(0, last_val * 0.5)] * steps_ahead,
            "upper_95": [last_val * 1.5] * steps_ahead,
            "model_name": "Projeção Linear Básica"
        }

    series = grouped["Casos"].astype(float).values
    last_year = int(grouped["NU_ANO"].iloc[-1])
    last_se = int(grouped["SE_NUM"].iloc[-1])

    forecast_labels = []
    curr_se = last_se
    curr_yr = last_year
    for _ in range(steps_ahead):
        curr_se += 1
        if curr_se > 52:
            curr_se = 1
            curr_yr += 1
        forecast_labels.append(f"{curr_yr}-SE{curr_se:02d}")

    model_used = "Holt-Winters"
    try:
        # Tenta Holt-Winters com amortecimento de tendência
        model = ExponentialSmoothing(
            series,
            trend="add",
            seasonal=None,
            damped_trend=True,
            initialization_method="estimated"
        ).fit()
        pred = model.forecast(steps_ahead)
        pred = np.maximum(0, pred)
        
        # Resíduos para calcular intervalos de confiança
        residuals = model.resid
        sigma = np.std(residuals) if len(residuals) > 0 else 5.0
    except Exception:
        try:
            # Fallback para ARIMA(1, 1, 1)
            model_used = "ARIMA(1,1,1)"
            model = ARIMA(series, order=(1, 1, 1)).fit()
            pred_res = model.get_forecast(steps_ahead)
            pred = np.maximum(0, pred_res.predicted_mean)
            ci = pred_res.conf_int(alpha=0.20)
            sigma = np.std(model.resid)
        except Exception:
            # Fallback para média móvel ponderada
            model_used = "Média Móvel Ponderada"
            weights = np.linspace(0.5, 1.0, min(5, len(series)))
            recent_mean = np.average(series[-len(weights):], weights=weights)
            pred = np.array([recent_mean] * steps_ahead)
            sigma = np.std(series[-6:]) if len(series) >= 6 else 3.0

    pred = np.maximum(0, np.round(pred, 1))
    
    # Intervalos de confiança aproximados
    step_factors = np.sqrt(np.arange(1, steps_ahead + 1))
    lower_80 = np.maximum(0, np.round(pred - 1.28 * sigma * step_factors, 1))
    upper_80 = np.round(pred + 1.28 * sigma * step_factors, 1)
    lower_95 = np.maximum(0, np.round(pred - 1.96 * sigma * step_factors, 1))
    upper_95 = np.round(pred + 1.96 * sigma * step_factors, 1)

    # Identificadores das semanas históricas recentes
    recent_grouped = grouped.tail(30).copy()
    recent_grouped["Label"] = recent_grouped["NU_ANO"].astype(str) + "-SE" + recent_grouped["SE_NUM"].apply(lambda s: f"{int(s):02d}")

    return {
        "historical": recent_grouped,
        "forecast_labels": forecast_labels,
        "forecast_values": pred.tolist(),
        "lower_80": lower_80.tolist(),
        "upper_80": upper_80.tolist(),
        "lower_95": lower_95.tolist(),
        "upper_95": upper_95.tolist(),
        "model_name": model_used
    }


def assess_epidemic_risk(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Avalia a Matriz de Risco Epidemiológico baseada na aceleração semana a semana (Delta SE),
    taxa de incidência e posicionamento no canal endêmico.
    Retorna nível de risco (Verde, Amarelo, Laranja, Vermelho), métricas e recomendações operacionais.
    """
    grouped = df.groupby(["NU_ANO", "SE_NUM"]).size().reset_index(name="Casos")
    grouped = grouped.sort_values(by=["NU_ANO", "SE_NUM"]).reset_index(drop=True)

    if len(grouped) == 0:
        return {
            "risk_level": "Verde",
            "color": "#10B981",
            "title": "Nível 1: Transmissão Baixa / Estável",
            "delta_se": 0.0,
            "cases_current": 0,
            "cases_previous": 0,
            "current_se": "N/A",
            "incidence_rate_4w": 0.0,
            "justification": "Sem registros suficientes para aferição de aceleração.",
            "recommendations": ["Manter vigilância entomológica e vistorias rotineiras."]
        }

    # Dados da última semana e semana anterior
    current_row = grouped.iloc[-1]
    prev_row = grouped.iloc[-2] if len(grouped) >= 2 else current_row
    
    curr_cases = int(current_row["Casos"])
    prev_cases = int(prev_row["Casos"])
    curr_se = f"{int(current_row['NU_ANO'])}-SE{int(current_row['SE_NUM']):02d}"

    # Delta SE percentual
    if prev_cases > 0:
        delta_se = ((curr_cases - prev_cases) / prev_cases) * 100.0
    else:
        delta_se = 100.0 if curr_cases > 0 else 0.0

    # Incidência acumulada nas últimas 4 semanas por 100k hab.
    recent_4w_cases = grouped.tail(4)["Casos"].sum()
    incid_4w = (recent_4w_cases / POPULACAO_ITAPORA) * 100000.0

    # Média móvel das últimas 3 semanas
    recent_3w_mean = grouped.tail(3)["Casos"].mean()

    # Determinação do nível de risco
    if incid_4w >= 300.0 or curr_cases >= 50 or delta_se >= 60.0:
        risk_level = "Vermelho"
        color = "#EF4444"
        title = "NÍVEL 4: ALERTA MÁXIMO / SURTO EPIDÊMICO"
        justification = (
            f"Forte aceleração de casos ({delta_se:+.1f}%) ou incidência crítica acumulada "
            f"({incid_4w:.1f} casos/100 mil hab.), caracterizando alta transmissibilidade."
        )
        recommendations = [
            "🚨 Ativação imediata do Comitê de Operações de Emergência em Saúde (COE Arboviroses).",
            "💨 Bloqueio químico imediato com Ultra Baixo Volume (UBV pesado/fumacê) nos bairros críticos.",
            "🏥 Ampliação de leitos de hidratação venosa e triagem com teste rápido de antígeno NS1.",
            "📢 Alerta geral à rede de atenção básica e reforço em mutirões de limpeza comunitária."
        ]
    elif incid_4w >= 100.0 or delta_se >= 25.0 or (curr_cases >= 20 and delta_se > 0):
        risk_level = "Laranja"
        color = "#F97316"
        title = "NÍVEL 3: RISCO ELEVADO / PRÉ-EPIDÊMICO"
        justification = (
            f"Crescimento semanal consistente (+{delta_se:.1f}%) e incidência moderada-alta "
            f"({incid_4w:.1f} casos/100 mil hab. em 4 semanas), indicando disseminação vetorial ativa."
        )
        recommendations = [
            "⚠️ Intensificação das vistorias focais e eliminação de depósitos de larvas por ACEs.",
            "💨 Aplicação de UBV costal nos quarteirões com notificações confirmadas nas últimas 48h.",
            "📊 Monitoramento diário de leitos hospitalares e disponibilidade de insumos laboratoriais.",
            "🗣️ Campanhas de conscientização nas escolas e mídia local de Itaporã."
        ]
    elif delta_se > 0 or incid_4w >= 50.0:
        risk_level = "Amarelo"
        color = "#F59E0B"
        title = "NÍVEL 2: ATENÇÃO / ACELERAÇÃO INICIAL"
        justification = (
            f"Variação positiva observada na semana ({delta_se:+.1f}%) ou incidência "
            f"em expansão ({incid_4w:.1f} casos/100 mil hab.)."
        )
        recommendations = [
            "🔍 Reforço na busca ativa de sintomáticos nos bairros com primeiros casos.",
            "🦟 Monitoramento do Índice de Infestação Predial (LIRAa/LIA) nos setores prioritários.",
            "⏱️ Redução do tempo entre início de sintomas e digitação das notificações no SINAN."
        ]
    else:
        risk_level = "Verde"
        color = "#10B981"
        title = "NÍVEL 1: TRANSMISSÃO BAIXA / CONTROLADA"
        justification = (
            f"Curva estável ou em declínio ({delta_se:+.1f}%) e incidência residual "
            f"({incid_4w:.1f} casos/100 mil hab.)."
        )
        recommendations = [
            "✅ Manutenção das ações permanentes de controle de criadouros.",
            "🔬 Investigação sorológica e oportuna de casos suspeitos isolados.",
            "📋 Atualização cadastral dos imóveis de pontos estratégicos (PEs)."
        ]

    return {
        "risk_level": risk_level,
        "color": color,
        "title": title,
        "delta_se": delta_se,
        "cases_current": curr_cases,
        "cases_previous": prev_cases,
        "current_se": curr_se,
        "incid_4w": incid_4w,
        "recent_3w_mean": recent_3w_mean,
        "justification": justification,
        "recommendations": recommendations
    }
