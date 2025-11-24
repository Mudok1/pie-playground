"""
Utilidades para mostrar información de pasajeros del Titanic.
"""


def print_passenger_details(passenger_ids, passenger_lookup, embarked_map, title="Resultado"):
    """
    Imprime detalles de los primeros 10 pasajeros de una lista.
    
    Args:
        passenger_ids: Set o lista de IDs de pasajeros
        passenger_lookup: Diccionario de lookup de pasajeros
        embarked_map: Diccionario para mapear códigos de embarque a ciudades
        title: Título para la impresión (default: "Resultado")
    """
    data_list = list(passenger_ids)
    preview_ids = data_list[:10]
    print(f"{title} ({len(data_list)} total):")
    
    for pid in preview_ids:
        if pid in passenger_lookup:
            p = passenger_lookup[pid]
            embarked_code = p.get('Embarked', '?')
            embarked_full = embarked_map.get(embarked_code, embarked_code)
            fare = p.get('Fare', 0.0)
            
            print(f" --- Pasajero ID: {pid} ---")
            print(f" Nombre: {p.get('Name', 'N/A')}")
            print(f" Edad: {p.get('Age', 'N/A')}")
            print(f" Sexo: {p.get('Sex', 'N/A')}")
            print(f" Clase: {p.get('Pclass', 'N/A')}")
            print(f" Ticket: {p.get('Ticket', 'N/A')}")
            print(f" Tarifa: £{fare:.2f}")
            print(f" Cabina: {p.get('Cabin', 'N/A')}")
            print(f" Embarcado en: {embarked_full}")
            print(f" Familia (SibSp/Parch): {p.get('SibSp', 0)}/{p.get('Parch', 0)}")
            print(" ---------------------------")
        else:
            print(f" - ID: {pid} (No info)")
    
    if len(data_list) > 10:
        print(" ...")
