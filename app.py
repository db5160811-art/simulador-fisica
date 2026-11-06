"""Laboratorio interactivo: MCU, MCUA y rotación de discos duros HDD."""
import csv
import io
import math

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from fisica import (
    estado_circular,
    latencia_rotacional_max_ms,
    latencia_rotacional_media_ms,
    periodo_s_desde_rpm,
    rpm_a_rad_s,
    rpm_minimas_para_objetivo,
)

st.set_page_config(
    page_title="Laboratorio de movimiento circular",
    page_icon="🌀",
    layout="wide",
)

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; max-width: 1250px;}
.hero {padding: 1.3rem 1.5rem; border-radius: 18px;
 background: linear-gradient(100deg,#102644,#214d69); color:white; margin-bottom:1.3rem;}
.hero h1 {color:#fff; margin:0; font-size:2rem;}
.hero p {color:#d9ecfb; margin:.5rem 0 0;}
.small-note {font-size:.92rem; opacity:.85;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>🌀 Laboratorio de movimiento circular</h1>
<p>Explora el MCU y el MCUA. Compara las RPM y la espera de rotación de un disco duro mecánico.</p>
</div>
""", unsafe_allow_html=True)

pagina_sim, pagina_hdd, pagina_aprender = st.tabs(
    ["🔄 Simulador MCU / MCUA", "💽 Disco duro HDD", "📘 Conceptos y práctica"]
)


def figura_rotacion(radio: float, angulo: float, omega: float, alpha: float) -> go.Figure:
    """Dibujo ilustrativo: flechas indican DIRECCIÓN, no magnitud a escala."""
    theta = np.linspace(0, 2 * np.pi, 300)
    x, y = radio * math.cos(angulo), radio * math.sin(angulo)
    tang = np.array([-math.sin(angulo), math.cos(angulo)])
    normal = np.array([-math.cos(angulo), -math.sin(angulo)])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=radio*np.cos(theta), y=radio*np.sin(theta),
                             mode="lines", line=dict(color="#3b82f6", width=3),
                             name="Trayectoria"))
    fig.add_trace(go.Scatter(x=[0, x], y=[0, y], mode="lines", line=dict(color="#94a3b8", dash="dot"),
                             name="Radio"))
    fig.add_trace(go.Scatter(x=[x], y=[y], mode="markers", marker=dict(size=15, color="#f59e0b"),
                             name="Objeto"))

    def flecha(vec, etiqueta, color, escala):
        xf, yf = x+vec[0]*escala*radio, y+vec[1]*escala*radio
        fig.add_annotation(x=xf, y=yf, ax=x, ay=y, xref="x", yref="y",
                           axref="x", ayref="y", text="", showarrow=True,
                           arrowhead=3, arrowsize=1.4, arrowwidth=3, arrowcolor=color)
        fig.add_annotation(x=xf, y=yf, text=etiqueta, showarrow=False,
                           xshift=13, yshift=-10, font=dict(color=color, size=13))

    if abs(omega) > 1e-9:
        flecha(tang * np.sign(omega), "v", "#16a34a", 0.65)
        flecha(normal, "aₙ", "#dc2626", 0.65)
    if abs(alpha) > 1e-9:
        flecha(tang * np.sign(alpha), "aₜ", "#8b5cf6", 0.45)
    fig.update_layout(title="Posición y direcciones de los vectores", showlegend=False,
                      height=390, margin=dict(l=12, r=12, b=16, t=45),
                      xaxis=dict(visible=False, range=[-1.9*radio, 1.9*radio]),
                      yaxis=dict(visible=False, range=[-1.9*radio, 1.9*radio], scaleanchor="x", scaleratio=1))
    return fig


def grafica_serie(x, y, titulo, eje_y, color, tiempo_observado):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, name=titulo, mode="lines",
                             line=dict(color=color, width=3)))
    fig.add_vline(x=tiempo_observado, line_color="#94a3b8", line_dash="dot")
    fig.update_layout(title=titulo, xaxis_title="Tiempo (s)", yaxis_title=eje_y,
                      height=295, margin=dict(l=8, r=8, t=45, b=25),
                      hovermode="x", showlegend=False)
    return fig


with pagina_sim:
    st.subheader("1. Introduce los datos del movimiento")
    opcion = st.radio("Tipo de movimiento", ["MCU — velocidad angular constante",
                                                  "MCUA — aceleración angular constante"],
                          horizontal=True)
    es_mcua = opcion.startswith("MCUA")
    c1, c2, c3 = st.columns(3)
    radio_m = c1.number_input("Radio de la trayectoria (m)", min_value=0.001,
                              max_value=100.0, value=0.05, step=0.01, format="%.3f",
                              help="Distancia entre el eje y el punto que se estudia")
    rpm0 = c2.number_input("RPM iniciales (rev/min)", min_value=-15000.0,
                           max_value=15000.0, value=60.0,
                           step=60.0, help="Signo positivo: giro antihorario; negativo: horario")
    alpha = c3.number_input("Aceleración angular α (rad/s²)", min_value=-5000.0,
                            max_value=5000.0, value=2.0, step=0.5,
                            ) if es_mcua else 0.0
    if not es_mcua:
        c3.metric("Aceleración angular α", "0 rad/s²")
    c4, c5 = st.columns(2)
    duracion = c4.slider("Duración total de la simulación (s)", min_value=1.0, max_value=30.0,
                         value=5.0, step=0.5)
    instante = c5.slider("Instante a observar (s)", min_value=0.0, max_value=duracion,
                         value=min(2.0, duracion), step=0.001)

    e = estado_circular(radio_m, rpm0, alpha, instante)
    st.subheader("2. Resultados calculados")
    a, b, c, d = st.columns(4)
    a.metric("Velocidad angular", f"{e.velocidad_angular_rpm:,.2f} RPM")
    b.metric("Rapidez tangencial", f"{e.rapidez_tangencial_m_s:,.3f} m/s")
    c.metric("Aceleración centrípeta", f"{e.aceleracion_centripeta_m_s2:,.2f} m/s²")
    d.metric("Vueltas netas", f"{e.vueltas_netas:,.2f}")
    a2, b2, c2 = st.columns(3)
    a2.metric("Velocidad angular", f"{e.velocidad_angular_rad_s:,.3f} rad/s")
    b2.metric("Aceleración tangencial", f"{e.aceleracion_tangencial_m_s2:,.3f} m/s²")
    c2.metric("Aceleración total", f"{e.aceleracion_total_m_s2:,.2f} m/s²")

    period = periodo_s_desde_rpm(rpm0)
    if not es_mcua:
        x1, x2 = st.columns(2)
        x1.metric("Período T", f"{period:.6f} s" if period is not None else "No definido")
        x2.metric("Frecuencia f", f"{abs(rpm0)/60:.3f} Hz")
    else:
        st.caption("En MCUA la velocidad angular varía: no hay un período ni frecuencia únicos para todo el movimiento. Las vueltas indicadas son netas (con signo), no la distancia angular total.")

    st.subheader("3. Visualización")
    ts = np.linspace(0.0, duracion, 301)
    estados = [estado_circular(radio_m, rpm0, alpha, float(t)) for t in ts]
    graf_c, info_c = st.columns([1.05, 1])
    with graf_c:
        st.plotly_chart(figura_rotacion(radio_m, e.angulo_rad,
                                       e.velocidad_angular_rad_s, alpha),
                        use_container_width=True)
    with info_c:
        st.markdown("**¿Qué representan las flechas?**")
        st.markdown("🟢 **v:** velocidad tangencial, perpendicular al radio.  ")
        st.markdown("🔴 **aₙ:** aceleración centrípeta, dirigida hacia el centro.  ")
        st.markdown("🟣 **aₜ:** aceleración tangencial, si α ≠ 0.")
        st.caption("Las flechas indican dirección, no magnitudes dibujadas a escala. La posición depende del instante seleccionado.")
        st.markdown("**Ecuaciones aplicadas**")
        if es_mcua:
            st.latex(r"\omega=\omega_0+\alpha t\qquad \theta=\omega_0t+\frac12\alpha t^2")
        else:
            st.latex(r"\omega=\omega_0\qquad \theta=\omega t")
        st.latex(r"v=|\omega|r\qquad a_c=\omega^2r\qquad a_t=\alpha r")

    z1, z2 = st.columns(2)
    with z1:
        st.plotly_chart(grafica_serie(ts, [v.velocidad_angular_rpm for v in estados],
            "Velocidad angular", "RPM (con signo)", "#2563eb", instante), use_container_width=True)
        st.plotly_chart(grafica_serie(ts, [v.rapidez_tangencial_m_s for v in estados],
            "Rapidez tangencial", "m/s", "#16a34a", instante), use_container_width=True)
    with z2:
        st.plotly_chart(grafica_serie(ts, [v.vueltas_netas for v in estados],
            "Desplazamiento angular neto", "Vueltas", "#8b5cf6", instante), use_container_width=True)
        st.plotly_chart(grafica_serie(ts, [v.aceleracion_centripeta_m_s2 for v in estados],
            "Aceleración centrípeta", "m/s²", "#dc2626", instante), use_container_width=True)

    with st.expander("Descargar datos calculados (CSV)"):
        salida = io.StringIO()
        escritor = csv.writer(salida)
        escritor.writerow(["tiempo_s", "angulo_rad", "vueltas_netas", "omega_rad_s", "omega_rpm",
                           "rapidez_m_s", "acel_tangencial_m_s2", "acel_centripeta_m_s2"])
        for v in estados:
            escritor.writerow([v.tiempo_s, v.angulo_rad, v.vueltas_netas,
                              v.velocidad_angular_rad_s, v.velocidad_angular_rpm,
                              v.rapidez_tangencial_m_s, v.aceleracion_tangencial_m_s2,
                              v.aceleracion_centripeta_m_s2])
        st.download_button("📥 Descargar resultados", salida.getvalue(),
                           file_name="resultados_movimiento_circular.csv", mime="text/csv")

with pagina_hdd:
    st.subheader("Relación entre RPM y espera de lectura en un HDD")
    st.info("Este apartado realiza una comparación TEÓRICA; no controla las RPM del disco instalado ni mide su velocidad real de lectura.")
    st.markdown("En un disco mecánico de rotación prácticamente constante, el **período de una vuelta** es `60/RPM` segundos. Si el sector buscado se distribuye de manera uniforme respecto al cabezal, la **espera rotacional media** equivale aproximadamente a medio período.")
    st.latex(r"T_{\rm vuelta}\,(\mathrm{ms})=\frac{60000}{\mathrm{RPM}}\quad\quad L_{\rm media}\,(\mathrm{ms})\approx\frac{30000}{\mathrm{RPM}}")
    col_a, col_b = st.columns(2)
    rpm_min, rpm_max = col_a.slider("Rango de RPM que deseas comparar", min_value=3000,
                                    max_value=15000, value=(5400, 7200), step=100)
    objetivo = col_b.number_input("Objetivo de espera rotacional media máxima (ms)",
                                  min_value=0.5, max_value=30.0, value=5.0, step=0.5)
    rpm_necesarias = rpm_minimas_para_objetivo(objetivo)
    m1, m2, m3 = st.columns(3)
    m1.metric(f"A {rpm_min:,} RPM", f"{latencia_rotacional_media_ms(rpm_min):.2f} ms")
    m2.metric(f"A {rpm_max:,} RPM", f"{latencia_rotacional_media_ms(rpm_max):.2f} ms")
    m3.metric("RPM teóricas mínimas para el objetivo", f"{rpm_necesarias:,.0f}")
    if rpm_necesarias <= rpm_min:
        st.success("Todo el intervalo seleccionado cumple el objetivo de espera rotacional media teórica.")
    elif rpm_necesarias <= rpm_max:
        st.success(f"Dentro del intervalo seleccionado, aproximadamente desde {rpm_necesarias:,.0f} RPM se cumple el objetivo teórico.")
    else:
        st.warning("Ninguna velocidad del intervalo seleccionado cumple el objetivo teórico de espera rotacional media.")

    valores = np.linspace(rpm_min, rpm_max, 220)
    fig_hdd = go.Figure()
    fig_hdd.add_trace(go.Scatter(x=valores, y=30000/valores, mode="lines",
                                 name="Espera media", line=dict(color="#2563eb", width=4)))
    fig_hdd.add_hline(y=objetivo, line_dash="dash", line_color="#dc2626",
                      annotation_text=f"Objetivo: {objetivo:g} ms", annotation_position="top left")
    if rpm_min <= rpm_necesarias <= rpm_max:
        fig_hdd.add_vline(x=rpm_necesarias, line_dash="dot", line_color="#16a34a")
    fig_hdd.update_layout(title="Espera rotacional media estimada vs. RPM",
                          xaxis_title="Velocidad de rotación (RPM)",
                          yaxis_title="Espera rotacional media (ms)",
                          height=375, margin=dict(l=10, r=10, t=50, b=25))
    st.plotly_chart(fig_hdd, use_container_width=True)

    st.markdown("**Comparación de los extremos del intervalo**")
    st.table({
        "Magnitud": ["Vueltas por segundo (Hz)", "Tiempo de una vuelta (ms)",
                     "Espera rotacional media (ms)", "Espera rotacional máxima aprox. (ms)"],
        f"{rpm_min:,} RPM": [f"{rpm_min/60:,.2f}", f"{60000/rpm_min:,.2f}",
                            f"{latencia_rotacional_media_ms(rpm_min):,.2f}",
                            f"{latencia_rotacional_max_ms(rpm_min):,.2f}"],
        f"{rpm_max:,} RPM": [f"{rpm_max/60:,.2f}", f"{60000/rpm_max:,.2f}",
                            f"{latencia_rotacional_media_ms(rpm_max):,.2f}",
                            f"{latencia_rotacional_max_ms(rpm_max):,.2f}"],
    })
    st.warning("**Importante:** una menor espera rotacional no garantiza mayor rendimiento total. También influyen el tiempo de búsqueda del cabezal, la transferencia sostenida, caché, carga de trabajo, interfaz y el propio diseño del HDD. Un HDD no permite generalmente elegir sus RPM libremente por software. Un SSD no tiene platos giratorios: estas ecuaciones no se aplican a su almacenamiento.")

with pagina_aprender:
    st.subheader("Conceptos de física")
    st.markdown("""
    | Magnitud | MCU | MCUA |
    |---|---|---|
    | Velocidad angular ω | Constante | Cambia linealmente con el tiempo |
    | Aceleración angular α | Cero | Constante (puede ser negativa) |
    | Aceleración tangencial aₜ | Cero | αr |
    | Aceleración centrípeta a꜀ | ω²r (no necesariamente cero) | Cambia si cambia |ω| |
    | Velocidad tangencial | Perpendicular al radio | Perpendicular al radio; su magnitud puede cambiar |
    """)
    st.markdown("**Conversión de unidades**")
    st.latex(r"\omega\,(\mathrm{rad/s})=\mathrm{RPM}\,\frac{2\pi}{60}")
    st.markdown("En el MCU la rapidez puede ser constante, pero **la velocidad cambia de dirección**; por eso existe aceleración centrípeta. En MCUA, además, puede haber aceleración tangencial.")
    st.markdown("**Comprueba lo aprendido**")
    pregunta = st.radio("Si se duplican las RPM de un HDD, ¿qué ocurre con la espera rotacional media teórica?",
                        ["Se duplica", "Se reduce a la mitad", "No cambia"], index=None)
    if st.button("Comprobar respuesta", disabled=pregunta is None):
        if pregunta == "Se reduce a la mitad":
            st.success("¡Correcto! L_media = 30000/RPM, por lo que al duplicar el denominador la espera se reduce a la mitad.")
        else:
            st.error("Revisa la relación inversa: L_media = 30000/RPM.")
    st.caption("Modelo idealizado: no incluye rozamiento ni variaciones reales de giro en el simulador, ni procesos de lectura distintos de la espera rotacional en el apartado HDD.")

st.divider()
st.caption("Simulador educativo en Python · MCU y MCUA · Los valores sobre HDD son cálculos teóricos, no mediciones de hardware.")
