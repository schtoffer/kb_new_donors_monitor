from app import app

# This is needed for Azure App Service
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)