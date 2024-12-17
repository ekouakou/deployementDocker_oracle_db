# README : Instructions pour configurer et restaurer la base de données avec Docker
# Ce guide décrit les étapes pour configurer une base de données Oracle dans un conteneur Docker, créer un utilisateur, et restaurer une base de données à partir d'un fichier de sauvegarde (dump).

# Lancer le conteneur Docker
# Pour démarrer les services Docker spécifiés dans le fichier docker-compose.yml :

docker compose up -d

# Explication :
# Cette commande démarre le conteneur en arrière-plan (-d pour detach mode). Assurez-vous que Docker est installé et en cours d'exécution sur votre système.

# Vérification de l'état de la base de données
# Étape importante :
# Après avoir lancé le conteneur, attendez que la base de données soit entièrement initialisée et prête à l'emploi. Cela peut prendre plusieurs minutes, selon votre environnement.

# Création de l'utilisateur de la base de données

# Étape 1 : Accéder au conteneur Docker
# Pour entrer dans le conteneur exécutant Oracle Database :

docker exec -it oracle-elax-db bash

# Explication :
# Cette commande ouvre un terminal interactif à l'intérieur du conteneur nommé oracle-elax-db.

# Étape 2 : Se connecter à Oracle en tant que SYSDBA
# Dans le terminal du conteneur, exécutez la commande suivante pour vous connecter en tant qu'administrateur Oracle :

sqlplus / as sysdba

# Étape 3 : Basculer vers la base de données pluggable (PDB)
# Passez à la base de données pluggable nommée ORCLPDB1 :

ALTER SESSION SET CONTAINER = ORCLPDB1;

# Étape 4 : Vérifier si l'utilisateur existe
# Vérifiez si l'utilisateur elax_db existe déjà :

SELECT username FROM dba_users WHERE username = 'ELAX_DB';

# Étape 5 : Créer l'utilisateur (si nécessaire)
# Si l'utilisateur n'existe pas, créez-le avec le mot de passe elaxnkm :

CREATE USER elax_db IDENTIFIED BY elaxnkm;
GRANT CONNECT, RESOURCE TO elax_db;
GRANT UNLIMITED TABLESPACE TO elax_db;
ALTER USER elax_db QUOTA UNLIMITED ON USERS;

# Explication :

# CREATE USER : Crée un nouvel utilisateur Oracle.
# GRANT CONNECT, RESOURCE : Donne les privilèges nécessaires pour se connecter et créer des objets.
# GRANT UNLIMITED TABLESPACE : Permet d'utiliser l'espace disque sans restriction.
# QUOTA UNLIMITED : Supprime les limites d'espace sur les tablespaces spécifiques.



# ======================= RESTAURATION DE LA BASE DE DONNEES ======================= 

# -------------------  Étape 1 : Importation d'une base de données sql ------------------- 

docker exec -it oracle-elax-db /opt/oracle/product/19c/dbhome_1/bin/sqlplus elax_db/elaxnkm@ORCLPDB1 @/opt/oracle/dumps/ELAX.sql
COMMIT;


# -------------------  Étape 1 : Vérifier la disponibilité des fichiers de dump ------------------- 
# Assurez-vous que le fichier de sauvegarde (dump) est présent dans le répertoire /opt/oracle/dumps à l'intérieur du conteneur :

ls /opt/oracle/dumps

# Passez à la base de données pluggable nommée ORCLPDB1 :

ALTER SESSION SET CONTAINER = ORCLPDB1;


ALTER SESSION SET CONTAINER = FREEPDB1;
# -------------------  Étape 2 : Créer un répertoire Oracle pour le dump ------------------- 

# Dans Oracle SQL*Plus, exécutez la commande suivante pour créer un répertoire logique pointant vers le chemin où se trouve le dump :

CREATE DIRECTORY DUMP_DIR AS '/opt/oracle/dumps';

# Explication :
# CREATE DIRECTORY permet à Oracle de référencer un chemin sur le système de fichiers à l'intérieur du conteneur.

# ------------------- Étape 3 : Donner les permissions sur le répertoire ------------------- 

# Attribuez les permissions de lecture et d'écriture sur ce répertoire à l'utilisateur elax_db :

GRANT READ, WRITE ON DIRECTORY DUMP_DIR TO elax_db;

# Explication :
# Ces permissions permettent à l'utilisateur elax_db d'importer des fichiers à partir du répertoire spécifié.

# ------------------- Étape 4 : Restaurer le dump avec impdp ------------------- 

# Pour importer les données à partir du fichier ELAX.dump, exécutez la commande suivante dans le conteneur :

docker exec -it oracle-elax-db /opt/oracle/product/19c/dbhome_1/bin/impdp elax_db/elaxnkm@ORCLPDB1 DUMPFILE=ELAX.dump DIRECTORY=DUMP_DIR FULL=Y


docker exec -it oracle-elax-db /opt/oracle/product/19c/dbhome_1/bin/impdp elax_db/elaxnkm@FREEPDB1 DUMPFILE=ELAX.dump DIRECTORY=DUMP_DIR FULL=Y


# Explication :

#  impdp : Utilitaire Oracle pour importer des données à partir d'un fichier de dump.
#  DUMPFILE=ELAX.dump : Spécifie le fichier de dump à importer.
#  DIRECTORY=DUMP_DIR : Indique le répertoire logique où se trouve le fichier dump.
#  FULL=Y : Indique que l'import doit inclure toutes les données du fichier dump.
