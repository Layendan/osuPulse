# Stage 1: Prepare .NET runtime environment
FROM mcr.microsoft.com/dotnet/runtime:8.0 AS dotnet-runtime

WORKDIR /app
COPY Mapperator.ConsoleAppLinux ./Mapperator.ConsoleAppLinux
RUN chmod +x Mapperator.ConsoleAppLinux

# Stage 2: Python base
FROM python:3.13.7-slim

WORKDIR /app

# Install python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python source
COPY . .

# Copy .NET executable and runtime environment from first stage
COPY --from=dotnet-runtime /app/Mapperator.ConsoleAppLinux ./Mapperator.ConsoleAppLinux
RUN chmod +x ./osu_skills_rs_0.1.0_linux-x64
RUN chmod +x ./Mapperator.ConsoleAppLinux

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
