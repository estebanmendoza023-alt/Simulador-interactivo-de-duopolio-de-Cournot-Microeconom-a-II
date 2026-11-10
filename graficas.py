"""Gráficas interactivas Plotly para LOS OPTIMOS."""
import numpy as np
import plotly.graph_objects as go
from modelo import Mercado, equilibrio, reaccion1, reaccion2

AZUL = "#2563EB"
VERDE = "#16A34A"
AZUL_ANTERIOR = "#91A9D0"
VERDE_ANTERIOR = "#8FD5B0"
NARANJA = "#F59E0B"
ROJO = "#EF4444"
OSCURO = "#10243B"


def estilo(fig, altura=430):
    fig.update_layout(
        template="plotly_white", height=altura,
        margin=dict(l=18, r=18, t=35, b=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(248,250,252,1)",
        font=dict(family="Arial, sans-serif", color=OSCURO),
        legend=dict(orientation="h", y=1.14, x=0, bgcolor="rgba(255,255,255,0)"),
        hovermode="closest",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#E6EDF5", zerolinecolor="#BAC8D8")
    fig.update_yaxes(showgrid=True, gridcolor="#E6EDF5", zerolinecolor="#BAC8D8")
    return fig


def grafica_reacciones(actual: Mercado, referencia: Mercado | None = None) -> go.Figure:
    """Convención rigurosa de ejes: X=q1, Y=q2.
    R1 se parametriza por Y=q2 y se dibuja X=BR1(Y).
    R2 se parametriza por X=q1 y se dibuja Y=BR2(X).
    """
    modelos = [actual] + ([referencia] if referencia is not None else [])
    max_q = max(max(m.a / m.b, equilibrio(m).q1, equilibrio(m).q2) for m in modelos)
    limite = max(1.0, max_q * 1.04)
    valores = np.linspace(0, limite, 260)
    fig = go.Figure()
    if referencia is not None:
        ref = equilibrio(referencia)
        fig.add_trace(go.Scatter(
            x=[reaccion1(referencia, y) for y in valores], y=valores,
            name="R₁ de referencia", mode="lines",
            line=dict(color=AZUL_ANTERIOR, width=2.5, dash="dash"),
            hovertemplate="R₁ referencia<br>q₁=%{x:.2f}<br>q₂=%{y:.2f}<extra></extra>"))
        fig.add_trace(go.Scatter(
            x=valores, y=[reaccion2(referencia, x) for x in valores],
            name="R₂ de referencia", mode="lines",
            line=dict(color=VERDE_ANTERIOR, width=2.5, dash="dash"),
            hovertemplate="R₂ referencia<br>q₁=%{x:.2f}<br>q₂=%{y:.2f}<extra></extra>"))
        fig.add_trace(go.Scatter(
            x=[ref.q1], y=[ref.q2], mode="markers", name="Equilibrio de referencia",
            marker=dict(size=12, color="#8590A5", symbol="circle-open", line=dict(width=2)),
            hovertemplate="Referencia (%{x:.2f}, %{y:.2f})<extra></extra>"))
    eq = equilibrio(actual)
    fig.add_trace(go.Scatter(
        x=[reaccion1(actual, y) for y in valores], y=valores,
        name="R₁ actual", mode="lines", line=dict(color=AZUL, width=4),
        hovertemplate="R₁ actual<br>q₁=%{x:.2f}<br>q₂=%{y:.2f}<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=valores, y=[reaccion2(actual, x) for x in valores],
        name="R₂ actual", mode="lines", line=dict(color=VERDE, width=4),
        hovertemplate="R₂ actual<br>q₁=%{x:.2f}<br>q₂=%{y:.2f}<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=[eq.q1], y=[eq.q2], mode="markers+text",
        text=[f"E ({eq.q1:.2f}, {eq.q2:.2f})"], textposition="top right",
        name="Equilibrio actual", marker=dict(size=16, color=NARANJA,
                                             line=dict(color="white", width=2)),
        hovertemplate="Equilibrio actual<br>q₁=%{x:.2f}<br>q₂=%{y:.2f}<extra></extra>"))
    fig.update_xaxes(title="Producción empresa 1 (q₁)", range=[-limite*.025, limite])
    fig.update_yaxes(title="Producción empresa 2 (q₂)", range=[-limite*.025, limite])
    return estilo(fig, 490)


def grafica_beneficio(m: Mercado, empresa: int, rival: float, elegido: float) -> go.Figure:
    from modelo import evaluar
    limite = max(0.0, (m.a / m.b) - rival)
    q = np.linspace(0, max(1e-6, limite), 200)
    mejor = reaccion1(m, rival) if empresa == 1 else reaccion2(m, rival)
    ganancia = lambda z: ((m.a - m.b*(z+rival) -
                          (m.c1 if empresa == 1 else m.c2))*z)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=q, y=[ganancia(z) for z in q], name="Beneficio según producción",
                             mode="lines", line=dict(color=AZUL, width=3),
                             hovertemplate="q=%{x:.2f}<br>Beneficio=%{y:.2f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=[mejor], y=[ganancia(mejor)], name="Mejor respuesta",
                             mode="markers", marker=dict(color=VERDE, size=14)))
    fig.add_trace(go.Scatter(x=[elegido], y=[ganancia(elegido)], name="Tu decisión",
                             mode="markers", marker=dict(color=NARANJA, size=14, symbol="diamond")))
    fig.update_xaxes(title="Cantidad de la empresa controlada")
    fig.update_yaxes(title="Beneficio de la empresa")
    return estilo(fig, 380)


def grafica_escenarios(escenarios: dict) -> go.Figure:
    """Barras comparadas para cantidades y precios (beneficios van en tabla)."""
    nombres = list(escenarios)
    resultados = [equilibrio(v) for v in escenarios.values()]
    fig = go.Figure()
    for campo, nombre, color in [("q1", "Producción E1", AZUL),
                                 ("q2", "Producción E2", VERDE),
                                 ("precio", "Precio", NARANJA)]:
        fig.add_trace(go.Bar(x=nombres, y=[getattr(r, campo) for r in resultados],
                             name=nombre, marker_color=color))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title="Cantidades / precio (unidades propias)")
    return estilo(fig, 400)
