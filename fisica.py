"""Modelo físico puro del simulador (sin dependencias externas)."""
from dataclasses import dataclass
from math import pi, hypot


@dataclass(frozen=True)
class EstadoCircular:
    tiempo_s: float
    angulo_rad: float
    velocidad_angular_rad_s: float
    velocidad_angular_rpm: float
    velocidad_tangencial_m_s: float
    rapidez_tangencial_m_s: float
    aceleracion_tangencial_m_s2: float
    aceleracion_centripeta_m_s2: float
    aceleracion_total_m_s2: float
    vueltas_netas: float


def rpm_a_rad_s(rpm: float) -> float:
    return rpm * 2.0 * pi / 60.0


def rad_s_a_rpm(rad_s: float) -> float:
    return rad_s * 60.0 / (2.0 * pi)


def estado_circular(radio_m: float, rpm_inicial: float, alpha_rad_s2: float, tiempo_s: float) -> EstadoCircular:
    """Movimiento circular con aceleración angular constante, incluso frenado/inversión."""
    if radio_m <= 0:
        raise ValueError("El radio debe ser positivo.")
    if tiempo_s < 0:
        raise ValueError("El tiempo no puede ser negativo.")
    omega_0 = rpm_a_rad_s(rpm_inicial)
    omega = omega_0 + alpha_rad_s2 * tiempo_s
    theta = omega_0 * tiempo_s + 0.5 * alpha_rad_s2 * tiempo_s**2
    a_t = alpha_rad_s2 * radio_m
    a_c = omega**2 * radio_m
    return EstadoCircular(
        tiempo_s=tiempo_s,
        angulo_rad=theta,
        velocidad_angular_rad_s=omega,
        velocidad_angular_rpm=rad_s_a_rpm(omega),
        velocidad_tangencial_m_s=omega * radio_m,  # Componente tangencial con signo.
        rapidez_tangencial_m_s=abs(omega) * radio_m,
        aceleracion_tangencial_m_s2=a_t,
        aceleracion_centripeta_m_s2=a_c,
        aceleracion_total_m_s2=hypot(a_t, a_c),
        vueltas_netas=theta / (2.0 * pi),
    )


def periodo_s_desde_rpm(rpm: float) -> float | None:
    """Período de una revolución para rapidez angular constante no nula."""
    return 60.0 / abs(rpm) if rpm != 0 else None


def latencia_rotacional_media_ms(rpm: float) -> float:
    """Aproximación teórica: mitad de una vuelta por solicitud, sin latencia de búsqueda."""
    if rpm <= 0:
        raise ValueError("Para un HDD, las RPM deben ser positivas.")
    return 30_000.0 / rpm


def latencia_rotacional_max_ms(rpm: float) -> float:
    """Espera rotacional máxima aproximada para una revolución completa."""
    if rpm <= 0:
        raise ValueError("Para un HDD, las RPM deben ser positivas.")
    return 60_000.0 / rpm


def rpm_minimas_para_objetivo(latencia_objetivo_ms: float) -> float:
    if latencia_objetivo_ms <= 0:
        raise ValueError("La latencia objetivo debe ser mayor que cero.")
    return 30_000.0 / latencia_objetivo_ms
