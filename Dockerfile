# Imagen para replicar la investigación seguridadEcobici sin Colab ni Drive.
#
#   docker build -t seguridad-ecobici .
#   docker run --rm -v "$(pwd)/salidas:/app/salidas" seguridad-ecobici
#
# Ver README, sección "Cómo ejecutar", para el modo completo.
FROM python:3.12.7-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Las gráficas se guardan a archivo, sin ventana
    MPLBACKEND=Agg \
    # Carpeta escribible para Jupyter y matplotlib aunque se corra con --user
    HOME=/tmp \
    TZ=America/Mexico_City

WORKDIR /app

# Primero las dependencias: Docker reutiliza esta capa si solo cambian los notebooks
COPY requirements.txt .
RUN pip install -r requirements.txt \
 && python -m ipykernel install --sys-prefix --name python3

# Código, notebooks y datos de entrada (ensu/, finanzasPublicas/, artefactos/)
COPY . .
RUN mkdir -p salidas datos_crudos && chmod -R a+rwX /app

ENTRYPOINT ["python", "ejecutar.py"]
CMD ["analisis"]
