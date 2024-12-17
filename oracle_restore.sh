#!/bin/bash

# Configuration des variables
CONTAINER_NAME="oracle-elax-db"
DB_USER="elax_db"
DB_PASSWORD="elaxnkm"
PDB_NAME="ORCLPDB1"
DUMP_FILE="ELAX.dump"
DUMP_DIR="/opt/oracle/dumps"

# Fonction de gestion des erreurs
handle_error() {
    echo "Erreur: $1"
    exit 1
}

# Étape 1 : Vérifier l'existence du conteneur
docker ps | grep $CONTAINER_NAME > /dev/null || handle_error "Le conteneur $CONTAINER_NAME n'existe pas"

# Étape 2 : Connexion et configuration SQL
docker exec -it $CONTAINER_NAME bash -c "
sqlplus / as sysdba << EOF
-- Basculer sur le container PDB
ALTER SESSION SET CONTAINER = $PDB_NAME;

-- Vérifier si l'utilisateur existe
DECLARE
    user_exists NUMBER;
BEGIN
    SELECT COUNT(*) INTO user_exists 
    FROM dba_users 
    WHERE username = UPPER('$DB_USER');
    
    IF user_exists = 0 THEN
        -- Créer l'utilisateur s'il n'existe pas
        EXECUTE IMMEDIATE 'CREATE USER $DB_USER IDENTIFIED BY $DB_PASSWORD';
        EXECUTE IMMEDIATE 'GRANT CONNECT, RESOURCE TO $DB_USER';
        EXECUTE IMMEDIATE 'GRANT UNLIMITED TABLESPACE TO $DB_USER';
        EXECUTE IMMEDIATE 'ALTER USER $DB_USER QUOTA UNLIMITED ON USERS';
        
        DBMS_OUTPUT.PUT_LINE('Utilisateur $DB_USER créé avec succès');
    ELSE
        DBMS_OUTPUT.PUT_LINE('Utilisateur $DB_USER existe déjà');
    END IF;
END;
/

-- Créer le répertoire pour le dump
CREATE OR REPLACE DIRECTORY DUMP_DIR AS '$DUMP_DIR';

-- Donner les permissions sur le répertoire
GRANT READ, WRITE ON DIRECTORY DUMP_DIR TO $DB_USER;

EXIT;
EOF
"

# Étape 3 : Restauration du dump
docker exec -it $CONTAINER_NAME /opt/oracle/product/19c/dbhome_1/bin/impdp \
    $DB_USER/$DB_PASSWORD@$PDB_NAME \
    DUMPFILE=$DUMP_FILE \
    DIRECTORY=DUMP_DIR \
    FULL=Y \
    || handle_error "Échec de l'import du dump"

echo "Configuration et restauration terminées avec succès !"