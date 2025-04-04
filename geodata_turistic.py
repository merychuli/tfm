"""
Nombre:     GeoDatos Carteristas

Objectivo:  Esta herramienta tiene el objetivo de iterar por toda la tabla de datos y asignar las direcciones a todos esos
            registros que proceden de transportes y tiene una parada asignada, con la dirección de la parada

Output:     La salida de esta herramienta son 2 CSV, uno con todos lo registros de la tabla a los que se les ha encontrado
            dirección, y otro CSV con los registros a los que no se les ha encontrado dirección

Copyright:  © 2025 María Pedrote Sanz

"""
# ---- Modulos ----
import pandas as pd
import xml.etree.ElementTree as ET
import xml.dom.minidom
import arcpy
import os

# ---- Parametros ----
xml_file = arcpy.GetParameterAsText(0)
output_fds = arcpy.GetParameterAsText(1)
output_folder = arcpy.GetParameterAsText(2)
# ---- Constantes ----
xml_pretty_file = os.path.join(os.path.dirname(xml_file), 'pretty.xml')
df = pd.DataFrame(columns=['Nombre', 'Direccion', 'CP', 'Zona', 'Lat', 'Lon', 'Categoria', 'Subcategoria'])
output_csv = os.path.join(output_folder, "DatosTuristicos.csv")
output_fc = os.path.join(output_fds, "POI_Turisticos")
temp_fc = os.path.join(output_fds, "temp_fc")
# ---- Main ----
arcpy.AddMessage("---- INICIO ----")

# Creamos un XML temporal con el archivo XML con tabulaciones
with open(xml_file, "r", encoding="utf-8") as f:
    xml_str = f.read()
xml_pretty = xml.dom.minidom.parseString(xml_str).toprettyxml(indent="  ")
with open(xml_pretty_file, "w", encoding="utf-8") as f:
    f.write(xml_pretty)
arcpy.AddMessage("XML optimizado creado")

# Cargamos el XML y guardamos los datos en un Dataframe
tree = ET.parse(xml_pretty_file)
root = tree.getroot()

for s in root.findall('service'):
    nombre = s.findtext('basicData/name', default='').strip()    
    geo = s.find('geoData')
    address = geo.findtext('address', default='').strip()
    zipcode = geo.findtext('zipcode', default='').strip()
    lat = geo.findtext('latitude', default='').strip()
    lon = geo.findtext('longitude', default='').strip()
    sub_area = geo.findtext('subAdministrativeArea', default='').strip()
    
    categoria = ''
    subcategoria = ''

    categorias_node = s.find('.//extradata/categorias')
    if categorias_node is not None:
        for cat in categorias_node.findall('categoria'):
            for item in cat.findall('item'):
                if item.attrib.get('name') == 'Categoria':
                    categoria = item.text.strip()
            for subcat in cat.findall('subcategorias/subcategoria'):
                for item in subcat.findall('item'):
                    if item.attrib.get('name') == 'SubCategoria':
                        subcategoria = item.text.strip()
    
    list_row = [nombre, address, zipcode, sub_area, lat, lon, categoria, subcategoria]
    df.loc[len(df)] = list_row

# Guardamos el dataframe
df.to_csv(output_csv, index=False)
arcpy.AddMessage("CSV creado")

# Transformamos la tabla a una feature class
arcpy.management.XYTableToPoint(output_csv, temp_fc, "Lon", "Lat", None, 4326)

# Pasamos al sistema de coordenadas del proyecto
arcpy.management.Project(temp_fc, output_fc, 25830)
arcpy.AddMessage("Feature Class creada y proyectada")

# Eliminamos archivos temporales
os.remove(xml_pretty_file)
arcpy.management.Delete(temp_fc)
arcpy.AddMessage("Archivos temporales eliminados")

arcpy.AddMessage("---- FIN ----")
