import random

class Miembro:
    def __init__(self, nombre, tipo_orador="orador", puntos_orador:int = 0):
        self.nombre = nombre
        self.puntos_orador = puntos_orador
        self.tipo_orador = tipo_orador

class Equipo:
    def __init__(self, nombre: str, miembros: list[Miembro], victorias: int = 0, items: int = 0):
        self.nombre = nombre
        self.victorias = victorias
        self.items = items
        self.miembros = miembros
        self.equipos_contra = []

def registrar_equipo(equipos: list[Equipo], nombre_equipo: str, miembros: list[dict], victorias=0, items=0):
    """
    Registra un nuevo equipo en la lista de equipos.
    
    Args:
        equipos (list[Equipo]): Lista global de equipos.
        nombre_equipo (str): Nombre del equipo.
        miembros (list[dict]): Lista de diccionarios con la información de los miembros ({'nombre': str, 'puntos_orador': int}).
        victorias (int): Número de victorias del equipo.
        items (int): Número de ítems del equipo.
    """
    # Validar que el equipo tenga entre 2 y 5 miembros
    if len(miembros) < 2 or len(miembros) > 5:
        raise ValueError("El equipo debe tener entre 2 y 5 miembros.")

    # Crear objetos Miembro para cada diccionario en la lista
    miembros_objetos = [Miembro(nombre=miembro['nombre'], puntos_orador=miembro.get('puntos_orador', 0)) for miembro in miembros]

    # Crear el equipo con las victorias e ítems proporcionados
    nuevo_equipo = Equipo(nombre=nombre_equipo, miembros=miembros_objetos, victorias=victorias, items=items)
    equipos.append(nuevo_equipo)


def enfrentamientos_iniciales(equipos: list[Equipo]):

    # Si hay un número impar de equipos y no existe un "Swing", crearlo
    if len(equipos) % 2 != 0 :
        swing_team = Equipo(nombre='Swing', miembros=[])
        equipos.append(swing_team)
        print("Equipo 'Swing' creado.")  # Para depuración

    # Mezclar los equipos y generar los enfrentamientos
    equipos_temp = equipos.copy()  # Trabajar con una copia para no modificar la lista original
    random.shuffle(equipos_temp)

    emparejamientos = [(equipos_temp[i], equipos_temp[i+1]) for i in range(0, len(equipos_temp), 2)]
    emparejamientos_real = []

    for equipo_a, equipo_b in emparejamientos:
        equipo_a.equipos_contra.append(equipo_b.nombre)
        equipo_b.equipos_contra.append(equipo_a.nombre)
        emparejamientos_real.append([equipo_a.nombre, equipo_b.nombre])

    return emparejamientos_real

def enfrentamientos_clasificatoria(equipos: list[Equipo]):
    equipos_ordenados = sorted(equipos, key=lambda equipo: (equipo.victorias, equipo.items), reverse=True)
    emparejamientos = []
    i = 0

    while i < len(equipos_ordenados) - 1:
        equipo_a = equipos_ordenados[i]
        equipo_b = equipos_ordenados[i + 1]

        # Emparejar sin restricciones de enfrentamientos anteriores
        emparejamientos.append([equipo_a.nombre, equipo_b.nombre])

        # Eliminar los equipos emparejados de la lista para no emparejarlos nuevamente
        equipos_ordenados.pop(i)
        equipos_ordenados.pop(i)  # El índice de equipo_b cambia después de eliminar equipo_a

    return emparejamientos


def resultados_ronda(equipos: list[Equipo], resultados: dict, items_de_equipo: dict, puntos_orador: dict):
    """
    Actualiza las estadísticas de los equipos y oradores basándose en los resultados de una ronda.
    
    Args:
        equipos (list[Equipo]): Lista de equipos.
        resultados (dict): Diccionario con los resultados de la ronda (equipo ganador).
        items_de_equipo (dict): Diccionario con los ítems ganados por cada equipo.
        puntos_orador (dict): Diccionario con los puntos de orador ganados por cada miembro.
    """
    for equipo in equipos:
        if equipo.nombre in resultados:
            equipo.victorias += resultados[equipo.nombre]
        if equipo.nombre in items_de_equipo:
            equipo.items += items_de_equipo[equipo.nombre]
        for miembro in equipo.miembros:
            if miembro.nombre in puntos_orador:
                miembro.puntos_orador += puntos_orador[miembro.nombre]

def fases_finales(equipos, fase):
    if fase == "octavos":
        fase = 16
    elif fase == "cuartos":
        fase = 8
    elif fase == "semifinales":
        fase = 4
    elif fase == "final":
        fase = 2
    else:
        raise ValueError("Fase no válida")

    equipos_ordenados = sorted(equipos, key=lambda equipo: (equipo.victorias, equipo.items), reverse=True)
    equipos_clasifican = equipos_ordenados[:fase]
    enfrentamientos = []

    for i in range(fase // 2):
        enfrentamientos.append([equipos_clasifican[i].nombre, equipos_clasifican[fase - 1 - i].nombre])

    return equipos_clasifican, enfrentamientos

