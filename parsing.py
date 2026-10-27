input_file = 'puco_2026-05.txt'
output_file = 'puco_2026-05.csv'

def limpiar_texto(texto):
    if not texto:
        return ""
    # Reemplazamos comillas dobles internas para que no rompan el formato CSV
    texto_limpio = texto.replace('"', '')
    return texto_limpio.strip()

def procesar_linea(linea):
    linea_limpia = linea.rstrip('\r\n')
    
    # Validamos longitud mínima
    if len(linea_limpia) < 22:
        return None
    
    # Cortes fijos según tu estructura
    dni = limpiar_texto(linea_limpia[0:3])
    numero = limpiar_texto(linea_limpia[3:11])
    obra_social = limpiar_texto(linea_limpia[15:21])
    tipo = limpiar_texto(linea_limpia[21:22])
    nombre_apellido = limpiar_texto(linea_limpia[22:])
    
    if not dni or not numero:
        return None
    
    # Corregimos el caracter especial de la Ñ si aparece
    nombre_apellido = nombre_apellido.replace('¥', 'Ñ')
    
    return [dni, numero, obra_social, tipo, nombre_apellido]

try:
    print("Iniciando procesamiento seguro...")
    contador = 0
    
    with open(input_file, 'r', encoding='latin-1', errors='ignore') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        # Escribimos el encabezado
        outfile.write("dni,numero,obraSocial,tipo,nombreapellido\n")
        
        for linea in infile:
            if not linea.strip():
                continue
            
            datos = procesar_linea(linea)
            if datos:
                dni, numero, obra_social, tipo, nombre_apellido = datos
                
                # Forzamos a que la última columna (nombre_apellido) vaya siempre 
                # entre comillas dobles. Así, si tiene comas internas (ej: HERNANDEZ, MARIA I.), 
                # PostgreSQL lo toma como un único bloque de texto sin tirar error.
                linea_formateada = f'{dni},{numero},{obra_social},{tipo},"{nombre_apellido}"\n'
                
                outfile.write(linea_formateada)
                contador += 1

    print(f"¡Listo! Se generó {output_file} con {contador} registros limpios.")

except FileNotFoundError:
    print("Error: No se encontró el archivo de entrada.")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")