FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN pip install --no-cache-dir numpy==1.24.3 scipy==1.11.1

COPY . .

# For GeoDjango dependencies (GDAL, GEOS, PROJ)
RUN apt-get update && \
    apt-get install -y binutils libproj-dev gdal-bin && \
    rm -rf /var/lib/apt/lists/*

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 