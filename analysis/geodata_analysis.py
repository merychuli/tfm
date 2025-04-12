"""
Nombre:     Creacion de analisis

Objectivo:
Output:
Copyright:  © 2025 María Pedrote Sanz

"""
# ---- Modulos ----
import arcpy
import os

# ---- Metodos ----

# ---- Parametros ----
gdb = arcpy.GetParameterAsText(0)

# ---- Constantes ----
turisticos = os.path.join(gdb, "Data", "POI_Turisticos")
carteristas = os.path.join(gdb, "Data", "GeoDatosCarteristas")

output_turisticos = os.path.join(gdb, "Analysis", "TuristicosBuffer")
output_carteristas = os.path.join(gdb, "Analysis", "GeoDatosCarteristasCounts")


dict_buffer = {100: "DistPOITuristicos_100", 500: "DistPOITuristicos_500", 1000: "DistPOITuristicos_1000"}
buffer_values = list(dict_buffer.keys())
fields_tbm = []
field_names = ["Linea", "Referencia"]

fields_cart = ['Status', 'Score', 'PlaceName', 'AddNumFrom', 'StDir', 'Region', 'Loc_name', 'Match_type', 'LongLabel', 
               'ShortLabel', 'Addr_type', 'Type', 'Place_addr',
               'Phone', 'Rank', 'AddBldg', 'AddNum', 'AddNumFronm', 'AddNumTo', 'AddRange', 'Side',
               'StPreDir', 'StPreType', 'StName', 'StType', 'BldgType', 'BldgName', 'LevelType',
               'LevelName', 'UnitType', 'UnitName', 'SubAddr', 'StAddr', 'Block', 'Sector', 'Nbrhd',
               'District', 'City', 'MetroArea', 'Subregion', 'RegionAbbr', 'Territory', 'Zone',
               'PostalExt', 'Country', 'CntryName', 'LangCode', 'Distance', 'DisplayX', 'DisplayY',
               'Xmin', 'Xmax', 'Ymin', 'Ymax', 'URL', 'ExInfo', 'StrucDet', 'StrucType']

# ---- Main ----
arcpy.AddMessage("---- INICIO ----")

# Limpiamos la capa de GeoDatosCarteristas de campos
arcpy.management.DeleteField(carteristas, fields_cart)

# Calculamos distancias desde los puntos de interes turisticos
arcpy.analysis.MultipleRingBuffer(turisticos, output_turisticos, buffer_values, "Meters", "DistBuffer")
arcpy.AddMessage("Buffer de puntos turisticos hecho")

# Calculamos los puntos de carteristas que estan a cada distancia
for buffer, field in dict_buffer.items():
    sel1 = arcpy.management.SelectLayerByAttribute(output_turisticos, "NEW_SELECTION", "DistBuffer = {}".format(buffer))
    sel2 = arcpy.management.SelectLayerByLocation(carteristas, "INTERSECT", sel1)
    arcpy.management.CalculateField(sel2, field, buffer)

arcpy.AddMessage("---- FIN ----")
