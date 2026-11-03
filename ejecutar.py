"""
Ejecuta todos los notebooks de la investigación, en orden y sin abrir Jupyter.

Uso:
    python ejecutar.py              # = analisis
    python ejecutar.py analisis     # ENSU + inversión + panel + gráficas + modelos (sin internet)
    python ejecutar.py completo     # además vuelve a descargar ECOBICI (internet, horas)
    python ejecutar.py lista        # solo muestra qué corre cada modo

Qué hace:
  1. Revisa que las entradas existan y no estén vacías.
  2. Borra lo que haya en salidas/ (para que nada venga de una corrida vieja).
  3. Corre cada notebook y guarda la versión ejecutada en salidas/notebooks/.
     Si un notebook falla, se detiene y dice cuál y en qué celda.
  4. Compara los archivos regenerados contra los de artefactos/.
"""
import os
import shutil
import sys
import time
import zipfile
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))
import rutas  # noqa: E402

# ---------------------------------------------------------------------------
# Orden de ejecución. Si renombras o agregas un notebook, cámbialo aquí.
# ---------------------------------------------------------------------------
ECOBICI = [
    ("dataIngestion/MapeoAlcaldias.ipynb", "Catálogo estación -> alcaldía (GBFS)"),
    ("dataIngestion/LecturaEcobici.ipynb", "Viajes ECOBICI 2020-2026 por trimestre y alcaldía"),
]
ANALISIS = [
    ("dataIngestion/LecturaDatosENSU.ipynb", "Percepción de inseguridad (ENSU, hoja 1.7)"),
    ("dataIngestion/LecturadeDatosInversionPublica.ipynb", "Inversión pública por alcaldía (EFIPEM)"),
    ("PaneldeDatos.ipynb", "Panel alcaldía x trimestre x género"),
    ("graficas/GraficasSeguridad.ipynb", "Gráficas descriptivas de la ENSU"),
    ("Modelado.ipynb", "EDA, modelos de efectos fijos, bootstrap, Tabla I, figuras y modelado.csv"),
]
MAPAS = [
    ("dataIngestion/MapasdeSeguridad.ipynb", "Mapas de inseguridad (descarga polígonos)"),
]
MODOS = {
    "analisis": ANALISIS,
    "completo": ECOBICI + ANALISIS + MAPAS,
}
# Límite por celda, en segundos. La descarga de ECOBICI tarda horas: sin límite.
TIEMPO_CELDA = {"analisis": 1800, "completo": None}

# Archivos regenerados que se comparan contra la versión del repositorio.
#   nombre en artefactos/  ->  dónde lo deja la corrida
COMPARAR = {
    "percepcion_seguridad_alcaldias_cdmx.csv": rutas.DATOS,
    "inversion_publica_alcaldia.csv": rutas.DATOS,
    "panel_ecobici.csv": rutas.DATOS,
    "modelado.csv": rutas.DATOS,
    "catalogo_ecobici_estaciones_alcaldia.csv": rutas.DATOS,
    "ecobici_resumen_viajes_trimestre_alcaldia.csv": rutas.DATOS,
    "tabla_I_modelos.csv": rutas.FIG_RES,
    "tabla_robustez.csv": rutas.FIG_RES,
}


def revisar_entradas(modo):
    """Falla antes de empezar si falta algo o hay archivos vacíos."""
    problemas = []

    for ruta, _ in MODOS[modo]:
        nb = RAIZ / ruta
        if not nb.exists() or nb.stat().st_size == 0:
            problemas.append(f"Notebook vacío o inexistente: {ruta}")

    zips = sorted(rutas.ENSU_ZIPS.rglob("*.zip"))
    if not zips:
        problemas.append("No hay archivos .zip de la ENSU en ensu/")
    for z in zips:
        if not zipfile.is_zipfile(z):
            problemas.append(f"ZIP vacío o dañado: {z.relative_to(RAIZ)}")

    if not list(rutas.FINANZAS.rglob("*.xls*")):
        problemas.append("No hay archivos de EFIPEM en finanzasPublicas/")

    if modo == "analisis":
        # Sin descarga, los viajes de ECOBICI salen de artefactos/
        f = rutas.ARTEFACTOS / "ecobici_resumen_viajes_trimestre_alcaldia.csv"
        if not f.exists() or f.stat().st_size == 0:
            problemas.append(f"Falta o está vacío: {f.relative_to(RAIZ)}")

    if problemas:
        print("No se puede empezar:")
        for p in problemas:
            print("  -", p)
        sys.exit(1)
    print(f"Entradas revisadas: {len(zips)} ZIP de la ENSU, archivos EFIPEM y notebooks OK.\n")


