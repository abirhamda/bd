FROM bitnami/spark:3.3.2

USER root

# Installer Python 3, pip et les packages nécessaires
RUN apt-get update && apt-get install -y python3-pip && \
    pip3 install --no-cache-dir pyspark pandas scikit-learn

USER 1001

WORKDIR /app
COPY app /app
