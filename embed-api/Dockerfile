FROM python:3.13.7-slim

WORKDIR /app

# Install dependencies and .NET runtime
RUN apt-get update && apt-get install -y ca-certificates wget gnupg \
    && wget -qO- https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/trusted.gpg.d/microsoft.asc \
    && echo "deb [arch=amd64 signed-by=/etc/apt/trusted.gpg.d/microsoft.asc] https://packages.microsoft.com/debian/13/prod stable main" | tee /etc/apt/sources.list.d/microsoft-prod.list \
    && apt-get update \
    && apt-get install -y dotnet-runtime-8.0 \
    && rm -rf /var/lib/apt/lists/*

# Install other dependencies
RUN apt-get install -y --no-install-recommends \
    build-essential \
    unzip

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x ./osu_skills_rs_0.1.0_linux-x64
RUN chmod +x ./Mapperator.ConsoleAppLinux

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
