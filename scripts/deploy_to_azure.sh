#!/bin/bash

# KB FG Monitor - Azure Deployment Script
# This script automates the deployment of the KB FG Monitor application to Azure App Service
# Created: May 18, 2025

# Color codes for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - Update these values as needed
RESOURCE_GROUP="kb-fg-monitor-rg"
APP_NAME="kb-fg-monitor-app"
LOCATION="westeurope"
APP_SERVICE_PLAN="kb-fg-monitor-plan"
SKU="F1"
PYTHON_VERSION="3.9"

# Print header
echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}      KB FG Monitor - Azure Deployment Tool      ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Function to check if Azure CLI is installed
check_az_cli() {
    echo -e "${YELLOW}Checking if Azure CLI is installed...${NC}"
    if ! command -v az &> /dev/null; then
        echo -e "${RED}Azure CLI is not installed. Please install it first:${NC}"
        echo "Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    fi
    echo -e "${GREEN}Azure CLI is installed.${NC}"
}

# Function to check if user is logged in to Azure
check_azure_login() {
    echo -e "${YELLOW}Checking Azure login status...${NC}"
    az account show &> /dev/null
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}You are not logged in to Azure. Initiating login...${NC}"
        az login
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to log in to Azure. Exiting.${NC}"
            exit 1
        fi
    fi
    echo -e "${GREEN}Successfully logged in to Azure.${NC}"
}

# Function to check if the resource group exists
check_resource_group() {
    echo -e "${YELLOW}Checking if resource group exists...${NC}"
    az group show --name $RESOURCE_GROUP &> /dev/null
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}Resource group '$RESOURCE_GROUP' does not exist. Creating it...${NC}"
        az group create --name $RESOURCE_GROUP --location $LOCATION
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to create resource group. Exiting.${NC}"
            exit 1
        fi
        echo -e "${GREEN}Resource group created successfully.${NC}"
    else
        echo -e "${GREEN}Resource group '$RESOURCE_GROUP' exists.${NC}"
    fi
}

# Function to check if the App Service Plan exists
check_app_service_plan() {
    echo -e "${YELLOW}Checking if App Service Plan exists...${NC}"
    az appservice plan show --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP &> /dev/null
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}App Service Plan '$APP_SERVICE_PLAN' does not exist. Creating it...${NC}"
        az appservice plan create --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP --sku $SKU --is-linux
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to create App Service Plan. Exiting.${NC}"
            exit 1
        fi
        echo -e "${GREEN}App Service Plan created successfully.${NC}"
    else
        echo -e "${GREEN}App Service Plan '$APP_SERVICE_PLAN' exists.${NC}"
    fi
}

# Function to check if the Web App exists
check_web_app() {
    echo -e "${YELLOW}Checking if Web App exists...${NC}"
    az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}Web App '$APP_NAME' does not exist. Creating it...${NC}"
        az webapp create --name $APP_NAME --resource-group $RESOURCE_GROUP --plan $APP_SERVICE_PLAN --runtime "PYTHON|$PYTHON_VERSION"
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to create Web App. Exiting.${NC}"
            exit 1
        fi
        echo -e "${GREEN}Web App created successfully.${NC}"
        
        # Configure the web app
        echo -e "${YELLOW}Configuring Web App...${NC}"
        az webapp config set --name $APP_NAME --resource-group $RESOURCE_GROUP --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 app:app"
        az webapp config appsettings set --name $APP_NAME --resource-group $RESOURCE_GROUP --settings FLASK_APP=app.py FLASK_ENV=production
        echo -e "${GREEN}Web App configured successfully.${NC}"
    else
        echo -e "${GREEN}Web App '$APP_NAME' exists.${NC}"
    fi
}

# Function to prepare the application for deployment
prepare_app() {
    echo -e "${YELLOW}Preparing application for deployment...${NC}"
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        echo -e "${YELLOW}requirements.txt not found. Creating it...${NC}"
        pip freeze > requirements.txt
        # Make sure gunicorn is in requirements.txt
        if ! grep -q "gunicorn" requirements.txt; then
            echo "gunicorn" >> requirements.txt
        fi
    fi
    
    # Create startup.txt if it doesn't exist
    if [ ! -f "startup.txt" ]; then
        echo -e "${YELLOW}startup.txt not found. Creating it...${NC}"
        echo "gunicorn --bind=0.0.0.0 --timeout 600 app:app" > startup.txt
    fi
    
    # Create a deployment zip file
    echo -e "${YELLOW}Creating deployment package...${NC}"
    rm -f app.zip
    zip -r app.zip . -x ".*" -x "__pycache__/*" -x "*.pyc" -x "*.pyo" -x "*.pyd" -x "env/*" -x "venv/*" -x "*.zip"
    
    echo -e "${GREEN}Application prepared for deployment.${NC}"
}

# Function to deploy the application
deploy_app() {
    echo -e "${YELLOW}Deploying application to Azure...${NC}"
    az webapp deployment source config-zip --resource-group $RESOURCE_GROUP --name $APP_NAME --src app.zip
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Deployment failed. Please check the error message above.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Application deployed successfully!${NC}"
}

# Function to verify application status and show logs if needed
verify_deployment() {
    echo -e "${YELLOW}Verifying deployment and application status...${NC}"
    
    # Wait for a moment to let the application initialize
    echo -e "Waiting 10 seconds for application to initialize..."
    sleep 10
    
    # Check if the application is responding
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://$APP_NAME.azurewebsites.net/)
    
    if [ "$HTTP_STATUS" == "200" ]; then
        echo -e "${GREEN}Application is running successfully (HTTP Status: $HTTP_STATUS)${NC}"
    else
        echo -e "${YELLOW}Application may not be fully initialized yet (HTTP Status: $HTTP_STATUS)${NC}"
        echo -e "${YELLOW}Checking application logs...${NC}"
        
        # Show logs briefly to help with initialization
        echo -e "${YELLOW}Showing application logs for 15 seconds...${NC}"
        echo -e "${YELLOW}(This often helps complete the initialization process)${NC}"
        timeout 15 az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP
        
        # Check again after viewing logs
        HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://$APP_NAME.azurewebsites.net/)
        if [ "$HTTP_STATUS" == "200" ]; then
            echo -e "${GREEN}Application is now running successfully (HTTP Status: $HTTP_STATUS)${NC}"
        else
            echo -e "${YELLOW}Application status: HTTP $HTTP_STATUS${NC}"
            echo -e "${YELLOW}The application may need more time to fully initialize.${NC}"
        fi
    fi
}

# Function to show application URL and additional information
show_app_info() {
    echo -e "${BLUE}=================================================${NC}"
    echo -e "${GREEN}Deployment completed successfully!${NC}"
    echo -e "${BLUE}=================================================${NC}"
    echo -e "Your application is now available at:"
    echo -e "${BLUE}https://$APP_NAME.azurewebsites.net${NC}"
    echo ""
    echo -e "To view application logs, run:"
    echo -e "${YELLOW}az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP${NC}"
    echo ""
    echo -e "To restart the application, run:"
    echo -e "${YELLOW}az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP${NC}"
    echo ""
    echo -e "To delete all resources when no longer needed, run:"
    echo -e "${RED}az group delete --name $RESOURCE_GROUP --yes --no-wait${NC}"
    echo -e "${BLUE}=================================================${NC}"
}

# Main execution flow
main() {
    check_az_cli
    check_azure_login
    check_resource_group
    check_app_service_plan
    check_web_app
    prepare_app
    deploy_app
    verify_deployment
    show_app_info
}

# Execute the main function
main
