FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir textX==4.3.0 networkx==3.4.2 matplotlib==3.9.2
ENV MPLCONFIGDIR=/tmp
ENTRYPOINT ["python", "verification.py"]
