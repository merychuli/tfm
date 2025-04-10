"""
Nombre:     Analisis de distritos y barrios

Objectivo:  Esta herramienta tiene el objetivo de crear FC de distritos y barrios con todos los resultados del análisis a través
            de la combinación de información de datos tanto por campos comunes como espacialmente.

Output:     El resultado de esta herramienta es una nueva FC en la GDB en el FDs de Admin con el Municipio y un nuevo FDs de
            Analysis con los datos de DistritosCarteristas y BarriosCarteristas con datos analizados

Copyright:  © 2025 María Pedrote Sanz

"""
# ---- Modulos ----
import arcpy
import os


# ---- Metodos ----
def calculate_points(in_fc, out_fc, field, join_data, fields_tbd):
    arcpy.analysis.SpatialJoin(in_fc, join_data, out_fc, "JOIN_ONE_TO_ONE", "KEEP_ALL", None, "INTERSECT")
    arcpy.management.AddField(out_fc, field, "SHORT")
    arcpy.management.CalculateField(out_fc, field, "!Join_Count!")
    arcpy.management.DeleteField(out_fc, fields_tbd)


# ---- Parametros ----
gdb = arcpy.GetParameterAsText(0)

# ---- Constantes ----
# Input FCs
municipio = os.path.join(gdb, "Admin", "MUNICIPIO")
distritos = os.path.join(gdb, "Admin", "DISTRITOS")
barrios = os.path.join(gdb, "Admin", "BARRIOS")
turisticos = os.path.join(gdb, "Data", "POI_Turisticos")
comisarias = os.path.join(gdb, "Data", "Comisarias")
carteristas = os.path.join(gdb, "Data", "GeoDatosCarteristas")

# Output FCs
output_distritos = os.path.join(gdb, "Analysis", "DistritosCarteristas")
output_barrios = os.path.join(gdb, "Analysis", "BarriosCarteristas")

# Fields
fields_cart = ['Status', 'Score', 'Match_addr', 'PlaceName', 'AddNumFrom', 'StDir', 'Region', 'Postal', 'X', 'Y', 'IN_SingleLine', 'USER_Clan', 'USER_Accion', 'USER_Ubicacion', 'USER_Calle', 'USER_Fecha', 'USER_Transporte', 'USER_Linea', 'USER_Parada', 'USER_ModusOperandi', 'USER_Cantidad', 'USER_Violencia', 'USER_ActuacionPolicial', 'USER_Target', 'USER_Referencia', 'Clan2']
fields_comisarias = ['NOMBRE', 'TRANSPORTE', 'ACCESIBILIDAD', 'COD_BARRIO', 'BARRIO', 'COD_DISTRITO', 'DISTRITO', 'COORDENADA_X', 'COORDENADA_Y', 'LATITUD', 'LONGITUD']
fields_poi = ['Nombre', 'Direccion', 'CP', 'Zona', 'Lat', 'Lon', 'Categoria', 'Subcategoria']
fields_tbd_join = []
field_output_tbd = fields_comisarias + fields_poi

# Other
dict_outputs = {"temp_distritos": output_distritos, "temp_barrios": output_barrios}
dict_clanes = {1: 'CountClanRumano', 2: 'CountClanBulgaro', 3: 'CountclanBosnio', 4: 'CountClanChileno', 5: 'CountClanPeruano'}

# ---- Main ----
arcpy.AddMessage("---- INICIO ----")


# Creamos el dataset de analisis
arcpy.management.CreateFeatureDataset(gdb, "Analysis", 25830)
arcpy.AddMessage("Dataset de Analisis creado")

# Creamos una FC del municipio de Madrid
arcpy.management.Dissolve(distritos, municipio)
arcpy.AddMessage("FC del municipio de Madrid creado")

# Calculamos el numero de carteristas por barrio y distrito
calculate_points(distritos, "temp_distritos", "CarteristasCount", carteristas, fields_cart)
calculate_points(barrios, "temp_barrios", "CarteristasCount", carteristas, fields_cart)
arcpy.AddMessage("Numero de carteristas calculado para distritos y barrios")

for temp_lyr, output_fc in dict_outputs.items():
    # Calculamos el numero de carteristas según la ubicacion por barrio y distrito
    sel = arcpy.management.SelectLayerByAttribute(carteristas, "NEW_SELECTION", "USER_Ubicacion = 1")
    calculate_points(temp_lyr, "temp_2", 'CarteristasCountCalle', sel, fields_cart)

    sel2 = arcpy.management.SelectLayerByAttribute(carteristas, "NEW_SELECTION", "USER_Ubicacion = 2")
    calculate_points("temp_2", "temp_transport", 'CarteristasCountTransp', sel2, fields_cart)

    arcpy.management.DeleteField("temp_transport", ["TARGET_FID", "TARGET_FID_1", "TARGET_FID_12"])
    arcpy.AddMessage("Numero de carteristas por Ubicacion calculado")

    # Eliminamos archivos temporales
    temp_files = [temp_lyr, "temp_2", sel, sel2]
    arcpy.management.Delete(temp_files)

    # Calculamos el número de datos de clanes en cada distrito y barrio
    for key, value in dict_clanes.items():
        sel3 = arcpy.management.SelectLayerByAttribute(carteristas, "NEW_SELECTION", "USER_Clan = {}".format(key))
        output = "temp_{}".format(key + 1)
        if key == 1:
            inp = "temp_transport"
        else:
            inp = "temp_{}".format(key)
        calculate_points(inp, output, value, sel3, fields_cart)
        arcpy.management.Delete(inp)
        arcpy.management.Delete(sel3)
    arcpy.AddMessage("Numero de carteristas por Clanes calculado")

    # Calculamos el numero de comisarias por distrito y barrio
    inp = "temp_6"
    calculate_points(inp, "temp_comisaria", 'ComisariasCount', comisarias, fields_comisarias)
    arcpy.AddMessage("Numero de Comisarias calculado")

    # Calculamos el numero de POI Turisticos por distrito y barrio
    inp = "temp_comisaria"
    calculate_points(inp, output_fc, 'POIsTuristicosCount', turisticos, fields_poi)
    # arcpy.management.DeleteField(output_fc, field_output_tbd)
    arcpy.AddMessage("Numero de POI Turisticos calculado")

    # Eliminamos archivos temporales
    temp_files2 = ["temp_5", "temp_comisaria"]
    arcpy.management.Delete(temp_files2)
    arcpy.AddMessage("Archivos temporales eliminados")

# Eliminamos campos innecesarios
for fc in [output_distritos, output_barrios]:
    for field in arcpy.ListFields(fc):
        if 'TARGET_FID' in field.name:
            fields_tbd_join.append(field.name)
    arcpy.management.DeleteField(fc, fields_tbd_join)
arcpy.AddMessage("Campos innecesarios eliminados")

arcpy.AddMessage("---- FIN ----")
