"""
Nombre:     GeoDatos Carteristas

Objectivo:  Esta herramienta tiene el objetivo de iterar por toda la tabla de datos y asignar las direcciones a todos esos
            registros que proceden de transportes y tiene una parada asignada, con la dirección de la parada

Output:     La salida de esta herramienta son 2 CSV, uno con todos lo registros de la tabla a los que se les ha encontrado
            dirección, y otro CSV con los registros a los que no se les ha encontrado dirección

Copyright:  © 2025 María Pedrote Sanz

"""
# ---- Modulos ----
import arcpy
import pandas as pd
import os

# ---- Parametros ----
data = arcpy.GetParameterAsText(0)
output_folder = arcpy.GetParameterAsText(1)

# ---- Constantes ----
table = os.path.join(output_folder, "GeoData.csv")
table2 = os.path.join(output_folder, "NonGeoData.csv")
estaciones_metro = r"D:\TFM\Datos\Transporte\M4_Estaciones\M4_Estaciones.shp"
estaciones_emt = r"D:\TFM\Datos\Transporte\M6_Estaciones\M6_Estaciones.shp"
estaciones_cercanias = r"D:\TFM\Datos\Transporte\M5_Estaciones\M5_Estaciones.shp"

# ---- Main ----
arcpy.AddMessage("---- INICIO ----")
# Modificar la tabla de carteristas con las direcciones de las paradas si las tenemos
df = pd.read_excel(data)

for ind, row in df.iterrows():
    if row['Ubicacion'] == 2 and pd.notna(row['Parada']):
        if row['Transporte'] == 1:
            capa = estaciones_emt
            sql_clause = "CODIGOESTA = '{}'".format(int(row['Parada']))
        elif row['Transporte'] == 2:
            capa = estaciones_metro
            sql_clause = "CODIGOCTME = '{}'".format(int(row['Parada']))

        elif row["Transporte"] == 3:
            capa = estaciones_cercanias
            sql_clause = "CODIGOCTME = '{}'".format(int(row['Parada']))

        datos_est = [row for row in arcpy.da.SearchCursor(capa, ['TIPOVIA', 'PARTICULA', 'NOMBREVIA', 'NUMEROPORT'], sql_clause)]
        if datos_est == []:
            arcpy.AddWarning("Dirección no encontrada para este registro: {}".format(row))
        else:
            direccion = "{} {} {} {}, Madrid".format(datos_est[0][0], datos_est[0][1], datos_est[0][2], datos_est[0][3])
            df.loc[ind, 'Calle'] = direccion

df_dir = df[df['Calle'].notna()]
df_dir.to_csv(table, index=False)
arcpy.AddMessage("CSV con datos geográficos exportada en {}".format(table))

df_no_dir = df[df['Calle'].isna()]
df_no_dir.to_csv(table2, index=False)
arcpy.AddMessage("CSV sin datos geográficos exportada en {}".format(table2))

arcpy.AddMessage("---- FIN ----")
