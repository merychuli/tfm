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
def calculate_points(in_fc, out_fc, field, join_data, fields_tbd):
    arcpy.analysis.SpatialJoin(in_fc, join_data, out_fc, "JOIN_ONE_TO_ONE", "KEEP_ALL", None, "INTERSECT")
    arcpy.management.AddField(out_fc, field, "SHORT")
    arcpy.management.CalculateField(out_fc, field, "!Join_Count!")
    arcpy.management.DeleteField(out_fc, fields_tbd)


# ---- Parametros ----
gdb = arcpy.GetParameterAsText(0)

# ---- Constantes ----
transport_fds = os.path.join(gdb, "Transport")
turisticos = os.path.join(gdb, "Data", "POI_Turisticos")
carteristas = os.path.join(gdb, "Data", "GeoDatosCarteristas")

fields_poi = ['Nombre', 'Direccion', 'CP', 'Zona', 'Lat', 'Lon', 'Categoria', 'Subcategoria', 'Join_Count']
out_fc_list = []
# ---- Main ----
arcpy.AddMessage("---- INICIO ----")

walk = arcpy.da.Walk(transport_fds)
for dirpath, dirnames, filenames in walk:
    for filename in filenames:
        fc_path = os.path.join(dirpath, filename)
        out_fc_path = os.path.join(gdb, "Analysis", "{}_Buffer".format(filename))
        out_fc_list.append(out_fc_path)
        arcpy.analysis.Buffer(fc_path, out_fc_path, "500 Meters")

for fc in out_fc_list:
    fc_name = os.path.basename(fc).split("_")[0]
    out_fc = os.path.join(gdb, "Analysis", "{}Carteristas")
    calculate_points(fc, "temp", "POICount", turisticos, fields_poi)
    calculate_points("temp", out_fc, "CarteristasCount", carteristas, fields_cart)


arcpy.AddMessage("---- FIN ----")
