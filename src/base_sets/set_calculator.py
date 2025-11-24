import pandas as pd
import os

def get_titanic_sets():
    """
    Lee el archivo CSV del Titanic y genera un diccionario de sets
    con el formato esperado por la UI de pie-playground.
    """
    # Ruta relativa al archivo desde este script
    # Asumimos que la estructura es:
    # root/
    #   data/Titanic-Dataset.csv
    #   src/base_sets/set_calculator.py
    
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    csv_path = os.path.join(base_path, 'data', 'Titanic-Dataset.csv')
    
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en {csv_path}")
        return {}

    sets = {}

    # 1. Hombres
    men_ids = set(df[df['Sex'] == 'male']['PassengerId'])
    sets['Hombres'] = {
        'count': len(men_ids),
        'color': (100, 149, 237), # Cornflower Blue
        'name': 'Hombres',
        'data': men_ids
    }

    # 2. Mujeres
    women_ids = set(df[df['Sex'] == 'female']['PassengerId'])
    sets['Mujeres'] = {
        'count': len(women_ids),
        'color': (255, 105, 180), # Hot Pink
        'name': 'Mujeres',
        'data': women_ids
    }

    # 3. Niños (< 18)
    children_ids = set(df[df['Age'] < 18]['PassengerId'])
    sets['Niños'] = {
        'count': len(children_ids),
        'color': (255, 215, 0), # Gold
        'name': 'Niños',
        'data': children_ids
    }

    # 4. Sobrevivientes (Survived == 1)
    survivor_ids = set(df[df['Survived'] == 1]['PassengerId'])
    sets['Sobrevivientes'] = {
        'count': len(survivor_ids),
        'color': (50, 205, 50), # Lime Green
        'name': 'Sobrevivientes',
        'data': survivor_ids
    }

    # 5. No Sobrevivientes (Survived == 0)
    non_survivor_ids = set(df[df['Survived'] == 0]['PassengerId'])
    sets['No Sobrevivientes'] = {
        'count': len(non_survivor_ids),
        'color': (70, 70, 70), # Dark Grey
        'name': 'No Sobrevivientes',
        'data': non_survivor_ids
    }

    # 6. Primera Clase (Pclass == 1) - YA EXISTE, pero agregamos las otras
    # CLASES
    for pclass in [1, 2, 3]:
        ids = set(df[df['Pclass'] == pclass]['PassengerId'])
        sets[f'Clase_{pclass}'] = {
            'count': len(ids),
            'color': (148, 0, 211) if pclass == 1 else ((100, 100, 200) if pclass == 2 else (100, 200, 100)),
            'name': f'Clase {pclass}',
            'data': ids
        }

    #  (< 5)
    bebes_ids = set(df[df['Age'] < 5]['PassengerId'])
    sets['Bebes'] = {'count': len(bebes_ids), 'color': (255, 182, 193), 'name': 'Bebes', 'data': bebes_ids}
    
    # Ninos (< 12)
    ninos_ids = set(df[df['Age'] < 12]['PassengerId'])
    sets['Ninos'] = {'count': len(ninos_ids), 'color': (135, 206, 235), 'name': 'Ninos', 'data': ninos_ids}
    
    # Adolescentes (12-17)
    adolescentes_ids = set(df[(df['Age'] >= 12) & (df['Age'] <= 17)]['PassengerId'])
    sets['Adolescentes'] = {'count': len(adolescentes_ids), 'color': (32, 178, 170), 'name': 'Adolescentes', 'data': adolescentes_ids}
    
    # Adultos (18-59)
    adultos_ids = set(df[(df['Age'] >= 18) & (df['Age'] <= 59)]['PassengerId'])
    sets['Adultos'] = {'count': len(adultos_ids), 'color': (112, 128, 144), 'name': 'Adultos', 'data': adultos_ids}
    
    # Ancianos (60+)
    ancianos_ids = set(df[df['Age'] >= 60]['PassengerId'])
    sets['Ancianos'] = {'count': len(ancianos_ids), 'color': (192, 192, 192), 'name': 'Ancianos', 'data': ancianos_ids}
    
    # Edad Desconocida
    edad_nan_ids = set(df[df['Age'].isna()]['PassengerId'])
    sets['Edad_Desconocida'] = {'count': len(edad_nan_ids), 'color': (50, 50, 50), 'name': 'Edad Desconocida', 'data': edad_nan_ids}

    # SOCIAL / FAMILIA
    # Calculamos familia
    df['FamilySize'] = df['SibSp'] + df['Parch']
    
    # Viajeros Solos (familia == 0)
    solos_ids = set(df[df['FamilySize'] == 0]['PassengerId'])
    sets['Viajeros Solos'] = {'count': len(solos_ids), 'color': (100, 100, 100), 'name': 'Viajeros Solos', 'data': solos_ids}
    
    # Con Familia (familia > 0)
    familia_ids = set(df[df['FamilySize'] > 0]['PassengerId'])
    sets['Con Familia'] = {'count': len(familia_ids), 'color': (255, 165, 0), 'name': 'Con Familia', 'data': familia_ids}
    
    gran_familia_ids = set(df[df['FamilySize'] >= 4]['PassengerId'])
    sets['Familia Grande'] = {'count': len(gran_familia_ids), 'color': (255, 69, 0), 'name': 'Familia Grande', 'data': gran_familia_ids}

    # ROLES
    # Madres (Mujer, con hijos (Parch>0), >16 años)
    madres_ids = set(df[(df['Sex'] == 'female') & (df['Parch'] > 0) & (df['Age'] > 16)]['PassengerId'])
    sets['Madres'] = {'count': len(madres_ids), 'color': (255, 20, 147), 'name': 'Madres', 'data': madres_ids}
    
    # VIPs (Fare > 100)
    vips_ids = set(df[df['Fare'] > 100]['PassengerId'])
    sets['VIPs'] = {'count': len(vips_ids), 'color': (218, 165, 32), 'name': 'VIPs', 'data': vips_ids}
    
    # Gratis (Fare == 0)
    gratis_ids = set(df[df['Fare'] == 0]['PassengerId'])
    sets['Gratis'] = {'count': len(gratis_ids), 'color': (0, 0, 0), 'name': 'Gratis', 'data': gratis_ids}

    # PUERTOS
    # Puerto C
    c_ids = set(df[df['Embarked'] == 'C']['PassengerId'])
    sets['Puerto_C'] = {'count': len(c_ids), 'color': (0, 0, 139), 'name': 'Puerto C', 'data': c_ids}
    
    # Puerto Q
    q_ids = set(df[df['Embarked'] == 'Q']['PassengerId'])
    sets['Puerto_Q'] = {'count': len(q_ids), 'color': (0, 100, 0), 'name': 'Puerto Q', 'data': q_ids}
    
    # Puerto S
    s_ids = set(df[df['Embarked'] == 'S']['PassengerId'])
    sets['Puerto_S'] = {'count': len(s_ids), 'color': (139, 0, 0), 'name': 'Puerto S', 'data': s_ids}


    df_indexed = df.set_index('PassengerId')

    passenger_lookup = df_indexed.to_dict(orient='index')

    return sets, passenger_lookup
