"""
Nombre:     Filtro para análisis de red

Objectivo:  Esta herramienta tiene el objetivo filtrar todas las FCs introducidas por el distrito 1, para posteriormente
            hacer un conteo de los elementos que se encuentran dentro de sus áreas de servicio

Output:     Network Dataset de la red creado y listo para configurar

Copyright:  © 2025 María Pedrote Sanz

"""
# ---- Modulos ----
import arcpy
import os

# ---- Parametros ----
list_fc = arcpy.GetParameter(0)
service_area = arcpy.GetParameterAsText(1)
# ---- Constantes ----
distritos = r"C:\TFM\TFM.gdb\Admin\DISTRITOS"
analysis_fds = r"C:\TFM\TFM.gdb\Analysis"
list_outputs = []
# ---- Main ----
arcpy.AddMessage("---- INICIO ----")

# Filtramos por el distrito 1
sel1 = arcpy.management.SelectLayerByAttribute(distritos, "NEW_SELECTION", "COD_DIS = '1'")
for fc in list_fc:
    name = os.path.basename(str(fc))
    output_fc = os.path.join(analysis_fds, "{}_Distrito1".format(name))
    arcpy.analysis.Clip(fc, sel1, output_fc)
    list_outputs.append(output_fc)

# Recorremos las FCs creadas
for output in list_outputs:
    # Añadimos un campo para almacenar la información
    arcpy.management.AddField(output, "InServiceArea", "SHORT", field_domain="BOL")
    arcpy.management.AddField(output, "InServiceAreaDistance", "SHORT")

    # Seleccionamos las entidades que se encuentran dentro del area y modificamos el campo creado con la información
    sel2 = arcpy.management.SelectLayerByLocation(output, "WITHIN", service_area, None, "NEW_SELECTION", "NOT_INVERT")
    arcpy.management.CalculateField(sel2, "InServiceArea", 1)

    sel3 = arcpy.management.SelectLayerByLocation(output, "WITHIN", service_area, None, "NEW_SELECTION", "INVERT")
    arcpy.management.CalculateField(sel3, "InServiceArea", 0)

    for dist in [100, 200, 500]:
        # Seleccionamos la distancia a evaluar
        sel_dist = arcpy.management.SelectLayerByAttribute(service_area, "NEW_SELECTION", "ToBreak = {}".format(dist))

        # Modificamos el campo con la distancia a la que están los puntos
        sel4 = arcpy.management.SelectLayerByLocation(output, "WITHIN", sel_dist, None, "NEW_SELECTION", "NOT_INVERT")
        arcpy.management.CalculateField(sel4, "InServiceAreaDistance", dist)

arcpy.AddMessage("---- FIN ----")
