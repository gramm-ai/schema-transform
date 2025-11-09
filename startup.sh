#!/bin/bash

# Azure App Service Startup Script for Multi-Tenant Schema Translator

# Install ODBC drivers if not present (Azure App Service has them pre-installed)
if ! [[ "18.0.1.1" = "$(odbcinst -q -d -n 'ODBC Driver 18 for SQL Server' | grep Version | awk '{print $3}')" ]]; then
    echo "Installing ODBC Driver 18 for SQL Server..."
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
    curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
    apt-get update
    ACCEPT_EULA=Y apt-get install -y msodbcsql18
fi

# Start the FastAPI application
echo "Starting Multi-Tenant Schema Translator API..."
cd /home/site/wwwroot
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
