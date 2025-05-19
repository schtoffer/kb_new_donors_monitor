#!/bin/bash

# KB FG Monitor - Azure Deployment Script
# This script automates the deployment of the KB FG Monitor application to Azure App Service
# Created: May 19, 2025

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

# Function to remove existing resources if they exist
remove_existing_resources() {
    echo -e "${YELLOW}Checking if resource group exists to remove it...${NC}"
    az group show --name $RESOURCE_GROUP &> /dev/null
    if [ $? -eq 0 ]; then
        echo -e "${YELLOW}Resource group '$RESOURCE_GROUP' exists. Removing it...${NC}"
        echo -e "${YELLOW}This will delete all resources in the group including the web app.${NC}"
        read -p "Are you sure you want to continue? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            az group delete --name $RESOURCE_GROUP --yes
            echo -e "${GREEN}Resource group deletion initiated. Waiting for completion...${NC}"
            # Wait for resource group to be deleted
            while az group show --name $RESOURCE_GROUP &> /dev/null; do
                echo -e "${YELLOW}Waiting for resource group deletion to complete...${NC}"
                sleep 10
            done
            echo -e "${GREEN}Resource group successfully deleted.${NC}"
        else
            echo -e "${YELLOW}Skipping resource group deletion.${NC}"
        fi
    else
        echo -e "${GREEN}Resource group '$RESOURCE_GROUP' does not exist. No need to remove.${NC}"
    fi
}

# Function to create a new resource group
create_resource_group() {
    echo -e "${YELLOW}Creating resource group '$RESOURCE_GROUP'...${NC}"
    az group create --name $RESOURCE_GROUP --location $LOCATION
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create resource group. Exiting.${NC}"
        exit 1
    fi
    echo -e "${GREEN}Resource group created successfully.${NC}"
}

# Function to create an App Service Plan
create_app_service_plan() {
    echo -e "${YELLOW}Creating App Service Plan '$APP_SERVICE_PLAN'...${NC}"
    az appservice plan create --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP --sku $SKU --is-linux
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create App Service Plan. Exiting.${NC}"
        exit 1
    fi
    echo -e "${GREEN}App Service Plan created successfully.${NC}"
}

# Function to create a Web App
create_web_app() {
    echo -e "${YELLOW}Creating Web App '$APP_NAME'...${NC}"
    az webapp create --name $APP_NAME --resource-group $RESOURCE_GROUP --plan $APP_SERVICE_PLAN --runtime "PYTHON|$PYTHON_VERSION"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create Web App. Exiting.${NC}"
        exit 1
    fi
    echo -e "${GREEN}Web App created successfully.${NC}"
}

# Function to configure the Web App
configure_web_app() {
    echo -e "${YELLOW}Configuring Web App...${NC}"
    
    # Set startup file to startup.sh
    echo -e "${YELLOW}Setting startup file to startup.sh...${NC}"
    az webapp config set --name $APP_NAME --resource-group $RESOURCE_GROUP --startup-file "startup.sh"
    
    # Set environment variables
    echo -e "${YELLOW}Setting environment variables...${NC}"
    az webapp config appsettings set --name $APP_NAME --resource-group $RESOURCE_GROUP --settings FLASK_APP=app.py FLASK_ENV=production SCM_DO_BUILD_DURING_DEPLOYMENT=true
    
    echo -e "${GREEN}Web App configured successfully.${NC}"
}

# Function to update requirements.txt for Azure compatibility
update_requirements() {
    echo -e "${YELLOW}Updating requirements.txt for Azure compatibility...${NC}"
    
    # Create a backup of the original requirements.txt
    cp requirements.txt requirements.txt.bak
    
    # Create a simplified requirements.txt for Azure compatibility
    cat > requirements.txt << EOL
Flask==2.2.5
Flask-SQLAlchemy==3.0.3
Jinja2==3.1.2
MarkupSafe==2.1.3
SQLAlchemy==2.0.23
Werkzeug==2.2.3
click==8.1.3
itsdangerous==2.1.2
python-dotenv==1.0.0
requests==2.28.2
gunicorn==21.2.0
pandas==1.5.3
numpy==1.24.3
python-dateutil==2.8.2
pytz==2023.3
openpyxl==3.1.2
EOL
    
    echo -e "${GREEN}Requirements.txt updated for Azure compatibility.${NC}"
    echo -e "${YELLOW}Original requirements saved as requirements.txt.bak${NC}"
}

