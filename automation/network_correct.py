"""
Nombre:     Corrección de la red

Objectivo:  Esta herramienta tiene el objetivo de primeramaente filtrar la red para solo el distrito 1 posteriormente arreglar
            las intersecciones para que todas las calles se interconecten entre ellas

Output:     Network Dataset de la red creado y listo para configurar

Copyright:  © 2025 María Pedrote Sanz

"""
# ---- Modulos ----
import arcpy
import os

# ---- Parametros ----
network = arcpy.GetParameterAsText(0)
feature_ds = arcpy.GetParameterAsText(1)

# ---- Constantes ----
distritos_fc = r"C:\TFM\TFM.gdb\Admin\DISTRITOS"
output_fc = os.path.join(feature_ds, "OSM_Network1")
temp_network = os.path.join(feature_ds, "temp_network")
temp_points = os.path.join(feature_ds, "temp_points")

# ---- Main ----
arcpy.AddMessage("---- INICIO ----")

# Filtramos por el distrito centro y cortamos la capa de network
sel1 = arcpy.management.SelectLayerByAttribute(distritos_fc, "NEW_SELECTION", "COD_DIS = '1'")
arcpy.analysis.Clip(network, sel1, temp_network)

# Intersecamos la red consigo misma y obtenemos los puntos de intersección
arcpy.analysis.Intersect([temp_network, temp_network], temp_points, "ALL", None, "POINT")

# Dividimos la línea en los puntos
arcpy.management.SplitLineAtPoint(temp_network, temp_points, output_fc)

# Creamos el network dataset
arcpy.na.CreateNetworkDataset(feature_ds, "OSM_footwayNetwork1", "OSM_Network1", "NO_ELEVATION")

# Eliminamos los archivos temporales
arcpy.management.Delete([temp_network, temp_points])
arcpy.AddMessage("---- FIN ----")
