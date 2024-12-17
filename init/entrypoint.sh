#!/bin/bash
# Démarrer le listener avant toute opération
lsnrctl start

# Attendre que la base de données soit prête
# (ajoutez une boucle de vérification)
while ! sqlplus -S sys/Oracle_12c@//localhost:1521/xe as sysdba <<< "SELECT status FROM v\$instance" 2>/dev/null; do
    echo "Attente de la base de données..."
    sleep 5
done

# Créer le répertoire
sqlplus sys/Oracle_12c@//localhost:1521/xe as sysdba <<EOF
CREATE DIRECTORY ORCL_DIR AS '/opt/oracle/dumps';
GRANT READ, WRITE ON DIRECTORY ORCL_DIR TO system;
EOF

echo "Conteneur Oracle prêt"