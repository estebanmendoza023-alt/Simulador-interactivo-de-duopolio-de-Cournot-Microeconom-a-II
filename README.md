# LOS OPTIMOS — Simulador de Duopolio de Cournot

**Universidad de La Sabana · Microeconomía II · Taller 5 — Reto 4**

Aplicación web **local**, gratuita y didáctica para comprender la competencia en cantidades. Permite cambiar la demanda y los costos, visualizar las curvas de mejor respuesta, tomar decisiones individuales, comparar escenarios y analizar precios, ingresos, costos y beneficios. **No requiere cuenta ni API.**

## Archivos

| Archivo | Para qué sirve |
|---|---|
| `app.py` | Interfaz Streamlit: portada, controles, pestañas, decisiones y guardados |
| `modelo.py` | Modelo económico, mejores respuestas y equilibrio interior/esquinas |
| `graficas.py` | Gráficas Plotly (curvas, beneficios y comparaciones) |
| `explicaciones.py` | Textos económicos ajustados a cálculos reales |
| `manual_economico.pdf` | Explicación, derivación y uso del modelo |
| `guion_video.md` | Guion demostrativo de máximo 5 minutos |
| `tests/` | Pruebas matemáticas y de visualización |
| `.streamlit/config.toml` | Paleta visual de la aplicación |
| `requirements.txt` | Dependencias gratuitas |
| `ejecutar_windows.bat`, `ejecutar_mac_linux.sh` | Arranque asistido |
| `verificar_entorno.py` | Detecta Python, VS Code (si está en PATH) y dependencias en tu equipo |
| `REPORTE_PRUEBAS.md` | Pruebas completadas y verificación de interfaz pendiente |

## Revisión del computador

Antes de instalar, en una terminal de esta carpeta ejecuta `python verificar_entorno.py` (o `python3` en Mac/Linux). El diagnóstico describe el computador en que lo ejecutes.

## Requisitos

- Python **3.11, 3.12 o 3.13**. Puedes obtenerlo gratuitamente en https://www.python.org/downloads/ (en Windows, marca «Add Python to PATH»).
- Visual Studio Code **opcional**, en https://code.visualstudio.com/ . La aplicación funciona sin VS Code.
- Acceso a internet **solo en la primera instalación** de bibliotecas. La app funciona localmente después (la tipografía externa puede sustituirse por fuente local si no hay internet).

## Cómo ejecutar — Windows

1. Descomprime la carpeta y ábrela.
2. Haz doble clic en `ejecutar_windows.bat` (si Windows impide scripts, abre la terminal en esa carpeta y sigue el método manual).
3. Espera a que se abra la página local en tu navegador, normalmente **http://localhost:8501**.
4. Para detenerla, cierra la terminal o presiona **Ctrl + C**.

## Cómo ejecutar — Mac o Linux

Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
bash ejecutar_mac_linux.sh
```

También puedes ejecutar todos los pasos de forma manual:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

En Mac/Linux usa `python3` si el comando `python` no existe. Si el puerto 8501 está ocupado, Streamlit puede utilizar otro y lo mostrará en terminal.

## Abrir en VS Code

En **Archivo > Abrir carpeta** elige `LOS_OPTIMOS`. Abre la terminal integrada y ejecuta los mismos comandos. Instala la extensión gratuita de Python si deseas sugerencias de código.

## Valores de validación obligatoria

`a=100`, `b=1`, `c1=c2=20`:

| Resultado | Valor |
|---|---:|
| q1* | 26.67 |
| q2* | 26.67 |
| Q* | 53.33 |
| P* | 46.67 |
| Beneficio de cada empresa | 711.11 |

## Cómo usarlo

1. En la portada, pulsa **Comenzar simulación**.
2. En la barra lateral, modifica `a`, `b`, `c1`, `c2` con el control deslizante **o** la entrada numérica. Usa Restablecer si lo deseas.
3. En **Reacciones y equilibrio**, compara las curvas `R1` y `R2`. Las sólidas son actuales y las discontinuas indican la referencia. Eje X = `q1`; eje Y = `q2`.
4. En **Decisión individual**, selecciona una empresa, fija la cantidad rival o usa la del equilibrio y mueve tu cantidad. Compara beneficio actual vs. mejor respuesta.
5. En **Resultados** mira la tabla que separa el equilibrio de la última decisión manual.
6. En **Escenarios** guarda, compara y exporta tus escenarios en JSON; puedes importarlos más adelante. Los escenarios se mantienen en la sesión abierta y **deben exportarse para conservarlos tras cerrar la pestaña**.
7. Selecciona uno guardado como **Escenario de referencia** en la barra lateral para visualizar los desplazamientos.

## Interpretación económica importante

El resultado interior **solo** se usa cuando ambas cantidades son estrictamente positivas. En las esquinas, el algoritmo resuelve `q1 = max(0, (a-c1-b*q2)/(2b))` y `q2 = max(0,(a-c2-b*q1)/(2b))`. Se valida que el equilibrio sea una mejor respuesta mutua.

La decisión individual mantiene fija la cantidad rival. Por coherencia didáctica, la interfaz limita la producción manual para mantener `Q ≤ a/b` (precio inverso no negativo). Las bibliotecas y la app trabajan con unidades monetarias genéricas; no se presupone un país o moneda particular.

## Estado real de las pruebas

El modelo económico y las gráficas superaron las pruebas automatizadas, pero **no se ha validado aquí el lanzamiento visual de Streamlit**, debido a que el entorno utilizado para preparar los archivos no pudo descargar la dependencia. Consulta `REPORTE_PRUEBAS.md` para ver qué se probó y qué debes verificar al abrirlo en tu computador.

## Pruebas

```bash
python -m pip install pytest
python -m pytest -q
```

Verifican el caso inicial, cambios en parámetros, esquinas, KKT/mejores respuestas, decisiones manuales, rangos no negativos y trazos de las funciones sobre los ejes correctos.

## Solución de problemas

- `python` no aparece: instala Python y reinicia la terminal.
- `No module named streamlit`: `python -m pip install -r requirements.txt` dentro del entorno virtual.
- No aparece el navegador: abre la URL local indicada en la terminal.
- El puerto está ocupado: `python -m streamlit run app.py --server.port 8502`.
- La vista está vacía: comprueba la terminal por si hay un error y reinicia la aplicación.
- Si estás en una red muy restrictiva, la instalación de dependencias puede requerir acceso a PyPI.

El proyecto no altera archivos externos, no envía datos a servidores y no requiere servicios de pago.
