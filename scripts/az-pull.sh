#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# App and resource group names
APP_NAME="kb-app-innsamling"
RESOURCE_GROUP="p-kb-app-innsamling"

# Function to print status messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed. Please install it first."
    echo "Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if user is logged in to Azure
print_status "Checking Azure login status..."
az account show &> /dev/null

if [ $? -ne 0 ]; then
    print_warning "You are not logged in to Azure."
    print_status "Please log in to Azure now..."
    
    # Attempt to login
    az login
    
    # Check if login was successful
    if [ $? -ne 0 ]; then
        print_error "Azure login failed. Exiting."
        exit 1
    else
        print_success "Successfully logged in to Azure."
    fi
else
    # Get account info and display it
    ACCOUNT_INFO=$(az account show --query "{Name:name, SubscriptionId:id, TenantId:tenantId}" -o json)
    ACCOUNT_NAME=$(echo $ACCOUNT_INFO | grep -o '"Name": *"[^"]*"' | cut -d'"' -f4)
    
    print_success "Already logged in to Azure as: $ACCOUNT_NAME"
fi

# Verify the resource group exists
print_status "Verifying resource group '$RESOURCE_GROUP' exists..."
if ! az group show --name "$RESOURCE_GROUP" &> /dev/null; then
    print_error "Resource group '$RESOURCE_GROUP' does not exist. Please check the name."
    exit 1
fi

# Verify the web app exists
print_status "Verifying web app '$APP_NAME' exists..."
if ! az webapp show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    print_error "Web app '$APP_NAME' does not exist in resource group '$RESOURCE_GROUP'. Please check the names."
    exit 1
fi

# Sync the deployment from the source
print_status "Syncing deployment from source for '$APP_NAME'..."
az webapp deployment source sync --name "$APP_NAME" --resource-group "$RESOURCE_GROUP"

if [ $? -eq 0 ]; then
    print_success "Deployment sync completed successfully!"
    
    # Get the app URL
    APP_URL=$(az webapp show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --query "defaultHostName" -o tsv)
    
    print_status "Your app is deployed at: https://$APP_URL"
    print_status "You can check the deployment logs with:"
    echo "az webapp log deployment show --name $APP_NAME --resource-group $RESOURCE_GROUP"
else
    print_error "Deployment sync failed. Please check the logs for more information."
    print_status "You can check the deployment logs with:"
    echo "az webapp log deployment show --name $APP_NAME --resource-group $RESOURCE_GROUP"
    exit 1
fi
