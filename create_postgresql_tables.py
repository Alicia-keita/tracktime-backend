#!/usr/bin/env python
"""
Script pour créer les tables PostgreSQL avec la structure complète
"""

import os
import sys
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')

def get_table_structures():
    """Obtenir les structures des tables depuis SQLite"""
    print("🔍 Analyse des structures de tables...")
    
    django.setup()
    from django.db import connection
    
    structures = {}
    
    # Lister toutes les tables
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = cursor.fetchall()
        
        for table_name, in tables:
            print(f"📋 Analyse de la table: {table_name}")
            
            # Obtenir la structure de la table
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Obtenir les index
            cursor.execute(f"PRAGMA index_list({table_name})")
            indexes = cursor.fetchall()
            
            # Obtenir les clés étrangères
            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            foreign_keys = cursor.fetchall()
            
            structures[table_name] = {
                'columns': columns,
                'indexes': indexes,
                'foreign_keys': foreign_keys
            }
    
    return structures

def generate_postgresql_sql(structures):
    """Générer les commandes SQL PostgreSQL"""
    print("\n📝 Génération des commandes SQL PostgreSQL...")
    
    django.setup()
    from django.db import connection
    
    sql_commands = "-- Création des tables pour PostgreSQL\n\n"
    
    for table_name, structure in structures.items():
        print(f"🔧 Génération SQL pour: {table_name}")
        
        sql_commands += f"-- Table: {table_name}\n"
        sql_commands += f"CREATE TABLE {table_name} (\n"
        
        # Colonnes
        columns_sql = []
        for col in structure['columns']:
            cid, name, col_type, not_null, default_val, pk = col
            
            # Convertir les types SQLite vers PostgreSQL
            pg_type = convert_sqlite_to_postgresql_type(col_type)
            
            col_sql = f"    {name} {pg_type}"
            
            if pk == 1:
                col_sql += " PRIMARY KEY"
            
            if not_null == 1 and pk == 0:
                col_sql += " NOT NULL"
            
            if default_val is not None:
                if default_val.startswith("'"):
                    col_sql += f" DEFAULT {default_val}"
                else:
                    col_sql += f" DEFAULT {default_val}"
            
            columns_sql.append(col_sql)
        
        sql_commands += ",\n".join(columns_sql)
        
        # Clés étrangères
        if structure['foreign_keys']:
            sql_commands += ",\n    -- Foreign Keys\n"
            for fk in structure['foreign_keys']:
                id, seq, table, from_col, to_col, on_update, on_delete, match = fk
                sql_commands += f"    FOREIGN KEY ({from_col}) REFERENCES {table}({to_col})\n"
        
        sql_commands += ");\n\n"
    
    # Index
    for table_name, structure in structures.items():
        if structure['indexes']:
            sql_commands += f"-- Index pour {table_name}\n"
            for idx in structure['indexes']:
                seq, name, unique, origin, partial = idx
                if not name.startswith('sqlite_'):
                    sql_commands += f"CREATE {'UNIQUE ' if unique else ''}INDEX {name} ON {table_name} ("
                    
                    # Obtenir les colonnes de l'index
                    with connection.cursor() as cursor:
                        cursor.execute(f"PRAGMA index_info({name})")
                        index_cols = cursor.fetchall()
                    
                    col_names = [col[2] for col in index_cols]
                    sql_commands += ", ".join(col_names)
                    sql_commands += ");\n"
            sql_commands += "\n"
    
    return sql_commands

def convert_sqlite_to_postgresql_type(sqlite_type):
    """Convertir les types SQLite vers PostgreSQL"""
    type_mapping = {
        'INTEGER': 'INTEGER',
        'TEXT': 'TEXT',
        'REAL': 'REAL',
        'NUMERIC': 'NUMERIC',
        'BLOB': 'BYTEA',
        'VARCHAR': 'VARCHAR',
        'CHAR': 'CHAR',
        'DATETIME': 'TIMESTAMP',
        'DATE': 'DATE',
        'BOOLEAN': 'BOOLEAN',
        'DECIMAL': 'DECIMAL',
        'FLOAT': 'FLOAT',
        'DOUBLE': 'DOUBLE PRECISION',
        'BIGINT': 'BIGINT',
        'SMALLINT': 'SMALLINT'
    }
    
    # Gérer les types avec parenthèses
    if '(' in sqlite_type:
        base_type = sqlite_type.split('(')[0].upper()
        params = sqlite_type.split('(')[1]
        
        if base_type in ['VARCHAR', 'CHAR', 'DECIMAL', 'NUMERIC']:
            return f"{base_type}({params}"
        elif base_type == 'DOUBLE':
            return 'DOUBLE PRECISION'
    
    # Conversion simple
    base_type = sqlite_type.upper()
    return type_mapping.get(base_type, 'TEXT')

def save_sql_file(sql_commands):
    """Sauvegarder les commandes SQL dans un fichier"""
    with open('create_postgresql_tables.sql', 'w', encoding='utf-8') as f:
        f.write(sql_commands)
    
    print("✅ Fichier SQL créé: create_postgresql_tables.sql")

def create_migration_plan():
    """Créer un plan de migration"""
    plan = """
# PLAN DE MIGRATION VERS POSTGRESQL

## ÉTAPES:

### 1. Créer l'utilisateur PostgreSQL
```sql
-- Exécuter dans pgAdmin en tant que postgres
CREATE USER pointage_user WITH PASSWORD 'pointage123';
GRANT ALL PRIVILEGES ON DATABASE pointage TO pointage_user;
```

### 2. Créer les tables
```sql
-- Exécuter create_postgresql_tables.sql dans la base pointage
```

### 3. Mettre à jour settings.py
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pointage',
        'USER': 'pointage_user',
        'PASSWORD': 'pointage123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 4. Tester la connexion
```bash
python manage.py migrate
python manage.py runserver
```

### 5. Importer les données (optionnel)
```bash
python migrate_data.py
```
"""
    
    with open('MIGRATION_PLAN.md', 'w', encoding='utf-8') as f:
        f.write(plan)
    
    print("✅ Plan de migration créé: MIGRATION_PLAN.md")

if __name__ == '__main__':
    print("🗄️ CRÉATION DES TABLES POSTGRESQL")
    print("=" * 50)
    
    # Étape 1: Analyser les structures SQLite
    structures = get_table_structures()
    
    # Étape 2: Générer le SQL PostgreSQL
    sql_commands = generate_postgresql_sql(structures)
    
    # Étape 3: Sauvegarder le fichier SQL
    save_sql_file(sql_commands)
    
    # Étape 4: Créer le plan de migration
    create_migration_plan()
    
    print(f"\n🎉 STRUCTURES ANALYSÉES: {len(structures)} tables")
    
    print("\n📋 Tables trouvées:")
    for table_name in structures.keys():
        print(f"   ✅ {table_name}")
    
    print("\n🚀 PROCHAINES ÉTAPES:")
    print("1. Exécuter create_user.sql dans pgAdmin")
    print("2. Exécuter create_postgresql_tables.sql dans pgAdmin")
    print("3. Mettre à jour settings.py avec la configuration PostgreSQL")
    print("4. Tester: python manage.py migrate")
    print("5. Importer les données si nécessaire")