# Function to prepare the application for deployment
prepare_app() {
    echo -e "${YELLOW}Preparing application for deployment...${NC}"
    
    # Make sure startup.sh is executable
    chmod +x startup.sh
    
    # Create a deployment zip file
    echo -e "${YELLOW}Creating deployment package...${NC}"
    rm -f app.zip
    zip -r app.zip . -x ".*" -x "__pycache__/*" -x "*.pyc" -x "*.pyo" -x "*.pyd" -x "env/*" -x "venv/*" -x "*.zip" -x "instance/*" -x "webapp_logs/*"
    
    echo -e "${GREEN}Application prepared for deployment.${NC}"
}

# Function to deploy the application
deploy_app() {
    echo -e "${YELLOW}Deploying application to Azure...${NC}"
    
    # Use the newer az webapp deploy command instead of the deprecated config-zip command
    az webapp deploy --resource-group $RESOURCE_GROUP --name $APP_NAME --src-path app.zip --type zip
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Deployment failed. Please check the error message above.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Application deployed successfully!${NC}"
}

# Function to verify deployment
verify_deployment() {
    echo -e "${YELLOW}Verifying deployment...${NC}"
    
    # Get the current state of the web app
    APP_STATE=$(az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query "state" -o tsv)
    
    if [ "$APP_STATE" == "Running" ]; then
        echo -e "${GREEN}Web App is in 'Running' state.${NC}"
    else
        echo -e "${YELLOW}Web App is in '$APP_STATE' state. It may still be starting up.${NC}"
    fi
    
    # Show the application URL
    APP_URL=$(az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query "defaultHostName" -o tsv)
    echo -e "${GREEN}Application URL: https://$APP_URL${NC}"
}

# Function to show application logs
show_logs() {
    echo -e "${YELLOW}Showing application logs (press Ctrl+C to stop)...${NC}"
    az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP
}

# Function to show application URL and additional information
show_app_info() {
    echo -e "${BLUE}=================================================${NC}"
    echo -e "${GREEN}Deployment completed!${NC}"
    echo -e "${BLUE}=================================================${NC}"
    
    APP_URL=$(az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query "defaultHostName" -o tsv)
    
    echo -e "Your application is now available at:"
    echo -e "${BLUE}https://$APP_URL${NC}"
    echo ""
    echo -e "To view application logs, run:"
    echo -e "${YELLOW}az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP${NC}"
    echo ""
    echo -e "To restart the application, run:"
    echo -e "${YELLOW}az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP${NC}"
    echo ""
    echo -e "To delete all resources when no longer needed, run:"
    echo -e "${RED}az group delete --name $RESOURCE_GROUP --yes${NC}"
    echo -e "${BLUE}=================================================${NC}"
}

# Main execution flow
main() {
    check_az_cli
    check_azure_login
    
    # Ask if user wants to remove existing resources
    read -p "Do you want to remove existing Azure resources before deployment? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        remove_existing_resources
    fi
    
    create_resource_group
    create_app_service_plan
    create_web_app
    configure_web_app
    
    # Ask if user wants to update requirements.txt for Azure compatibility
    read -p "Do you want to update requirements.txt for Azure compatibility? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        update_requirements
    fi
    
    prepare_app
    deploy_app
    verify_deployment
    
    # Ask if user wants to view logs
    read -p "Do you want to view application logs? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        show_logs
    fi
    
    show_app_info
    
    # Restore original requirements.txt if it was modified
    if [ -f "requirements.txt.bak" ]; then
        read -p "Do you want to restore the original requirements.txt? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            mv requirements.txt.bak requirements.txt
            echo -e "${GREEN}Original requirements.txt restored.${NC}"
        fi
    fi
}

# Execute the main function
main
