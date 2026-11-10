"""LOS OPTIMOS | Simulador didáctico de duopolio de Cournot.

Ejecutar: python -m streamlit run app.py
El cálculo matemático reside en modelo.py; las visualizaciones, en graficas.py.
"""
from __future__ import annotations

import html
import json
from datetime import datetime

import pandas as pd
import streamlit as st

from modelo import Mercado, equilibrio, reaccion1, reaccion2, evaluar, parametros, etiqueta_reaccion
from graficas import grafica_reacciones, grafica_beneficio, grafica_escenarios
from explicaciones import descripcion_cambios, curva_desplazada, diagnostico_decision

st.set_page_config(page_title="LOS OPTIMOS | Cournot", page_icon="📈", layout="wide",
                   initial_sidebar_state="expanded")

AZUL = "#2563eb"
VERDE = "#16a34a"
NARANJA = "#f59e0b"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
html, body, [class*="css"], [data-testid="stAppViewContainer"] { font-family: 'DM Sans', sans-serif; }
[data-testid="stAppViewContainer"] { background: linear-gradient(155deg,#f8fbff 0%,#ffffff 42%,#f4f8fd 100%); }
[data-testid="stSidebar"] { background: #f1f6fc; border-right:1px solid #dbe6f3; }
.block-container { padding-top: 1.35rem; padding-bottom: 4rem; max-width: 1380px; }
h1,h2,h3 {font-family:'Manrope',sans-serif !important;letter-spacing:-.025em; color:#10243b;}
h1 {font-weight:800 !important;}
[data-testid="stMetric"] {background: white; border:1px solid #e3ebf5; border-radius:15px; padding:15px 16px; box-shadow:0px 4px 14px #17395e0b;}
[data-testid="stMetricLabel"] {color:#556780; font-weight:600;}
[data-testid="stMetricValue"] {font-family:'Manrope',sans-serif; color:#10243b;}
.stTabs [data-baseweb="tab-list"] {gap:.4rem;overflow-x:auto;}
.stTabs [data-baseweb="tab"] {background:#eff4fb; border-radius:9px 9px 0 0;padding:12px 16px;}
.stTabs [aria-selected="true"] {background:#dceafb; color:#103a68;}
.stButton>button[kind="primary"] {background:linear-gradient(115deg,#153b70,#2563eb);border:0;box-shadow:0 6px 14px #1554ab28;}
.stButton>button {border-radius:10px;}
.hero {background:linear-gradient(110deg,#0d2340,#153d70 65%,#2057a3);border-radius:24px;color:#fff;padding:38px 42px;margin-bottom:20px;box-shadow:0px 18px 36px #13365a22;}
.hero h1 {color:white !important;font-size:clamp(2.3rem,4vw,3.8rem);margin:0 0 .4rem;font-weight:800;}
.hero p{color:#d7e7ff;max-width:780px;line-height:1.6;font-size:1.08rem;}
.hero .eyebrow {color:#9dc7ff; font-size:.84rem;font-weight:700;letter-spacing:.15em;text-transform:uppercase;}
.soft-card {background:#fff;border:1px solid #e1eaf6;border-radius:16px;padding:19px 20px;min-height:116px;box-shadow:0 5px 18px #16376009;margin-bottom:12px;}
.soft-card .kicker {font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:#71839a;}
.soft-card .big {font-family:Manrope,sans-serif;font-size:1.28rem;font-weight:800;color:#123558;margin-top:.4rem;}
.soft-card p {color:#53667b;font-size:.92rem;margin:9px 0 0;}
.section-intro {color:#5e728a;margin-top:-.4rem;margin-bottom:1.1rem;}
.note{border-left:4px solid #7ba7ed;background:#eef5ff;color:#244a75;border-radius:6px;padding:12px 16px;margin:8px 0 15px;}
.positive{border-left-color:#19a36c;background:#edfaf3;color:#16714e;}
.warning{border-left-color:#f39b3b;background:#fff6e7;color:#895414;}
.footerline{color:#8b9ab0;font-size:.78rem;margin-top:28px;text-align:center}
@media (max-width:700px) {.hero{padding:25px 20px;border-radius:16px}.block-container{padding-left:.9rem;padding-right:.9rem}}
</style>
""", unsafe_allow_html=True)

INICIAL = Mercado()


def box(titulo: str, valor: str, descripcion: str = "") -> None:
    st.markdown(
        f'<div class="soft-card"><div class="kicker">{html.escape(titulo)}</div>'
        f'<div class="big">{html.escape(valor)}</div><p>{html.escape(descripcion)}</p></div>',
        unsafe_allow_html=True,
    )


def banner(texto: str, estilo: str = "") -> None:
    st.markdown(f'<div class="note {estilo}">{html.escape(texto)}</div>', unsafe_allow_html=True)


def cambio(valor, referencia) -> str:
    diferencia = valor-referencia
    return f"{diferencia:+.2f} vs. referencia"


def resetear():
    for campo, x in parametros(INICIAL).items():
        st.session_state[f"input_{campo}"] = float(x)
        st.session_state[f"slider_{campo}"] = float(x)


def sincronizar(campo: str, origen: str):
    destino = "slider" if origen == "input" else "input"
    st.session_state[f"{destino}_{campo}"] = st.session_state[f"{origen}_{campo}"]


def mostrar_control(campo, titulo, minimo, maximo, step):
    if f"input_{campo}" not in st.session_state:
        x = float(getattr(INICIAL, campo))
        st.session_state[f"input_{campo}"] = x
        st.session_state[f"slider_{campo}"] = x
    with st.sidebar:
        izquierda, derecha = st.columns([1.2, .8])
        with izquierda:
            st.slider(titulo, min_value=float(minimo), max_value=float(maximo),
                      step=float(step), key=f"slider_{campo}",
                      on_change=sincronizar, args=(campo, "slider"))
        with derecha:
            st.number_input(f"Valor {campo}", min_value=float(minimo), max_value=float(maximo),
                            step=float(step), key=f"input_{campo}",
                            on_change=sincronizar, args=(campo, "input"),
                            format="%.1f" if campo == "b" else "%.2f")


def guardar(nombre: str, mercado: Mercado):
    nombre = nombre.strip()[:55]
    if not nombre:
        st.warning("Escribe un nombre para guardar el escenario.")
        return
    st.session_state.escenarios[nombre] = parametros(mercado)
    st.success(f"Escenario «{nombre}» guardado en esta sesión.")


def a_mercado(dic):
    return Mercado(a=float(dic["a"]), b=float(dic["b"]),
                   c1=float(dic["c1"]), c2=float(dic["c2"]))


def formato_cambio(actual, inicial):
    return f"{actual:.2f} ({actual-inicial:+.2f})"


st.session_state.setdefault("iniciado", False)
st.session_state.setdefault("escenarios", {})

st.markdown("""<div class="hero"><div class="eyebrow">Universidad de La Sabana · Microeconomía II · Taller 5 / Reto 4</div>
<h1>LOS OPTIMOS</h1>
<p>Simulador de duopolio de Cournot. Explora cómo las decisiones de producción de dos empresas cambian cuando varían los costos, la demanda y la cantidad producida por su rival.</p>
</div>""", unsafe_allow_html=True)

if not st.session_state.iniciado:
    izq, centro, der = st.columns(3)
    with izq:
        box("01 · Experimenta", "Cambia el mercado", "Modifica costos y demanda en tiempo real.")
    with centro:
        box("02 · Compite", "Sé el gerente", "Encuentra tu mejor respuesta frente al rival.")
    with der:
        box("03 · Interpreta", "Entiende el equilibrio", "Compara precios, producción y beneficios.")
    st.write("")
    if st.button("Comenzar simulación  →", type="primary", use_container_width=True):
        st.session_state.iniciado = True
        st.rerun()
    st.caption("Modelo académico de demanda inversa lineal, costos marginales constantes y producción no negativa.")
    st.stop()

with st.sidebar:
    st.markdown("### ⚙️ Panel de mercado")
    st.caption("Cambia un deslizador o escribe un valor. Los resultados se recalculan automáticamente.")
    if st.button("↺ Restablecer parámetros", use_container_width=True):
        resetear()
        st.rerun()

mostrar_control("a", "Demanda (a)", 10, 300, 1)
mostrar_control("b", "Pendiente (b)", .1, 10, .1)
mostrar_control("c1", "Costo empresa 1 (c₁)", 0, 300, 1)
mostrar_control("c2", "Costo empresa 2 (c₂)", 0, 300, 1)

m = Mercado(*(float(st.session_state[f"input_{x}"]) for x in ("a", "b", "c1", "c2")))
r = equilibrio(m)

referencias = {"Inicial (a=100, b=1, c₁=20, c₂=20)": INICIAL}
for nombre, dic in st.session_state.escenarios.items():
    referencias[f"Guardado · {nombre}"] = a_mercado(dic)

with st.sidebar:
    st.divider()
    st.markdown("#### 🔁 Comparar curvas")
    nombre_ref = st.selectbox("Escenario de referencia", list(referencias),
                             help="Las curvas discontinuas y las diferencias toman este escenario como punto de partida.")
    referencia = referencias[nombre_ref]
    mostrar_ref = st.toggle("Mostrar referencia en gráfica", value=True)
    st.caption("Las cantidades son unidades de producto y el precio/beneficio usan unidades monetarias genéricas.")

pestanas = st.tabs(["🏠 Resumen", "📉 Reacciones y equilibrio", "🎮 Decisión individual",
                    "📊 Resultados", "🧪 Escenarios", "📖 Aprende"])

with pestanas[0]:
    st.subheader("Radiografía del mercado")
    st.markdown('<p class="section-intro">El equilibrio surge cuando ninguna empresa puede ganar más cambiando sola su producción.</p>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Producción empresa 1", f"{r.q1:.2f}", cambio(r.q1, equilibrio(referencia).q1))
    with c2: st.metric("Producción empresa 2", f"{r.q2:.2f}", cambio(r.q2, equilibrio(referencia).q2))
    with c3: st.metric("Precio de mercado", f"{r.precio:.2f}", cambio(r.precio, equilibrio(referencia).precio))
    with c4: st.metric("Producción total", f"{r.q_total:.2f}", cambio(r.q_total, equilibrio(referencia).q_total))
    ciz,cde = st.columns([1.55, 1], gap="large")
    with ciz:
        st.plotly_chart(grafica_reacciones(m, referencia if mostrar_ref else None), use_container_width=True,
                        key="grafica_resumen")
    with cde:
        st.markdown("#### Lo que está pasando")
        st.markdown(f"**Tipo de equilibrio:** {r.tipo}.")
        for texto in descripcion_cambios(m, referencia):
            st.write("• " + texto)
        banner(curva_desplazada(m, referencia))
        st.caption("La reacción de la empresa 1 se grafica como q₁=R₁(q₂) (eje X); la de la empresa 2 como q₂=R₂(q₁) (eje Y).")
    st.markdown("#### Beneficios al equilibrio")
    b1,b2 = st.columns(2)
    with b1: st.metric("Beneficio empresa 1", f"{r.beneficio1:,.2f}")
    with b2: st.metric("Beneficio empresa 2", f"{r.beneficio2:,.2f}")

with pestanas[1]:
    st.subheader("Funciones de reacción y equilibrio")
    st.markdown('<p class="section-intro">Cada curva contiene las cantidades que maximizan el beneficio de una empresa, dada la producción de la otra.</p>', unsafe_allow_html=True)
    k1,k2 = st.columns(2)
    with k1:
        st.markdown("**Empresa 1 · Curva azul (R₁)**")
        st.code(etiqueta_reaccion(m, 1), language=None)
    with k2:
        st.markdown("**Empresa 2 · Curva verde (R₂)**")
        st.code(etiqueta_reaccion(m, 2), language=None)
    st.plotly_chart(grafica_reacciones(m, referencia if mostrar_ref else None), use_container_width=True,
                    key="grafica_reacciones")
    banner(curva_desplazada(m, referencia), "positive")
    st.markdown("#### Prueba la mejor respuesta")
    una, dos = st.columns(2)
    with una:
        q2_exog = st.slider("Si la empresa 2 produce q₂…", 0.0,
                           max(1.0, float(m.a/m.b)), float(min(r.q2,m.a/m.b)), .1,
                           key="rival_2_exog")
        st.metric("Mejor respuesta de empresa 1", f"{reaccion1(m,q2_exog):.2f}")
    with dos:
        q1_exog = st.slider("Si la empresa 1 produce q₁…", 0.0,
                           max(1.0, float(m.a/m.b)), float(min(r.q1,m.a/m.b)), .1,
                           key="rival_1_exog")
        st.metric("Mejor respuesta de empresa 2", f"{reaccion2(m,q1_exog):.2f}")
    st.caption("Las funciones de reacción truncadas en cero incorporan las restricciones q₁ ≥ 0 y q₂ ≥ 0.")
    if "Esquina" in r.tipo:
        banner("Caso de esquina: al menos una empresa produce cero. Se usa la mejor respuesta no negativa, no las fórmulas interiores.", "warning")
    else:
        st.info("Caso interior: ambas empresas producen y se cumplen simultáneamente las condiciones de primer orden.")

with pestanas[2]:
    st.subheader("Tú decides cuánto producir")
    st.markdown('<p class="section-intro">Eres gerente: elige una cantidad y compárala con la mejor respuesta y con el equilibrio de Nash-Cournot.</p>', unsafe_allow_html=True)
    empresa = st.radio("Controlas a…", [1, 2], horizontal=True, format_func=lambda x:f"Empresa {x}")
    usar_eq = st.toggle("Usar la cantidad de equilibrio de la empresa rival", value=True,
                       help="Si se desactiva, puedes fijar la producción del competidor manualmente.")
    rival_eq = r.q2 if empresa == 1 else r.q1
    if usar_eq:
        q_rival = rival_eq
        st.caption(f"El rival mantiene q = {q_rival:.2f}, su cantidad de equilibrio actual.")
    else:
        max_rival = float(max(0.0, m.a / m.b))
        st.session_state.setdefault("q_rival_manual", min(rival_eq, max_rival))
        st.session_state.q_rival_manual = min(max(0.0,st.session_state.q_rival_manual),max_rival)
        q_rival = st.slider("Cantidad del competidor", 0.0, max(1.0,max_rival),
                            key="q_rival_manual", step=.1)
    mejor = reaccion1(m,q_rival) if empresa == 1 else reaccion2(m,q_rival)
    max_propia = max(0.0, m.a/m.b - q_rival)
    # Para no utilizar la parte de demanda lineal con precio negativo, Q <= a/b.
    if max_propia <= 1e-9:
        q_elegida = 0.0
        st.info("El rival ya satisface toda la demanda a precio no negativo; en este escenario tu producción disponible es cero.")
    else:
        st.session_state.setdefault("q_elegida_manual", min(mejor, max_propia))
        st.session_state.q_elegida_manual = max(0.0, min(st.session_state.q_elegida_manual,max_propia))
        q_elegida = st.slider("Tu cantidad de producción", 0.0, float(max_propia),
                              step=.1, key="q_elegida_manual")
    q1_esc, q2_esc = (q_elegida, q_rival) if empresa==1 else (q_rival,q_elegida)
    manual = evaluar(m, q1_esc, q2_esc, "Decisión manual")
    escenario_optimo = (evaluar(m,mejor,q_rival) if empresa==1 else
                        evaluar(m,q_rival,mejor))
    beneficio_real = manual.beneficio1 if empresa==1 else manual.beneficio2
    beneficio_optimo = (escenario_optimo.beneficio1 if empresa==1 else escenario_optimo.beneficio2)
    equi_empresa = r.q1 if empresa==1 else r.q2
    k1,k2,k3 = st.columns(3)
    with k1: st.metric("Tu decisión", f"{q_elegida:.2f}")
    with k2: st.metric("Mejor respuesta", f"{mejor:.2f}")
    with k3: st.metric("Cantidad en Cournot", f"{equi_empresa:.2f}")
    ciz,cde = st.columns([1.25, 1],gap="large")
    with ciz:
        st.plotly_chart(grafica_beneficio(m,empresa,q_rival,q_elegida),
                        use_container_width=True, key="grafica_beneficio")
    with cde:
        st.metric("Beneficio con tu decisión", f"{beneficio_real:,.2f}")
        st.metric("Beneficio con mejor respuesta", f"{beneficio_optimo:,.2f}")
        st.metric("Beneficio que dejas de ganar", f"{max(0.0,beneficio_optimo-beneficio_real):,.2f}")
        banner(diagnostico_decision(q_elegida,mejor,equi_empresa),
               "positive" if abs(q_elegida-mejor)<.05 else "warning")
    st.caption("Se supone que la cantidad del rival está fija. Tu elección no obliga al competidor a reaccionar en este ejercicio individual.")
    st.session_state["ultima_decision"] = {"empresa": empresa,"q1": q1_esc,"q2": q2_esc}

with pestanas[3]:
    st.subheader("Resultados económicos")
    st.markdown('<p class="section-intro">Todos los importes se calculan con P=a−bQ, Iᵢ=Pqᵢ, Cᵢ=cᵢqᵢ y πᵢ=Iᵢ−Cᵢ.</p>',unsafe_allow_html=True)
    st.markdown("#### Equilibrio de Cournot")
    a1,a2,a3,a4=st.columns(4)
    with a1:st.metric("q₁*",f"{r.q1:.2f}")
    with a2:st.metric("q₂*",f"{r.q2:.2f}")
    with a3:st.metric("Q*",f"{r.q_total:.2f}")
    with a4:st.metric("P*",f"{r.precio:.2f}")
    d1,d2=st.columns(2)
    with d1:st.metric("π₁*",f"{r.beneficio1:,.2f}")
    with d2:st.metric("π₂*",f"{r.beneficio2:,.2f}")
    st.markdown("#### Comparación con la última decisión manual")
    ultimo = st.session_state.get("ultima_decision",{"empresa":1,"q1":r.q1,"q2":r.q2})
    manual_res = evaluar(m,ultimo["q1"],ultimo["q2"],"Decisión manual")
    campos = [("Producción empresa 1","q1"),("Producción empresa 2","q2"),
              ("Producción total","q_total"),("Precio de mercado","precio"),
              ("Ingresos empresa 1","ingreso1"),("Ingresos empresa 2","ingreso2"),
              ("Costos empresa 1","costo1"),("Costos empresa 2","costo2"),
              ("Beneficio empresa 1","beneficio1"),("Beneficio empresa 2","beneficio2")]
    df = pd.DataFrame([{"Indicador":nombre,"Equilibrio":round(getattr(r,clave),2),
                        "Decisión manual":round(getattr(manual_res,clave),2),
                        "Cambio manual − equilibrio":round(getattr(manual_res,clave)-getattr(r,clave),2)}
                       for nombre,clave in campos])
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("Descargar resultados (CSV)", df.to_csv(index=False).encode("utf-8-sig"),
                       file_name="los_optimos_resultados.csv", mime="text/csv")
    banner(f"Equilibrio: {r.tipo}. La comparación manual se calcula manteniendo las cantidades que seleccionaste en la pestaña «Decisión individual».")

with pestanas[4]:
    st.subheader("Laboratorio de escenarios")
    st.markdown('<p class="section-intro">Compara cambios de costos y demanda. Guarda tus propios parámetros y expórtalos para reutilizarlos.</p>', unsafe_allow_html=True)
    nombre = st.text_input("Nombre de tu escenario", value=f"Mi escenario {len(st.session_state.escenarios)+1}", max_chars=55)
    cguardar, cexportar = st.columns([1,1])
    with cguardar:
        if st.button("💾 Guardar escenario actual", use_container_width=True):
            if len(st.session_state.escenarios)>=30 and nombre not in st.session_state.escenarios:
                st.error("Máximo 30 escenarios guardados. Borra alguno antes de continuar.")
            else:
                guardar(nombre,m)
    with cexportar:
        json_export = json.dumps({"proyecto":"LOS OPTIMOS","escenarios":st.session_state.escenarios},
                                  indent=2,ensure_ascii=False)
        st.download_button("⬇️ Exportar escenarios (JSON)",json_export.encode("utf-8"),
                           file_name="los_optimos_escenarios.json",mime="application/json",
                           use_container_width=True)
    with st.expander("📂 Importar escenarios guardados / eliminar"):
        importado=st.file_uploader("Cargar archivo JSON exportado", type="json")
        if importado is not None and st.button("Importar archivo"):
            try:
                raw=json.loads(importado.getvalue().decode("utf-8"))
                if not isinstance(raw,dict) or not isinstance(raw.get("escenarios"),dict):
                    raise ValueError("No corresponde a una exportación de LOS OPTIMOS.")
                nuevos={}
                for nombre_i,dic in list(raw["escenarios"].items())[:30]:
                    if not isinstance(nombre_i,str) or not isinstance(dic,dict):
                        raise ValueError("Formato de escenario inválido.")
                    nuevo=a_mercado(dic)
                    if not (10<=nuevo.a<=300 and .1<=nuevo.b<=10 and 0<=nuevo.c1<=300 and 0<=nuevo.c2<=300):
                        raise ValueError("Hay parámetros fuera de los límites de la interfaz.")
                    nuevos[nombre_i[:55]]=parametros(nuevo)
                st.session_state.escenarios.update(nuevos)
                st.success(f"Se importaron {len(nuevos)} escenarios.")
            except (ValueError,UnicodeDecodeError,TypeError,KeyError,OverflowError) as err:
                st.error(f"No se pudo importar: {err}")
        if st.session_state.escenarios:
            quitar=st.selectbox("Eliminar guardado",list(st.session_state.escenarios),key="quitar_escenario")
            if st.button("Eliminar escenario seleccionado"):
                del st.session_state.escenarios[quitar]
                st.rerun()
    base = INICIAL
    casos = {
        "Inicial":base,
        "↑ Costo E1": Mercado(base.a,base.b,min(300,base.c1+15),base.c2),
        "↓ Costo E2": Mercado(base.a,base.b,base.c1,max(0,base.c2-10)),
        "↑ Demanda": Mercado(min(300,base.a+20),base.b,base.c1,base.c2),
        "Actual":m,
    }
    for nombre_guardado, dic_guardado in st.session_state.escenarios.items():
        casos[f"Guardado · {nombre_guardado}"]=a_mercado(dic_guardado)
    disponibles=list(casos)
    elegidos=st.multiselect("Escenarios a comparar", disponibles,
                            default=disponibles[:5],max_selections=10)
    if elegidos:
        mostrar={n:casos[n] for n in elegidos}
        ref=equilibrio(INICIAL)
        filas=[]
        for caso,modelo in mostrar.items():
            rc=equilibrio(modelo)
            filas.append({"Escenario":caso, "a":modelo.a,"b":modelo.b,"c₁":modelo.c1,"c₂":modelo.c2,
                          "R₁(q₂)":etiqueta_reaccion(modelo,1),
                          "R₂(q₁)":etiqueta_reaccion(modelo,2),
                          "q₁*":round(rc.q1,2),"q₂*":round(rc.q2,2),
                          "Q*":round(rc.q_total,2),"P*":round(rc.precio,2),
                          "π₁*":round(rc.beneficio1,2),"π₂*":round(rc.beneficio2,2),
                          "Δq₁":round(rc.q1-ref.q1,2),"Δq₂":round(rc.q2-ref.q2,2),
                          "ΔP":round(rc.precio-ref.precio,2),
                          "Δπ₁":round(rc.beneficio1-ref.beneficio1,2),
                          "Δπ₂":round(rc.beneficio2-ref.beneficio2,2),"Tipo":rc.tipo})
        st.dataframe(pd.DataFrame(filas), use_container_width=True,hide_index=True)
        st.plotly_chart(grafica_escenarios(mostrar),use_container_width=True,key="grafica_escenarios")
        st.download_button("Exportar comparación (CSV)", pd.DataFrame(filas).to_csv(index=False).encode("utf-8-sig"),
                           file_name="los_optimos_comparacion.csv",mime="text/csv")
        st.markdown("**Lectura económica para el escenario actual frente al inicial:**")
        for texto in descripcion_cambios(m,INICIAL):st.write("• " + texto)
        st.caption("Los Δ se calculan siempre contra el caso inicial (100, 1, 20, 20). Las curvas se pueden superponer en «Reacciones y equilibrio» eligiendo una referencia guardada.")
    else:
        st.info("Selecciona al menos un escenario para ver la tabla y la gráfica.")

with pestanas[5]:
    st.subheader("¿Cómo funciona el simulador?")
    st.markdown("""
**¿Qué es un duopolio?** Un mercado con dos empresas oferentes.

**¿Qué es Cournot?** Cada empresa elige una **cantidad** de forma simultánea, tomando como dada la cantidad de su rival. El precio se determina por la producción conjunta.

**¿Qué es una función de reacción?** La cantidad que maximiza el beneficio de una empresa para cada nivel de producción de su competidor.

**¿Qué significa el equilibrio?** Ambas empresas están en su mejor respuesta: ninguna puede mejorar su beneficio cambiando unilateralmente su cantidad.

**¿Por qué importa el rival?** Como el precio es **P = a − b(q₁ + q₂)**, si tu rival produce más, el precio de mercado disminuye. Normalmente eso reduce la cantidad que te conviene producir.
""")
    st.divider()
    st.markdown("#### Modelo y supuestos")
    st.latex(r"P=a-b(q_1+q_2),\qquad C_i(q_i)=c_iq_i")
    st.latex(r"\pi_i=(a-b(q_1+q_2)-c_i)q_i")
    st.latex(r"BR_1(q_2)=\max\left\{0,\frac{a-c_1-bq_2}{2b}\right\}")
    st.latex(r"BR_2(q_1)=\max\left\{0,\frac{a-c_2-bq_1}{2b}\right\}")
    st.markdown("En un **equilibrio interior** (solo si ambas cantidades son positivas):")
    st.latex(r"q_1^*=\frac{a-2c_1+c_2}{3b},\quad q_2^*=\frac{a-2c_2+c_1}{3b}")
    st.latex(r"P^*=\frac{a+c_1+c_2}{3},\quad \pi_i^*=(P^*-c_i)q_i^*")
    st.info("Si una fórmula interior arroja una cantidad no positiva, el simulador comprueba casos de esquina y verifica simultáneamente las dos mejores respuestas. Nunca presenta cantidades negativas como equilibrio.")
    st.markdown("#### Guía rápida")
    st.markdown("""
1. Pulsa **Comenzar simulación** en la portada (si acabas de abrir la aplicación).
2. Usa el **panel izquierdo** para modificar demanda y costos; cada cambio actualiza los cálculos.
3. En **Reacciones y equilibrio**, mueve las cantidades del competidor para observar las mejores respuestas; compara curvas sólidas y discontinuas.
4. En **Decisión individual**, selecciona una empresa, elige la cantidad rival y decide tu producción. Compara tu beneficio con el máximo posible.
5. En **Resultados**, consulta ingresos, costos, beneficios y compara con tu decisión manual.
6. En **Escenarios**, guarda tus parámetros, compara alternativas y exporta/importa un archivo JSON.
7. Para comparar las curvas de un escenario guardado, selecciónalo en **Comparar curvas**, en la barra lateral.
""")
    st.caption("El modelo es didáctico: demanda lineal, firmas sin costos fijos, costos marginales constantes, información completa y decisiones simultáneas. No modela Bertrand, Stackelberg ni dinámica temporal.")

st.markdown('<div class="footerline">LOS OPTIMOS · Modelo de Cournot · Universidad de La Sabana · Desarrollo local con Python, Streamlit y Plotly</div>', unsafe_allow_html=True)
