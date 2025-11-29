import pandas as pd
import os
import sys

def get_resource_path(relative_path):

    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_titanic_sets():


    csv_filename = "Titanic-Dataset.csv" 
    
    csv_path = get_resource_path(csv_filename)
    
    if not os.path.exists(csv_path):
        csv_path = get_resource_path(os.path.join("data", csv_filename))

    print(f"Cargando datos desde: {csv_path}")

    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"ERROR CRÍTICO: No se encontró '{csv_filename}'. Asegúrate de que esté en la carpeta del proyecto.")
        return {}, {}

    sets = {}

    # --- 1. GÉNERO ---
    men_ids = set(df[df['Sex'] == 'male']['PassengerId'])
    sets['Hombres'] = {
        'count': len(men_ids),
        'color': (100, 149, 237), # Cornflower Blue
        'name': 'Hombres',
        'data': men_ids
    }

    women_ids = set(df[df['Sex'] == 'female']['PassengerId'])
    sets['Mujeres'] = {
        'count': len(women_ids),
        'color': (255, 105, 180), # Hot Pink
        'name': 'Mujeres',
        'data': women_ids
    }

    # --- 2. SUPERVIVENCIA ---
    survivor_ids = set(df[df['Survived'] == 1]['PassengerId'])
    sets['Sobrevivientes'] = {
        'count': len(survivor_ids),
        'color': (50, 205, 50), # Lime Green
        'name': 'Sobrevivientes',
        'data': survivor_ids
    }

    non_survivor_ids = set(df[df['Survived'] == 0]['PassengerId'])
    sets['No Sobrevivientes'] = {
        'count': len(non_survivor_ids),
        'color': (70, 70, 70), # Dark Grey
        'name': 'Fallecidos',
        'data': non_survivor_ids
    }

    # --- 3. CLASES ---
    colors_class = {1: (148, 0, 211), 2: (100, 100, 200), 3: (100, 200, 100)}
    names_class = {1: "1ra Clase", 2: "2da Clase", 3: "3ra Clase"}
    
    for pclass in [1, 2, 3]:
        ids = set(df[df['Pclass'] == pclass]['PassengerId'])
        sets[names_class[pclass]] = {
            'count': len(ids),
            'color': colors_class[pclass],
            'name': names_class[pclass],
            'data': ids
        }

    # --- 4. EDAD ---
    # Bebés (< 5)
    bebes_ids = set(df[df['Age'] < 5]['PassengerId'])
    sets['Bebés'] = {'count': len(bebes_ids), 'color': (255, 182, 193), 'name': 'Bebés', 'data': bebes_ids}
    
    # Niños (< 12)
    ninos_ids = set(df[df['Age'] < 12]['PassengerId'])
    sets['Niños'] = {'count': len(ninos_ids), 'color': (255, 215, 0), 'name': 'Niños', 'data': ninos_ids}
    
    # Adolescentes (12-17)
    adolescentes_ids = set(df[(df['Age'] >= 12) & (df['Age'] <= 17)]['PassengerId'])
    sets['Adolescentes'] = {'count': len(adolescentes_ids), 'color': (32, 178, 170), 'name': 'Adolescentes', 'data': adolescentes_ids}
    
    # Ancianos (60+)
    ancianos_ids = set(df[df['Age'] >= 60]['PassengerId'])
    sets['Ancianos'] = {'count': len(ancianos_ids), 'color': (192, 192, 192), 'name': 'Ancianos', 'data': ancianos_ids}

    # --- 5. SOCIAL / FAMILIA ---
    df['FamilySize'] = df['SibSp'] + df['Parch']
    
    # Viajeros Solos (familia == 0)
    solos_ids = set(df[df['FamilySize'] == 0]['PassengerId'])
    sets['Viajeros Solos'] = {'count': len(solos_ids), 'color': (100, 100, 100), 'name': 'Viajeros Solos', 'data': solos_ids}
    
    # Con Familia (familia > 0)
    familia_ids = set(df[df['FamilySize'] > 0]['PassengerId'])
    sets['Con Familia'] = {'count': len(familia_ids), 'color': (255, 165, 0), 'name': 'Con Familia', 'data': familia_ids}
    
    # Familias Grandes (>= 4)
    gran_familia_ids = set(df[df['FamilySize'] >= 4]['PassengerId'])
    sets['Familia Grande'] = {'count': len(gran_familia_ids), 'color': (255, 69, 0), 'name': 'Familia Grande', 'data': gran_familia_ids}

    # --- 6. ROLES / ESTATUS ---
    # Madres (Mujer, con hijos (Parch>0), >16 años)
    madres_ids = set(df[(df['Sex'] == 'female') & (df['Parch'] > 0) & (df['Age'] > 16)]['PassengerId'])
    sets['Madres'] = {'count': len(madres_ids), 'color': (255, 20, 147), 'name': 'Madres', 'data': madres_ids}
    
    # VIPs (Fare > 100)
    vips_ids = set(df[df['Fare'] > 100]['PassengerId'])
    sets['VIPs'] = {'count': len(vips_ids), 'color': (218, 165, 32), 'name': 'VIPs', 'data': vips_ids}

    # --- 7. PUERTOS ---
    sets['Puerto C'] = {'count': len(set(df[df['Embarked'] == 'C']['PassengerId'])), 'color': (0, 0, 139), 'name': 'Puerto C (Francia)', 'data': set(df[df['Embarked'] == 'C']['PassengerId'])}
    sets['Puerto Q'] = {'count': len(set(df[df['Embarked'] == 'Q']['PassengerId'])), 'color': (0, 100, 0), 'name': 'Puerto Q (Irlanda)', 'data': set(df[df['Embarked'] == 'Q']['PassengerId'])}
    sets['Puerto S'] = {'count': len(set(df[df['Embarked'] == 'S']['PassengerId'])), 'color': (139, 0, 0), 'name': 'Puerto S (Inglaterra)', 'data': set(df[df['Embarked'] == 'S']['PassengerId'])}

    # --- LOOKUP DICTIONARY ---
    # Convertimos el DataFrame a un diccionario indexado por PassengerId para búsquedas rápidas en la UI
    df_indexed = df.set_index('PassengerId')
    
    # Rellenamos NaNs para que no den problemas en la UI
    df_indexed['Age'] = df_indexed['Age'].fillna(-1)
    df_indexed['Fare'] = df_indexed['Fare'].fillna(0)
    
    passenger_lookup = df_indexed.to_dict(orient='index')

    return sets, passenger_lookup