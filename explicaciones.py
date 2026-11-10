"""Interpretaciones basadas en resultados calculados, incluidos los casos de esquina."""
from modelo import Mercado, equilibrio, reaccion1, reaccion2


def dinero(x: float) -> str:
    return f"{x:,.2f}"


def descripcion_cambios(actual: Mercado, referencia: Mercado) -> list[str]:
    r0, r1 = equilibrio(referencia), equilibrio(actual)
    mensajes = []
    etiquetas = {"a": "intercepto de demanda (a)", "b": "pendiente de demanda (b)",
                 "c1": "costo marginal de la empresa 1", "c2": "costo marginal de la empresa 2"}
    for campo in ("a", "b", "c1", "c2"):
        anterior = getattr(referencia, campo)
        nuevo = getattr(actual, campo)
        if abs(nuevo-anterior) < 1e-9:
            continue
        sentido = "aumentó" if nuevo > anterior else "disminuyó"
        if campo == "a":
            idea = ("La demanda inversa se desplaza hacia arriba y puede incentivar mayor producción."
                    if nuevo > anterior else "La menor demanda puede reducir la producción rentable.")
        elif campo == "b":
            idea = ("El precio cae más por cada unidad adicional de producción total."
                    if nuevo > anterior else "El precio cae menos por cada unidad adicional.")
        elif campo == "c1":
            idea = ("La empresa 1 tiene un menor incentivo a producir."
                    if nuevo > anterior else "La empresa 1 puede producir rentablemente más.")
        else:
            idea = ("La empresa 2 tiene un menor incentivo a producir."
                    if nuevo > anterior else "La empresa 2 puede producir rentablemente más.")
        mensajes.append(f"El {etiquetas[campo]} {sentido} de {anterior:g} a {nuevo:g}. {idea}")
    if not mensajes:
        return ["Los parámetros son iguales a los de referencia; por eso el equilibrio y las curvas no cambian."]

    for etiqueta, key in (("Empresa 1", "q1"), ("Empresa 2", "q2"),
                          ("Precio", "precio"), ("Producción total", "q_total")):
        delta = getattr(r1, key) - getattr(r0, key)
        if abs(delta) < 1e-7:
            mensajes.append(f"{etiqueta}: sin cambio respecto a la referencia.")
        else:
            mensajes.append(f"{etiqueta}: {'aumentó' if delta > 0 else 'disminuyó'} "
                            f"{abs(delta):.2f} (de {getattr(r0, key):.2f} a {getattr(r1, key):.2f}).")
    if "Esquina" in r1.tipo:
        mensajes.append(f"El escenario actual es un caso de esquina: {r1.tipo.lower()}. "
                        "No se aplican indiscriminadamente las fórmulas del equilibrio interior.")
    elif "Esquina" in r0.tipo:
        mensajes.append("El equilibrio salió de una esquina y ahora las dos empresas producen.")
    return mensajes


def curva_desplazada(actual: Mercado, referencia: Mercado) -> str:
    # BR1 depende de (a-c1)/b; BR2 depende de (a-c2)/b; ambas tienen pendiente -1/2 en parte positiva.
    coef1 = (actual.a-actual.c1)/actual.b
    coef1_ref = (referencia.a-referencia.c1)/referencia.b
    coef2 = (actual.a-actual.c2)/actual.b
    coef2_ref = (referencia.a-referencia.c2)/referencia.b
    shift1 = abs(coef1-coef1_ref)>1e-8
    shift2 = abs(coef2-coef2_ref)>1e-8
    # Si ambos interceptos <=0, todas sus BR son idénticamente cero: no desplazamiento observable.
    if max(coef1, coef1_ref) <= 0: shift1 = False
    if max(coef2, coef2_ref) <= 0: shift2 = False
    names = []
    if shift1: names.append("R₁ (azul)")
    if shift2: names.append("R₂ (verde)")
    if not names: return "Ninguna curva de mejor respuesta se desplazó de forma observable."
    return "Se desplazó " + (" y ".join(names)) + ". Las líneas discontinuas muestran la referencia."


def diagnostico_decision(elegido: float, mejor: float, equilibrio_individual: float) -> str:
    if abs(elegido-mejor) <= 1e-5:
        mensaje = "Tu cantidad coincide con tu mejor respuesta ante la producción rival elegida."
    elif elegido > mejor:
        mensaje = "Estás produciendo más que tu mejor respuesta: el ingreso marginal queda por debajo del costo marginal en el margen relevante."
    else:
        mensaje = "Estás produciendo menos que tu mejor respuesta: te convendría expandir la cantidad, manteniendo fija la producción rival."
    if abs(elegido-equilibrio_individual)>1e-5:
        mensaje += " La diferencia frente a Cournot no implica por sí sola un error, porque el rival puede producir una cantidad distinta a la del equilibrio."
    return mensaje
