# Accédez au conteneur Docker :

docker exec -it oracle-db bash

# Lancez SQL*Plus comme administrateur :
sqlplus / as sysdba

# Vérifiez si l'utilisateur elax_db existe :

SELECT username FROM dba_users WHERE username = 'ELAX_DB';

# Si aucun résultat n’est retourné, l’utilisateur n’a pas été créé.
# 2. Créez ou corrigez l’utilisateur.
# Si l'utilisateur n'existe pas, créez-le avec le mot de passe correct :

ALTER SESSION SET CONTAINER = ORCLPDB1;

CREATE USER elax_db IDENTIFIED BY elaxnkm;
GRANT CONNECT, RESOURCE TO elax_db;
GRANT UNLIMITED TABLESPACE TO elax_db;
ALTER USER elax_db QUOTA UNLIMITED ON USERS;


# Importer la base de donnée
# Une fois connecté à sqlplus :

@/sql/elax.sql 


# Si l'utilisateur existe, réinitialisez son mot de passe pour être sûr :

ALTER SESSION SET CONTAINER = ORCLPDB1;

ALTER USER elax_db IDENTIFIED BY elaxnkm;
# 3. Vérifiez le service ORCLPDB1.
# Assurez-vous que le conteneur utilise bien ORCLPDB1 comme nom de service. Testez les services disponibles :

SELECT name, open_mode FROM v$pdbs;
Assurez-vous que ORCLPDB1 est bien dans le mode READ WRITE.




# 4. Assurez-vous que l’utilisateur est dans ORCLPDB1.
# L’utilisateur doit être créé dans le conteneur ORCLPDB1. Si ce n'est pas le cas, vous devez spécifier ce conteneur dans votre 

ALTER SESSION SET CONTAINER = ORCLPDB1;

# __________________-------------______





# 1 - Accédez au conteneur Docker :

docker exec -it oracle-elax-db bash

# Verify the directory exists ( la ou se trouve le dump ):
ls /opt/oracle/dumps

# Se connecter en tant que SYSDBA
sqlplus / as sysdba

# Basculer vers le PDB (Pluggable Database)
ALTER SESSION SET CONTAINER = ORCLPDB1;

# Assurez-vous que le répertoire /opt/oracle/dumps est bien mappé dans votre
CREATE DIRECTORY DUMP_DIR AS '/opt/oracle/dumps';
GRANT READ, WRITE ON DIRECTORY DUMP_DIR TO SYSTEM;

# Restaurer le dump
sqlplus / as sysdba
CREATE OR REPLACE DIRECTORY DUMP_DIR AS '/opt/oracle/dumps';
GRANT READ, WRITE ON DIRECTORY DUMP_DIR TO elax_db;

# Lancer cette commande pour restauré la base de données
docker exec -it oracle-elax-db /opt/oracle/product/19c/dbhome_1/bin/impdp elax_db/elaxnkm@ORCLPDB1 DUMPFILE=ELAX.dump DIRECTORY=DUMP_DIR FULL=Y


# docker exec -it oracle-elax-db /opt/oracle/product/19c/dbhome_1/bin/impdp SYSTEM/Oracle_12c@ORCLPDB1 DUMPFILE=ELAX.dump DIRECTORY=DUMP_DIR FULL=Y

