"""
Rutas del proyecto seguridadEcobici.

Sustituye a las rutas de Google Drive (/content/drive/MyDrive/...). Todas
las rutas son relativas a la raíz del repositorio, así que el mismo código
corre en Docker, en tu computadora o en Colab (con el repo clonado).

Carpetas:
    ensu/              Tabulados ENSU originales (.zip de INEGI). Entrada.
    finanzasPublicas/  Exportaciones EFIPEM de INEGI (.xls). Entrada.
    artefactos/        Archivos derivados que están en el repositorio. Se usan
                       como entrada cuando no se regeneran en la corrida
                       (por ejemplo, los viajes de ECOBICI en modo "analisis").
    salidas/           Todo lo que genera la corrida: CSV, tablas, figuras y
                       notebooks ejecutados. No se sube a git.
    datos_crudos/      Parquet mensuales de ECOBICI y temporales. Pesa varios
                       GB, no se sube a git.
"""
from pathlib import Path

__all__ = [
    "RAIZ", "ENSU_ZIPS", "FINANZAS", "ARTEFACTOS", "SALIDAS", "DATOS",
    "FIG_EDA", "FIG_RES", "FIG_SEG", "LOGS", "DATOS_CRUDOS", "ECOBICI_MESES",
    "TMP", "entrada", "salida",
]

RAIZ = Path(__file__).resolve().parent

# Entradas originales
ENSU_ZIPS = RAIZ / "ensu"
FINANZAS = RAIZ / "finanzasPublicas"
ARTEFACTOS = RAIZ / "artefactos"

# Salidas de la corrida
SALIDAS = RAIZ / "salidas"
DATOS = SALIDAS / "datos"
FIG_EDA = SALIDAS / "figuras_eda_ieee"
FIG_RES = SALIDAS / "figuras_resultados"
FIG_SEG = SALIDAS / "figuras_seguridad"
LOGS = SALIDAS / "logs"

# Datos pesados que no van a git
DATOS_CRUDOS = RAIZ / "datos_crudos"
ECOBICI_MESES = DATOS_CRUDOS / "ecobici_meses"
TMP = DATOS_CRUDOS / "tmp"

for _carpeta in (DATOS, FIG_EDA, FIG_RES, FIG_SEG, LOGS, ECOBICI_MESES, TMP):
    _carpeta.mkdir(parents=True, exist_ok=True)


def entrada(nombre: str) -> str:
    """Ruta de un archivo derivado que se va a LEER.

    Usa la versión que generó esta corrida (salidas/datos/) si existe. Si no,
    usa la del repositorio (artefactos/). Imprime cuál eligió para que quede
    en el notebook ejecutado.
    """
    for carpeta in (DATOS, ARTEFACTOS):
        ruta = carpeta / nombre
        if ruta.exists() and ruta.stat().st_size > 0:
            print(f"[rutas] {nombre} <- {ruta.relative_to(RAIZ)}")
            return str(ruta)
    raise FileNotFoundError(
        f"No encontré {nombre} ni en {DATOS.relative_to(RAIZ)} ni en "
        f"{ARTEFACTOS.relative_to(RAIZ)}. Corre antes el notebook que lo genera "
        f"o súbelo a artefactos/."
    )


def salida(nombre: str) -> str:
    """Ruta de un archivo derivado que se va a ESCRIBIR (en salidas/datos/)."""
    return str(DATOS / nombre)