def limpiar_salidas():
    """Vacía salidas/ sin borrar la carpeta (puede ser un volumen montado)."""
    rutas.SALIDAS.mkdir(exist_ok=True)
    for hijo in rutas.SALIDAS.iterdir():
        shutil.rmtree(hijo) if hijo.is_dir() else hijo.unlink()
    # rutas crea estas carpetas al importarse; se vuelven a crear después de limpiar
    for c in (rutas.DATOS, rutas.FIG_EDA, rutas.FIG_RES, rutas.FIG_SEG, rutas.LOGS):
        c.mkdir(parents=True, exist_ok=True)


def correr_notebook(ruta_rel, descripcion, tiempo_celda):
    origen = RAIZ / ruta_rel
    destino = rutas.SALIDAS / "notebooks" / ruta_rel
    destino.parent.mkdir(parents=True, exist_ok=True)

    print(f"--> {ruta_rel}\n    {descripcion}")
    inicio = time.time()
    nb = nbformat.read(origen, as_version=4)
    cliente = NotebookClient(
        nb,
        timeout=tiempo_celda,
        kernel_name="python3",
        # Cada notebook corre desde su propia carpeta, como en Jupyter
        resources={"metadata": {"path": str(origen.parent)}},
    )
    try:
        cliente.execute()
    except CellExecutionError as error:
        nbformat.write(nb, destino)
        print(f"\n[ERROR] Falló {ruta_rel}. El notebook con el error quedó en "
              f"{destino.relative_to(RAIZ)}\n")
        print(str(error)[-3000:])
        sys.exit(1)
    nbformat.write(nb, destino)
    print(f"    listo en {time.time() - inicio:,.0f} s\n")


def comparar():
    """Compara cada archivo regenerado con el que está en artefactos/."""
    import pandas as pd

    print("=" * 70)
    print("Comparación contra artefactos/ (lo que está en el repositorio)")
    print("=" * 70)
    for nombre, carpeta in COMPARAR.items():
        nuevo = carpeta / nombre
        original = rutas.ARTEFACTOS / nombre
        if not nuevo.exists():
            continue  # no se regeneró en este modo
        if not original.exists():
            print(f"  {nombre:50s} sin versión en artefactos/ para comparar")
            continue
        a, b = pd.read_csv(original), pd.read_csv(nuevo)
        try:
            pd.testing.assert_frame_equal(a, b, check_dtype=False, rtol=1e-6)
            print(f"  {nombre:50s} IGUAL ({len(b)} filas)")
        except AssertionError as e:
            detalle = str(e).strip().splitlines()
            print(f"  {nombre:50s} DISTINTO: {' '.join(detalle[:3])[:160]}")


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else "analisis"
    if modo == "lista":
        for m, pasos in MODOS.items():
            print(f"\n{m}:")
            for i, (r, d) in enumerate(pasos, 1):
                print(f"  {i}. {r:52s} {d}")
        return
    if modo not in MODOS:
        print(f"Modo desconocido: {modo}. Usa: analisis, completo o lista.")
        sys.exit(2)

    print(f"Modo: {modo}\n")
    revisar_entradas(modo)
    limpiar_salidas()
    inicio = time.time()
    for ruta, descripcion in MODOS[modo]:
        correr_notebook(ruta, descripcion, TIEMPO_CELDA[modo])
    comparar()
    print(f"\nTerminado en {(time.time() - inicio) / 60:,.1f} min. "
          f"Resultados en {rutas.SALIDAS.relative_to(RAIZ)}/")


if __name__ == "__main__":
    main()
