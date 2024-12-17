import subprocess
import os

class OracleDatabaseSetup:
    def __init__(self, container_name='oracle-elax-db', 
                 pdb_name='ORCLPDB1', 
                 username='elax_db', 
                 password='elaxnkm'):
        self.container_name = container_name
        self.pdb_name = pdb_name
        self.username = username
        self.password = password
        self.dump_file = 'ELAX.dump'
        self.dump_directory = '/opt/oracle/dumps'

    def execute_docker_command(self, command):
        """Exécute une commande dans le conteneur Docker"""
        full_command = f'docker exec -it {self.container_name} {command}'
        print(f"Exécution : {full_command}")
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Erreur : {result.stderr}")
            return False
        
        print(result.stdout)
        return True

    def check_dump_availability(self):
        """Vérifie la disponibilité des fichiers de dump"""
        command = f'ls {self.dump_directory}'
        return self.execute_docker_command(command)

    def connect_as_sysdba(self):
        """Se connecte à Oracle en tant que SYSDBA via sqlplus"""
        sqlplus_commands = f"""
        sqlplus / as sysdba <<EOF
        ALTER SESSION SET CONTAINER = {self.pdb_name};
        exit;
        EOF
        """
        command = f'docker exec -i {self.container_name} bash -c "{sqlplus_commands}"'
        return self.execute_docker_command(command)

    def create_user(self):
        """Crée l'utilisateur et lui attribue les permissions"""
        sqlplus_commands = [
            f"sqlplus / as sysdba",
            f"ALTER SESSION SET CONTAINER = {self.pdb_name};",
            f"BEGIN",
            f"  IF NOT EXISTS (SELECT 1 FROM dba_users WHERE username = 'ELAX_DB') THEN",
            f"    EXECUTE IMMEDIATE 'CREATE USER {self.username} IDENTIFIED BY {self.password}';",
            f"    EXECUTE IMMEDIATE 'GRANT CONNECT, RESOURCE TO {self.username}';",
            f"    EXECUTE IMMEDIATE 'GRANT UNLIMITED TABLESPACE TO {self.username}';",
            f"    EXECUTE IMMEDIATE 'ALTER USER {self.username} QUOTA UNLIMITED ON USERS';",
            f"  END IF;",
            f"END;",
            f"/",
            f"exit"
        ]
        command = f'bash -c "echo -e \'{chr(10).join(sqlplus_commands)}\' | docker exec -i {self.container_name} sqlplus"'
        return self.execute_docker_command(command)

    def create_dump_directory(self):
        """Crée un répertoire Oracle pour le dump"""
        sqlplus_commands = [
            f"sqlplus / as sysdba",
            f"ALTER SESSION SET CONTAINER = {self.pdb_name};",
            f"CREATE DIRECTORY DUMP_DIR AS '{self.dump_directory}';",
            f"GRANT READ, WRITE ON DIRECTORY DUMP_DIR TO {self.username};",
            f"exit"
        ]
        command = f'bash -c "echo -e \'{chr(10).join(sqlplus_commands)}\' | docker exec -i {self.container_name} sqlplus"'
        return self.execute_docker_command(command)

    def restore_database(self):
        """Restaure la base de données à partir du dump"""
        impdp_command = (
            f"/opt/oracle/product/19c/dbhome_1/bin/impdp "
            f"{self.username}/{self.password}@{self.pdb_name} "
            f"DUMPFILE={self.dump_file} "
            f"DIRECTORY=DUMP_DIR FULL=Y"
        )
        return self.execute_docker_command(impdp_command)

    def run_full_setup(self):
        """Exécute toutes les étapes de configuration"""
        steps = [
            ("Vérification des dumps", self.check_dump_availability),
            ("Connexion SYSDBA", self.connect_as_sysdba),
            ("Création de l'utilisateur", self.create_user),
            ("Création du répertoire de dump", self.create_dump_directory),
            ("Restauration de la base de données", self.restore_database)
        ]

        for step_name, step_function in steps:
            print(f"\n--- {step_name} ---")
            result = step_function()
            if not result:
                print(f"Échec lors de l'étape : {step_name}")
                return False
        
        print("\n✅ Configuration et restauration terminées avec succès !")
        return True

def main():
    setup = OracleDatabaseSetup()
    setup.run_full_setup()

if __name__ == "__main__":
    main()