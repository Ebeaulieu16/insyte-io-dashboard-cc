#!/bin/bash

echo "Démarrage de l'API simplifiée pour Insyte.io Dashboard..."
echo "L'API sera accessible à l'adresse : http://localhost:9000"
echo "Documentation Swagger : http://localhost:9000/docs"
echo ""

# Exécution du serveur FastAPI
python3 -m uvicorn simple_api:app --host 0.0.0.0 --port 9000 --reload 