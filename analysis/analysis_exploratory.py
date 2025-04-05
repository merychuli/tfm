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
def calculate_points(in_fc, out_fc, field, cart_data):
    arcpy.analysis.SpatialJoin(in_fc, cart_data, out_fc, "JOIN_ONE_TO_ONE", "KEEP_ALL", None, "INTERSECT")
    arcpy.management.AddField(out_fc, field, "SHORT")
    arcpy.management.CalculateField(out_fc, field, "!Join_Count!")
    arcpy.management.DeleteField(out_fc, fields_tbd)


# ---- Parametros ----
gdb = arcpy.GetParameterAsText(0)

# ---- Constantes ----
dict_ubicacion = {1: 'CarteristasCountCalle', 2: 'CarteristasCountTransp'}
dict_clanes = {}
buffer_values = [100, 500, 1000]
distritos = os.path.join(gdb, "Admin", "DISTRITOS")
barrios = os.path.join(gdb, "Admin", "BARRIOS")
turisticos = os.path.join(gdb, "Data", "POI_Turisticos")
carteristas = os.path.join(gdb, "Data", "GeoDatosCarteristas")
output_distritos = os.path.join(gdb, "Analysis", "DistritosCarteristas")
output_barrios = os.path.join(gdb, "Analysis", "BarriosCarteristas")
output_turisticos = os.path.join(gdb, "Analysis", "TuristicosBuffer")
output_carteristas = os.path.join(gdb, "Analysis", "GeoDatosCarteristasCounts")
flag_analysis = False
fields_cart = ['Loc_name', 'Match_type', 'LongLabel', 'ShortLabel', 'Addr_type', 'Type', 'Place_addr',
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
fields_tbd = [field.name for field in arcpy.ListFields(carteristas)]
fields_tbd.remove('ObjectID')
fields_tbd.remove('Shape')
fields_tbd = fields_tbd + ['Join_Count']

# Creamos el dataset de analisis
arcpy.management.CreateFeatureDataset(gdb, "Analysis", 25830)

# Calculamos el numero de carteristas por barrio y distrito
calculate_points(distritos, "temp_distritos", "CarteristasCount", carteristas)
calculate_points(barrios, output_barrios, "CarteristasCount", carteristas)

# Calculamos el numero de carteristas según la ubicacion por barrio y distrito
# for fc in ["temp_distritos", output_barrios]:
sel = arcpy.management.SelectLayerByAttribute(carteristas, "NEW_SELECTION", "USER_Ubicacion = 1")
calculate_points("temp_distritos", "temp_distritos2", 'CarteristasCountCalle', sel)
arcpy.management.Delete("temp_distritos")

sel2 = arcpy.management.SelectLayerByAttribute(carteristas, "NEW_SELECTION", "USER_Ubicacion = 2")
calculate_points("temp_distritos2", output_distritos, 'CarteristasCountTransp', sel2)
arcpy.management.Delete("temp_distritos")
arcpy.management.Delete("temp_distritos2")

arcpy.management.DeleteField(output_distritos, ["TARGET_FID", "TARGET_FID_1", "TARGET_FID_12"])
# # Calculamos distancias desde los puntos de interes turisticos
# arcpy.analysis.MultipleRingBuffer(turisticos, output_turisticos, buffer_values, "Meters", "DistBuffer")

# # Calculamos los puntos de carteristas que estan a cada distancia
# for buffer in buffer_values:
#     sel1 = arcpy.management.SelectLayerByAttribute(output_turisticos, "NEW_SELECTION", "DistBuffer = {}".format(buffer))
#     if flag_analysis:
#         cart = output_carteristas
#     else:
#         cart = carteristas
#     sel2 = arcpy.management.SelectLayerByLocation(cart, "INTERSECT", sel1)
#     arcpy.management.CalculateField(sel2, "DistPOITuristico", buffer)
#     arcpy.conversion.ExportFeatures(sel2, output_carteristas)
#     flag_analysis = True

# # Calculamos los clanes en cada distrito
# for fc in [output_distritos, output_barrios]:
#     for key, value in dict_ubicacion.items():
#         arcpy.management.MakeFeatureLayer(fc, "temp_lyr")
#         arcpy.management.SelectLayerByAttribute("temp_lyr", "NEW_SELECTION", "Clan = {}".format(key))
#         calculate_points("temp_lyr", fc, value)
#         arcpy.management.Delete("temp_lyr")
arcpy.AddMessage("---- FIN ----")
