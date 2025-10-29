FROM python:3.13.7-slim

WORKDIR /app

# Install dependencies and .NET runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    apt-transport-https \
    && wget https://packages.microsoft.com/config/debian/13/packages-microsoft-prod.deb -O packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && apt-get update \
    && apt-get install -y dotnet-runtime-8.0 \
    && rm -rf /var/lib/apt/lists/* packages-microsoft-prod.deb

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
