# Seguridad percibida y movilidad ciclista: evidencia de datos panel para ECOBICI en la Ciudad de México

**Carla Andrea Sosa Peralta** · Caso de titulación, Ciencia de Datos, ITAM

**[Ver el tablero interactivo](https://carlaandr.github.io/seguridadEcobici/)** · [Documento (PDF)](documento/seguridad_ecobici.pdf)

Este repositorio contiene las fuentes de información, los notebooks de procesamiento, los datos derivados, el modelo econométrico y el tablero del caso. Todo el análisis se puede replicar con Docker (sección 6).

> **En una frase:** con un panel de seis alcaldías entre 2020 y 2026, no encontramos evidencia de una asociación entre la percepción de inseguridad (ENSU) y los viajes de ECOBICI. Esto no demuestra que la asociación sea cero: el diseño solo permite descartar asociaciones grandes.

## Contenido

1. [Pregunta e hipótesis](#1-pregunta-e-hipótesis)
2. [Resultado principal](#2-resultado-principal)
3. [Datos](#3-datos)
4. [Estructura del repositorio](#4-estructura-del-repositorio)
5. [Notebooks y flujo de procesamiento](#5-notebooks-y-flujo-de-procesamiento)
6. [Cómo replicar el análisis](#6-cómo-replicar-el-análisis)
7. [Modelo econométrico](#7-modelo-econométrico)
8. [Diccionario de artefactos](#8-diccionario-de-artefactos)
9. [Limitaciones y trabajo pendiente](#9-limitaciones-y-trabajo-pendiente)
10. [Uso de inteligencia artificial](#10-uso-de-inteligencia-artificial)
11. [Fuentes](#11-fuentes)

## 1. Pregunta e hipótesis

**¿Se asocia la percepción de inseguridad de la población con el uso de ECOBICI en las alcaldías de la Ciudad de México?**

- **Hipótesis de investigación:** una mayor percepción de inseguridad se asocia con menos viajes, porque el temor a ser víctima de un delito puede llevar a evitar la calle.
- **Prueba estadística:** H₀: β₁ = 0 contra H₁: β₁ ≠ 0, a dos colas, con nivel de significancia de 5 %. Se usa una prueba bilateral porque un signo positivo también sería un hallazgo.

El estudio mide una **asociación**, no un efecto causal. Los efectos fijos controlan diferencias permanentes entre alcaldías y choques comunes a todos los trimestres, pero no factores que cambian por alcaldía y por trimestre al mismo tiempo.

## 2. Resultado principal

El modelo principal usa el **total de viajes del ejercicio 1** (sin inversión pública). Los modelos por sexo y el ejercicio 2 se reportan como extensiones.

| Modelo | β₁ | EE agrupado | IC 95 %, t(5) | p | Obs. |
|---|---|---|---|---|---|
| **Total, ejercicio 1** | **0.0064** | **0.0079** | **[−0.014, 0.027]** | **0.45** | **105** |

- **Lectura:** no se rechaza H₀. Un punto porcentual más de población que se siente insegura se asocia con unos 0.64 % más viajes, pero el coeficiente no se distingue de cero.
- **Qué descarta:** para un aumento de 10 puntos de población insegura, el intervalo es compatible con cambios de **−13 % a +31 %** en los viajes. El modelo no tiene potencia para detectar asociaciones pequeñas.
- **Robustez:** ningún intervalo excluye el cero en los modelos por sexo, en el ejercicio 2 ni en las variantes de especificación (sin estaciones, logaritmo de estaciones, quitando una alcaldía a la vez, solo alcaldías con panel completo). El signo cambia entre variantes, por lo que no se interpreta.
- **Inferencia con pocos grupos:** el wild cluster bootstrap con pesos de Webb lleva a la misma conclusión.

Las tablas completas, la robustez y la discusión de por qué no se detecta la asociación están en el documento y en el [tablero](https://carlaandr.github.io/seguridadEcobici/).

## 3. Datos

| Fuente | Qué se usa | Frecuencia | Papel en el modelo |
|---|---|---|---|
| **ECOBICI** (datos abiertos) | Viajes por estación de retiro y sexo; catálogo de estaciones (feed GBFS) | Mensual, agregada a trimestre | Variable dependiente: viajes. Control: estaciones activas |
| **ENSU**, INEGI | Cuadro 1.7 de los tabulados básicos: población de 18 años y más que se siente segura o insegura, por alcaldía | Trimestral | Variable explicativa: % de población insegura |
| **EFIPEM**, INEGI | Inversión pública por alcaldía | Anual | Control en el ejercicio 2 |

**Alcaldías:** Álvaro Obregón, Azcapotzalco, Benito Juárez, Coyoacán, Cuauhtémoc y Miguel Hidalgo, que son las que tienen estaciones de ECOBICI. La ENSU y EFIPEM cubren las 16 alcaldías; el panel conserva solo estas seis.

**Panel:** alcaldía × trimestre, 2020-T1 a 2026-T1, **no balanceado**.

- Benito Juárez, Cuauhtémoc y Miguel Hidalgo están desde 2020. Álvaro Obregón, Azcapotzalco y Coyoacán entran al panel en 2023.
- Falta 2020-T2: la ENSU no se levantó en ese trimestre por la pandemia.
- Ejercicio 1: 105 observaciones alcaldía-trimestre. Ejercicio 2: 99, porque la inversión pública llega hasta 2025.
- Los viajes de estaciones que no aparecen en el catálogo actual (`SIN_CATALOGO`) no se asignan a ninguna alcaldía y quedan fuera del panel.
- ECOBICI registra el sexo como `F`, `M`, `O` y `?`. Los modelos usan el total y, como extensión, `F` y `M`. La ENSU no publica la percepción por sexo a nivel alcaldía.

## 4. Estructura del repositorio

```text
seguridadEcobici/
├── README.md
├── index.html                  Tablero (GitHub Pages)
├── documento/
│   └── seguridad_ecobici.pdf   Documento del caso (formato IEEE)
├── Dockerfile                  Imagen para replicar todo
├── compose.yaml                Comandos de ejecución
├── requirements.txt            Dependencias con versiones fijas
├── ejecutar.py                 Corre los notebooks en orden y compara resultados
├── rutas.py                    Rutas del proyecto (sustituye a Google Drive)
├── PaneldeDatos.ipynb          Construcción del panel
├── Modelado.ipynb              Análisis exploratorio, modelos y figuras
├── dataIngestion/
│   ├── MapeoAlcaldias.ipynb
│   ├── LecturaEcobici.ipynb
│   ├── LecturaDatosENSU.ipynb
│   ├── LecturadeDatosInversionPublica.ipynb
│   └── MapasdeSeguridad.ipynb
├── graficas/
│   └── GraficasSeguridad.ipynb
├── ensu/                       25 paquetes de tabulados ENSU (.zip), marzo 2020 a junio 2026
├── finanzasPublicas/           6 exportaciones EFIPEM (.xls), 2020 a 2025
└── artefactos/                 Datos derivados (sección 8)
```

Al ejecutar el proyecto se crean `salidas/` (resultados de la corrida) y `datos_crudos/` (descargas de ECOBICI). Ninguna de las dos se sube al repositorio.

## 5. Notebooks y flujo de procesamiento

| Orden | Notebook | Qué hace | Genera |
|---|---|---|---|
| 1 | `dataIngestion/MapeoAlcaldias.ipynb` | Descarga las estaciones del feed GBFS y las asigna a una alcaldía por sus coordenadas | `catalogo_ecobici_estaciones_alcaldia.csv` |
| 2 | `dataIngestion/LecturaEcobici.ipynb` | Lee los CSV mensuales de viajes desde el portal sin guardarlos, homologa columnas entre años y agrega por trimestre, estación, alcaldía y sexo | `ecobici_resumen_viajes_trimestre_alcaldia.csv` |
| 3 | `dataIngestion/LecturaDatosENSU.ipynb` | Extrae el cuadro 1.7 de cada paquete de la ENSU | `percepcion_seguridad_alcaldias_cdmx.csv` |
| 4 | `dataIngestion/LecturadeDatosInversionPublica.ipynb` | Extrae la inversión pública por alcaldía y año | `inversion_publica_alcaldia.csv` |
| 5 | `PaneldeDatos.ipynb` | Une las tres fuentes en el panel alcaldía × trimestre × sexo | `panel_ecobici.csv` |
| 6 | `graficas/GraficasSeguridad.ipynb` | Gráficas descriptivas de la ENSU | Figuras |
| 7 | `Modelado.ipynb` | Análisis exploratorio, modelos de efectos fijos, robustez y exportación para el tablero | Tablas, figuras y `modelado.csv` |
| 8 | `dataIngestion/MapasdeSeguridad.ipynb` | Mapas de percepción de inseguridad por alcaldía | Figuras |

```text
Viajes ECOBICI ──> LecturaEcobici ─────────────┐
Feed GBFS ───────> MapeoAlcaldias ─────────────┤
ENSU (INEGI) ────> LecturaDatosENSU ───────────┼──> PaneldeDatos ──> Modelado ──> index.html (tablero)
EFIPEM (INEGI) ──> LecturadeDatosInversionPublica ┘
```

## 6. Cómo replicar el análisis

No se necesita Colab ni Google Drive. Requisito: [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bash
git clone https://github.com/carlaAndr/seguridadEcobici.git
cd seguridadEcobici
docker compose run --rm analisis
```

| Modo | Qué corre | Internet | Tiempo |
|---|---|---|---|
| `analisis` (por defecto) | ENSU y EFIPEM desde los archivos originales de `ensu/` y `finanzasPublicas/`, panel, gráficas y modelos. Los viajes de ECOBICI se toman de `artefactos/`. | No | Minutos |
| `completo` | Además reconstruye el catálogo de estaciones y vuelve a descargar los viajes de ECOBICI 2020–2026. | Sí | Horas |

```bash
docker compose run --rm completo
```

Al terminar, `ejecutar.py` compara cada archivo regenerado contra la versión de `artefactos/` e indica si es **IGUAL** o **DISTINTO**. Los resultados quedan en `salidas/`:

| Carpeta | Contenido |
|---|---|
| `salidas/datos/` | CSV regenerados y `resultados_panel_ecobici_seguridad.txt` |
| `salidas/figuras_eda_ieee/` | Figuras del análisis exploratorio (PNG 600 dpi, PDF, SVG) |
| `salidas/figuras_resultados/` | Figuras de resultados y tablas de modelos y robustez |
| `salidas/figuras_seguridad/` | Gráficas y mapas de la ENSU |
| `salidas/notebooks/` | Cada notebook ya ejecutado, con sus salidas |

Sin `docker compose`:

```bash
docker build -t seguridad-ecobici .
docker run --rm -v "$(pwd)/salidas:/app/salidas" seguridad-ecobici
```

En Windows (PowerShell), cambia `$(pwd)` por `${PWD}`.

**Sin Docker:** con Python 3.12, `pip install -r requirements.txt` y luego `python ejecutar.py`.

**Tablero en local:** desde la raíz del repositorio, `python -m http.server` y abre `http://localhost:8000`. Abrir `index.html` con doble clic no funciona, porque el navegador no deja leer los CSV.

**Límites de la replicación completa.** El catálogo de estaciones sale del feed GBFS, que refleja las estaciones de hoy; si ECOBICI agrega o mueve estaciones, el catálogo regenerado puede diferir del de `artefactos/`, que es el usado en el documento. El portal de datos abiertos puede tener meses posteriores al corte del estudio; esos trimestres no entran al panel porque no tienen dato de la ENSU.

## 7. Modelo econométrico

**Ejercicio 1 (modelo principal):**

$$
\log(1+\mathrm{Viajes}_{it}) = \beta_1\,\mathrm{Inseguridad}_{it} + \gamma\,\mathrm{Estaciones}_{it} + \alpha_i + \lambda_t + \varepsilon_{it}
$$

**Ejercicio 2:** agrega $\beta_3 \log(\mathrm{Inversión}_{it})$.

| Término | Definición |
|---|---|
| $i$, $t$ | Alcaldía y trimestre |
| $\mathrm{Viajes}_{it}$ | Viajes de ECOBICI que inician en estaciones de la alcaldía (total, mujeres u hombres) |
| $\mathrm{Inseguridad}_{it}$ | % de población de 18 años y más que se siente insegura (ENSU, cuadro 1.7) |
| $\mathrm{Estaciones}_{it}$ | Estaciones con al menos un viaje en el trimestre |
| $\mathrm{Inversión}_{it}$ | Inversión pública anual de la alcaldía (EFIPEM), repetida en los trimestres del año |
| $\alpha_i$, $\lambda_t$ | Efectos fijos de alcaldía y de trimestre |

**Inferencia.** Errores estándar agrupados por alcaldía. Como solo hay seis grupos, los intervalos y p-valores usan una t con 5 grados de libertad (G − 1), y se verifican con un wild cluster bootstrap con pesos de Webb. Se usan efectos fijos y no aleatorios porque las seis alcaldías son toda la población de interés, no una muestra; por eso no se usa la prueba de Hausman, que además no es válida con errores agrupados.

**Precauciones.** Las estaciones activas se calculan con los mismos datos de viajes, así que son un control imperfecto. La inversión es anual y es un rubro agregado: no es inversión en ciclovías ni en ECOBICI, y repetir el monto anual no crea cuatro mediciones independientes.

## 8. Diccionario de artefactos

Los archivos de `artefactos/` son datos derivados. `ejecutar.py` los usa como referencia para comprobar que la corrida reproduce los resultados.

| Archivo | Filas | Contenido |
|---|---|---|
| `catalogo_ecobici_estaciones_alcaldia.csv` | 677 | `station_id`, `name`, `short_name`, `alcaldia`. El cruce con los viajes se hace por `short_name`. |
| `ecobici_estaciones_por_alcaldia_resumen.csv` | 6 | `alcaldia`, `num_estaciones` |
| `ecobici_resumen_viajes_trimestre_alcaldia.csv` | 46,091 | `anio`, `trimestre`, `ciclo_estacion_retiro`, `alcaldia` (o `SIN_CATALOGO`), `genero` (`F`, `M`, `O`, `?`), `n_viajes`, `estaciones_activas_alcaldia` |
| `percepcion_seguridad_alcaldias_cdmx.csv` | 400 | 16 alcaldías × 25 levantamientos. `anio`, `mes`, `trimestre`, `region`, `alcaldia`, `poblacion_18mas`, `seguro_abs`, `seguro_pct`, `inseguro_abs`, `inseguro_pct` |
| `inversion_publica_alcaldia.csv` | 96 | 16 alcaldías × 2020–2025. `año`, `alcaldia`, `inversion_publica` |
| `panel_ecobici.csv` | 345 | Panel alcaldía × trimestre × sexo. `anio`, `trimestre`, `alcaldia_norm`, `genero`, `n_viajes`, `estaciones_activas`, `inseguro_pct`, `seguro_pct`, `inversion_publica`, `log_viajes`, `log_inversion` |
| `modelado.csv` | — | Una fila por coeficiente: modelos principales, diferencia mujeres − hombres y variantes de robustez, con EE, t, p, IC, N y cambio % por 10 puntos. Lo lee el tablero. |
| `tabla_I_modelos.csv`, `tabla_robustez.csv` | — | Tablas del documento, para comparar contra la corrida |

## 9. Limitaciones y trabajo pendiente

- **Junio 2026 de la ENSU (pendiente).** Un cambio en las columnas del tabulado de junio 2026 hace que ese levantamiento se pierda al construir el panel. Al corregirlo, el ejercicio 1 gana seis observaciones y las cifras pueden moverse ligeramente.
- **Escala de la percepción.** La ENSU mide la percepción de quienes viven en la alcaldía, no de quienes usan ECOBICI, y no permite separar el número de personas que viajan de los viajes por persona.
- **Error de medición.** Las estimaciones de la ENSU por alcaldía tienen error muestral; parte de su variación entre trimestres puede ser ruido, lo que sesga el coeficiente hacia cero.
- **Poca variación.** Después de los efectos fijos queda poca variación en la percepción de inseguridad para identificar β₁.
- **Pocos grupos.** Con seis alcaldías, la inferencia con errores agrupados es aproximada aun con la corrección t(5).
- **Panel no balanceado.** La entrada de tres alcaldías en 2023 pesa en la estimación.
- **Catálogo actual.** El catálogo de estaciones refleja el sistema actual; estaciones históricas que ya no existen quedan como `SIN_CATALOGO`.

## 10. Uso de inteligencia artificial

Durante el proyecto se usaron herramientas de inteligencia artificial generativa (ChatGPT y Claude) como apoyo en:

- **Procesamiento de datos:** identificar inconsistencias, homologar estructuras y construir las bases de análisis.
- **Visualización:** construir y mejorar gráficas, mapas y el tablero.
- **Código y reproducibilidad:** revisar notebooks y preparar la ejecución con Docker.
- **Documentación:** redactar descripciones metodológicas, comentarios de código y este README.

La definición del problema, la selección de fuentes, las hipótesis, las decisiones metodológicas y la interpretación de los resultados son responsabilidad de la autora.

## 11. Fuentes

- **ECOBICI.** Datos abiertos del sistema de bicicletas públicas de la Ciudad de México: https://ecobici.cdmx.gob.mx/datos-abiertos/
- **INEGI, ENSU.** Encuesta Nacional de Seguridad Pública Urbana, tabulados básicos.
- **INEGI, EFIPEM.** Estadística de Finanzas Públicas Estatales y Municipales.

---

**Estado:** caso de titulación en revisión final (noviembre 2026).
