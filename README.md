# 📋 Descripción del Script de Parsing (`parsing.py`)

Este script en **Python** 🐍 está diseñado para procesar, limpiar y transformar un archivo de texto plano mal formateado del padrón PUCO (`.txt`) en un archivo estructurado y limpio en formato **`.csv`**, listo para ser importado de forma segura en una base de datos PostgreSQL 🗄️.

### ⚙️ ¿Qué hace paso a paso?

1. **Lectura y Codificación segura (`latin-1`)**: Abre el archivo de entrada (`puco_2026-05.txt`) ignorando errores de codificación comunes para evitar que el programa se rompa por caracteres extraños. 📄
2. **Extracción por posiciones fijas (`procesar_linea`)**: Analiza cada renglón del texto plano cortándolo por rangos de caracteres específicos para separar los campos clave:
   - **`dni`**: Del carácter 0 al 3. 🆔
   - **`numero`**: Del carácter 3 al 11. 🔢
   - **`obra_social`**: Del carácter 15 al 21. 🏥
   - **`tipo`**: Del carácter 21 al 22. 🏷️
   - **`nombre_apellido`**: Del carácter 22 en adelante. 👤
3. **Limpieza y Corrección de Errores**:
   - Remueve espacios vacíos y comillas dobles internas que puedan romper el formato de columnas. 🧹
   - Corrige automáticamente errores tipográficos del sistema (como reemplazar el carácter especial `¥` por la letra `Ñ`). 🔤
4. **Exportación Estructurada (`.csv`)**: 
   - Escribe un encabezado estándar (`dni,numero,obraSocial,tipo,nombreapellido`). 📝
   - Envuelve el campo de **nombre y apellido** entre comillas dobles para evitar conflictos con comas internas (por ejemplo: `HERNANDEZ, MARIA I.`), asegurando que PostgreSQL lo interprete como un único bloque de texto sin arrojar errores de importación. 📊
5. **Control de Excepciones y Conteo**: Muestra en consola el progreso y la cantidad total de registros procesados con éxito de forma limpia. 📈
