import csv
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.set_int_max_str_digits(100000)
csv.field_size_limit(sys.maxsize)

excel_input = 'enero-mayo-26.xlsx'
csv_input = 'puco_2026-5.csv'
excel_output = 'enero-mayo-26_procesado.xlsx'

# 1. Cargar el PUCO en un set para búsqueda rápida
print("Cargando archivo PUCO...")
dnis_puco = set()
with open(csv_input, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) > 1 and row[1].strip():
            dnis_puco.add(row[1].strip())

# 2. Leer cadenas compartidas del Excel
print("Leyendo cadenas compartidas del Excel...")
shared_strings = []
with zipfile.ZipFile(excel_input, 'r') as z:
    if 'xl/sharedStrings.xml' in z.namelist():
        with z.open('xl/sharedStrings.xml') as f_ss:
            for event, elem in ET.iterparse(f_ss, events=('end',)):
                if elem.tag.endswith('si'):
                    t = elem.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
                    shared_strings.append(t.text if t is not None else "")
                    elem.clear()

    sheet_path = 'xl/worksheets/sheet1.xml'
    
    # 3. Detectar la columna 'DNI Paciente' y la estructura máxima
    dni_col_letter = None
    max_col_num = 0
    
    with z.open(sheet_path) as f_sheet:
        for event, elem in ET.iterparse(f_sheet, events=('end',)):
            if elem.tag.endswith('row'):
                for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                    cell_type = c.get('t')
                    v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                    val = ""
                    if v is not None and v.text is not None:
                        val = shared_strings[int(v.text)] if cell_type == 's' else v.text
                    
                    cell_ref = c.get('r', '')
                    letters = ''.join([char for char in cell_ref if char.isalpha()])
                    
                    if val.strip() == 'DNI Paciente':
                        dni_col_letter = letters
                    
                    col_num = sum((ord(char) - 64) * (26 ** i) for i, char in enumerate(reversed(letters)))
                    if col_num > max_col_num:
                        max_col_num = col_num
                elem.clear()
                break

if not dni_col_letter:
    raise ValueError("No se encontró la columna 'DNI Paciente' en el archivo Excel.")

def num_to_col_letter(num):
    letter = ''
    while num > 0:
        num, remainder = divmod(num - 1, 26)
        letter = chr(65 + remainder) + letter
    return letter

nueva_col_num = max_col_num + 1
nueva_col_letter = num_to_col_letter(nueva_col_num)

# 4. Procesar y modificar las filas mediante streaming y archivo temporal XML
print("Cruzando datos y generando nuevo Excel...")
ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
temp_xml = 'temp_sheet.xml'

with zipfile.ZipFile(excel_input, 'r') as zin:
    with zin.open(sheet_path) as f_in, open(temp_xml, 'w', encoding='utf-8') as f_out:
        f_out.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        
        is_first_row = True
        context = ET.iterparse(f_in, events=('start', 'end'))
        
        for event, elem in context:
            if event == 'end' and elem.tag == f'{{{ns}}}row':
                r_idx = ''.join([char for char in elem.get('r', '1') if char.isdigit()])
                
                if is_first_row:
                    new_c_head = ET.SubElement(elem, f'{{{ns}}}c')
                    new_c_head.set('r', f'{nueva_col_letter}1')
                    new_c_head.set('t', 'inlineStr')
                    is_h = ET.SubElement(new_c_head, f'{{{ns}}}is')
                    t_h = ET.SubElement(is_h, f'{{{ns}}}t')
                    t_h.text = 'obra social'
                    is_first_row = False
                else:
                    dni_val = None
                    for c in elem.findall(f'{{{ns}}}c'):
                        c_ref = c.get('r', '')
                        if c_ref.startswith(dni_col_letter):
                            cell_type = c.get('t')
                            v = c.find(f'{{{ns}}}v')
                            if v is not None and v.text is not None:
                                dni_val = shared_strings[int(v.text)] if cell_type == 's' else v.text
                            break
                    
                    resultado = 'OS' if (dni_val and str(dni_val).strip() in dnis_puco) else 'CPE'
                    
                    new_c = ET.SubElement(elem, f'{{{ns}}}c')
                    new_c.set('r', f'{nueva_col_letter}{r_idx}')
                    new_c.set('t', 'inlineStr')
                    is_elem = ET.SubElement(new_c, f'{{{ns}}}is')
                    t_elem = ET.SubElement(is_elem, f'{{{ns}}}t')
                    t_elem.text = resultado
                
                f_out.write(ET.tostring(elem, encoding='utf-8').decode('utf-8'))
                elem.clear()

# 5. Reconstruir el archivo .xlsx final
with zipfile.ZipFile(excel_input, 'r') as zin:
    with zipfile.ZipFile(excel_output, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == sheet_path:
                zout.write(temp_xml, item.filename)
            else:
                zout.writestr(item, zin.read(item.filename))

print(f"¡Listo! Archivo generado con éxito: '{excel_output}'.")