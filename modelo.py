"""Núcleo económico independiente de Streamlit. Duopolio de Cournot lineal.

Unidades: cantidades físicas y unidades monetarias genéricas.
Se trabaja con a >= 0, b > 0, c1 >= 0, c2 >= 0.
"""
from dataclasses import dataclass
from math import isclose


@dataclass(frozen=True)
class Mercado:
    a: float = 100.0
    b: float = 1.0
    c1: float = 20.0
    c2: float = 20.0

    def __post_init__(self):
        if not (self.a >= 0 and self.b > 0 and self.c1 >= 0 and self.c2 >= 0):
            raise ValueError("Se requiere a >= 0, b > 0 y costos no negativos.")


@dataclass(frozen=True)
class Resultado:
    q1: float
    q2: float
    q_total: float
    precio: float
    ingreso1: float
    ingreso2: float
    costo1: float
    costo2: float
    beneficio1: float
    beneficio2: float
    tipo: str


def reaccion1(m: Mercado, q2: float) -> float:
    """Mejor respuesta no negativa de la empresa 1."""
    if q2 < 0:
        raise ValueError("La cantidad del rival no puede ser negativa.")
    return max(0.0, (m.a - m.c1 - m.b * q2) / (2 * m.b))


def reaccion2(m: Mercado, q1: float) -> float:
    """Mejor respuesta no negativa de la empresa 2."""
    if q1 < 0:
        raise ValueError("La cantidad del rival no puede ser negativa.")
    return max(0.0, (m.a - m.c2 - m.b * q1) / (2 * m.b))


def evaluar(m: Mercado, q1: float, q2: float, tipo: str = "Escenario") -> Resultado:
    """Evalúa precio, ingresos, costos y beneficios de cantidades dadas.

    Se permite precio inverso negativo en el modelo matemático, aunque la interfaz
    restringe cantidades manuales a Q <= a/b para operar con P >= 0.
    """
    if q1 < -1e-9 or q2 < -1e-9:
        raise ValueError("No se permite producción negativa.")
    q1, q2 = max(0.0, q1), max(0.0, q2)
    total = q1 + q2
    precio = m.a - m.b * total
    ingreso1, ingreso2 = precio * q1, precio * q2
    costo1, costo2 = m.c1 * q1, m.c2 * q2
    return Resultado(q1, q2, total, precio, ingreso1, ingreso2, costo1,
                     costo2, ingreso1 - costo1, ingreso2 - costo2, tipo)


def equilibrio(m: Mercado) -> Resultado:
    """Equilibrio único de Nash-Cournot, incluyendo esquinas y (0,0).

    Condiciones KKT para q_i >= 0:
    q_i >= 0, g_i=a-c_i-2b*q_i-b*q_j <= 0 si q_i=0;
    si q_i>0 entonces g_i=0. Equivalente a q_i=BR_i(q_j).
    """
    tolerancia = 1e-10
    # Ambas empresas fuera del mercado.
    if m.c1 >= m.a and m.c2 >= m.a:
        resultado = evaluar(m, 0, 0, "Esquina: ambas empresas inactivas")
    else:
        q1_int = (m.a - 2 * m.c1 + m.c2) / (3 * m.b)
        q2_int = (m.a - 2 * m.c2 + m.c1) / (3 * m.b)
        if q1_int > tolerancia and q2_int > tolerancia:
            resultado = evaluar(m, q1_int, q2_int, "Equilibrio interior")
        else:
            q1_mon = reaccion1(m, 0)
            q2_mon = reaccion2(m, 0)
            if q1_mon > tolerancia and reaccion2(m, q1_mon) <= tolerancia:
                resultado = evaluar(m, q1_mon, 0, "Esquina: solo produce empresa 1")
            elif q2_mon > tolerancia and reaccion1(m, q2_mon) <= tolerancia:
                resultado = evaluar(m, 0, q2_mon, "Esquina: solo produce empresa 2")
            else:
                # Fallback de punto fijo; BR tiene pendiente absoluta 1/2.
                q1, q2 = 0.0, 0.0
                for _ in range(300):
                    nuevo1, nuevo2 = reaccion1(m, q2), reaccion2(m, q1)
                    if max(abs(nuevo1-q1), abs(nuevo2-q2)) < 1e-12:
                        q1, q2 = nuevo1, nuevo2
                        break
                    q1, q2 = nuevo1, nuevo2
                tipo = ("Equilibrio interior" if q1 > tolerancia and q2 > tolerancia
                        else "Esquina: solo produce empresa 1" if q1 > tolerancia
                        else "Esquina: solo produce empresa 2" if q2 > tolerancia
                        else "Esquina: ambas empresas inactivas")
                resultado = evaluar(m, q1, q2, tipo)
    if not (isclose(resultado.q1, reaccion1(m, resultado.q2), abs_tol=1e-7, rel_tol=1e-9)
            and isclose(resultado.q2, reaccion2(m, resultado.q1), abs_tol=1e-7, rel_tol=1e-9)):
        raise ArithmeticError("El resultado no satisface ambas mejores respuestas.")
    return resultado


def etiqueta_reaccion(m: Mercado, empresa: int) -> str:
    if empresa == 1:
        return f"q₁ = máx(0, ({m.a:g} − {m.c1:g} − {m.b:g}·q₂) / {2*m.b:g})"
    if empresa == 2:
        return f"q₂ = máx(0, ({m.a:g} − {m.c2:g} − {m.b:g}·q₁) / {2*m.b:g})"
    raise ValueError("Empresa debe ser 1 o 2")


def parametros(m: Mercado) -> dict:
    return {"a": m.a, "b": m.b, "c1": m.c1, "c2": m.c2}
