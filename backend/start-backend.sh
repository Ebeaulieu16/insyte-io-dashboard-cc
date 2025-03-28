#!/bin/bash

# Script pour démarrer le backend FastAPI

echo "===== Démarrage du backend FastAPI ====="

# Vérification de la présence de l'environnement virtuel
if [ ! -d "../venv-py311" ]; then
  echo "Erreur: L'environnement virtuel venv-py311 n'a pas été trouvé"
  echo "Exécutez d'abord: ../setup_venv.sh"
  exit 1
fi

# Activation de l'environnement virtuel
echo "Activation de l'environnement virtuel..."
source ../venv-py311/bin/activate

# Vérification de l'activation
if [ -z "$VIRTUAL_ENV" ]; then
  echo "Erreur: L'environnement virtuel n'a pas été activé correctement"
  exit 1
fi

# Affichage de la version Python
echo "Utilisation de Python: $(python --version)"

# Vérification des dépendances
echo "Vérification des dépendances..."
pip install -r requirements.txt

# Démarrage du serveur
echo "Démarrage du serveur FastAPI..."
echo "Le backend sera accessible à http://localhost:8000"
echo "L'API sera disponible à http://localhost:8000/docs"

# Exécution avec option de rechargement pour le développement
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 