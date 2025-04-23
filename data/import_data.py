import csv
import sqlite3
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Nombre del archivo CSV y de la base de datos
csv_filename = os.path.join(script_dir, 'Inventario_Fisico poli.txt')  # Path relative to script
db_filename = os.path.join(script_dir, 'inventory.db')  # Database in same directory as script

print(f"Looking for CSV file at: {csv_filename}")
print(f"Database will be created at: {db_filename}")

# Check if the CSV file exists
if not os.path.exists(csv_filename):
    print(f"Error: The CSV file was not found at {csv_filename}")
    print("Please make sure the file exists and try again.")
    print("Available files in the current directory:")
    for file in os.listdir(script_dir):
        print(f"  - {file}")
    exit(1)

# Conectar a la base de datos SQLite (se crea si no existe)
conn = sqlite3.connect(db_filename)
cursor = conn.cursor()

# Crear la tabla 'producto' si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS producto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        cantidad REAL
    )
''')

# Abrir y leer el archivo CSV
with open(csv_filename, newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        # Verifica que la fila tenga al menos 6 campos
        if len(row) >= 6:
            nombre = row[1].strip()  # Segunda columna
            cantidad_str = row[5].strip()  # Sexta columna

            # Elimina posibles comas usadas como separador de miles y convierte a float
            if cantidad_str:
                cantidad_str = cantidad_str.replace(',', '')
                try:
                    cantidad = float(cantidad_str)
                except ValueError:
                    cantidad = 0.0
            else:
                cantidad = 0.0

            # Insertar los datos en la tabla producto
            cursor.execute('''
                INSERT INTO producto (nombre, cantidad)
                VALUES (?, ?)
            ''', (nombre, cantidad))

# Guardar los cambios y cerrar la conexión
conn.commit()
conn.close()

print("Datos importados correctamente a inventory.db")