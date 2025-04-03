"""
Nombre:     Procesamiento de transporte

Objetivo:   Esta herramienta tiene el objectivo de procesar los datos de transporte del Consorcio Regional de Transportes y eliminar
            datos innecesarios además de añadir los datos de afluencia. También se añadirán al mapa y se simbolizará cada línea
            en base a sus colores oficiales

Output:     Las capas de los 3 transportes (Metro, EMT y Cercanias) tanto lineas como estaciones añadidas al mapa con su simbologia
            oficial y con sus datos necesarios para analisis

Copyright:  © 2025 María Pedrote Sanz

"""

# ---- Modulos ----
import arcpy
import pandas as pd
import glob
import os

# ---- Parametros ----
data_folder = arcpy.GetParameterAsText(0)
output_dataset = arcpy.GetParameterAsText(1)
csv_symbology = arcpy.GetParameterAsText(2)
xlsx_carteristas = arcpy.GetParameterAsText(3)
csv_afluencia_renfe = arcpy.GetParameterAsText(4)
csv_afluencia_metro = arcpy.GetParameterAsText(5)

# ---- Constantes ----
estaciones_fields = ['IDESTACION', 'FECHAACTUA', 'MODO', 'OBSERVACIO', 'SITUACION', 'CODIGOEMPR', 'DENOMINA_1', 'MODOINTERC', 'CODIGOINTE', 'TIPO', 'CODIGOPROV', 'CODIGOMUNI', 'CODIGOENTI', 'CODIGONUCL', 'CODIGOVIA', 'TIPOVIA', 'PARTICULA', 'NOMBREVIA', 'TIPONUMERO', 'NUMEROPORT', 'CALIFICADO', 'CARRETERA', 'CODIGOPOST', 'SECCIONCEN', 'TESELA', 'SECTORURBA', 'SECTOR', 'CORREDOR', 'CORONATARI', 'CORONA123', 'ZONATRANSP', 'ENCUESTADO', 'ENCUESTAAF', 'HOJA25000', 'ACONDICION', 'ACONDICI_1', 'FECHAALTA', 'FECHAINICI', 'FECHAFIN', 'X', 'Y', 'SITUACIONC', 'DENOMINA_2', 'INTERURBAN', 'INTERURB_1', 'LINEAS']
tramos_fields = ['IDTRAMO', 'FECHAACTUA', 'MODO', 'CODIGOITIN', 'SENTIDO', 'CODIGOPOST', 'CODIGOANDE', 'CODIGOPROV', 'CODIGOMUNI', 'MUNICIPIO', 'CORONATARI', 'DIRECCION', 'FECHAALTA', 'FECHAINICI', 'FECHAFIN', 'LONGITUDTR', 'VELOCIDADT', 'MODOINTERC', 'CODIGOINTE', 'CODPROV_LI', 'CODMUN_LIN', 'IDFTRAMO', 'CODIGOOBSE', 'CODIGOSUBL', 'DENOMINA_1', 'IDFLINEA']
df_symbology = pd.read_excel(csv_symbology)
afluencia_renfe = pd.read_csv(csv_afluencia_renfe)
afluencia_metro = pd.read_csv(csv_afluencia_metro)
df_carteristas = pd.read_excel(xlsx_carteristas)
dict_join = {'1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6-1': '6', '6-2': '6', '7a': '7', '7b': '7',
             '8': '8', '9A': '9', '9B': '9', '10a': '10', '10b': '10', '11': '11', '12-1': '12', '12-2': '12', 'R': 'R'}

# ---- Main ----
arcpy.AddMessage("---- INICIO ----")

# Listar los SHP en la carpeta de datos
shp_list = glob.glob(data_folder + "\**\*.shp", recursive=True)

# Exportar los datos de los SHP al dataset ademas de renombrarlos
for shp in shp_list:
    input_name = os.path.basename(shp)
    if 'M4' in input_name:
        output_name = input_name.replace("M4", "Metro").split(".")[0]
    elif 'M5' in shp:
        output_name = input_name.replace("M5", 'Cercanias').split(".")[0]
    elif 'M6' in shp:
        output_name = input_name.replace("M6", "EMT").split(".")[0]
    out_path = os.path.join(output_dataset, output_name)
    if 'Estaciones' in output_name:
        arcpy.conversion.ExportFeatures(shp, out_path)
    else:
        # Para las lineas de metro se hace un proceso específico
        if 'Metro' in output_name:
            # Se añade un campo linea donde se almacenara el numero de linea sin tener en cuenta el sentido
            arcpy.management.AddField(shp, "Linea", "TEXT")
            with arcpy.da.UpdateCursor(shp, ["NUMEROLINE", "Linea"]) as cursor0:
                for row0 in cursor0:
                    for clave in dict_join.keys():
                        if clave == row0[0]:
                            row0[1] = dict_join[clave]
                            cursor0.updateRow(row0)
                            break        
            # Disolvemos y exportamos a la GDB en base al campo creado
            arcpy.management.Dissolve(shp, out_path, ['Linea'])

            # Añadimos los datos de afluencia de metro segun el campo linea
            arcpy.management.AddJoin(out_path, "Linea", csv_afluencia_metro, "Linea")

        else:
            # Disolvemos en base al campo NUMEROLINE
            arcpy.management.Dissolve(shp, out_path, ['NUMEROLINE'])
arcpy.AddMessage("Datos de tranporte exportados al FDs")

# Iterar por el Dataset donde estan los datos
walk = arcpy.da.Walk(output_dataset)
for dirpath, dirnames, filenames in walk:
    for filename in filenames:
        fc_path = os.path.join(dirpath, filename)

        # Añadir el campo CarteristasCount
        arcpy.management.AddField(fc_path, "CarteristasCount", "SHORT")

        # Crear SQL para filtrar en base a tipo de tranposrte
        if 'EMT' in filename:
            transp = 1
        elif 'Metro' in filename:
            transp = 2
        elif 'Cercanias' in filename:
            transp = 3

        # Para las estaciones solo
        if 'Estaciones' in filename:

            # Eliminar campos innecesarios
            arcpy.management.DeleteField(fc_path, estaciones_fields)

            # Establecemos los campos a usar
            if transp == 1:
                fields1 = ["CarteristasCount", "CODIGOESTA"]
            else:
                fields1 = ["CarteristasCount", "CODIGOCTME"]
            arcpy.AddMessage(fc_path)
            # Actualizar la tabla en el campo Carteristas count, en base al número de datos de carteristas
            with arcpy.da.UpdateCursor(fc_path, fields1) as cursor1:
                for row1 in cursor1:
                    filtered_df = df_carteristas[(df_carteristas['Parada'] == "{}".format(row1[1])) & (df_carteristas['Transporte'] == transp)]
                    if not filtered_df.empty:
                        num_rows = len(filtered_df)
                        row1[0] = num_rows
                    else:
                        row1[0] = 0
                    cursor1.updateRow(row1)
            if transp == 3:
                # Añadimos los datos de afluencia de las estaciones de renfe
                arcpy.management.AddJoin(fc_path, "CODIGOCTME", afluencia_renfe, "Parada")

        else:
            # Eliminamos campos innecesarios
            arcpy.management.DeleteField(fc_path, tramos_fields)

            # Definimos los campos a considerar
            if transp == 2:
                fields2 = ['CarteristasCount', "Linea"]
            else:
                fields2 = ['CarteristasCount', "NUMEROLINE"]

            # Actualizar los datos del campo CarteristasCount
            with arcpy.da.UpdateCursor(fc_path, fields2) as cursor2:
                for row2 in cursor2:
                    filtered_df = df_carteristas[(df_carteristas['Linea'] == "{}".format(row2[1])) & (df_carteristas['Transporte'] == transp)]
                    if not filtered_df.empty:
                        num_rows = len(filtered_df)
                        row2[0] = num_rows
                    else:
                        row2[0] = 0
                    cursor2.updateRow(row2)

aprx = arcpy.mp.ArcGISProject("CURRENT")
m = aprx.activeMap

# Agregar la capa al mapa
metro_lineas = os.path.join(output_dataset, "Metro_Tramos")
cercanias_lineas = os.path.join(output_dataset, "Cercanias_Tramos")

for fc in [metro_lineas, cercanias_lineas]:
    lyr = m.addDataFromPath(fc)
    sym = lyr.symbology

    if "Metro" in fc:
        df_transporte = df_symbology[df_symbology['TipoTransporte'] == 2]
        field = ['Linea']
    else:
        df_transporte = df_symbology[df_symbology['TipoTransporte'] == 3]
        field = ['NUMEROLINE']

    colores = df_transporte.set_index("Linea").T.to_dict("list")

    # Asignamos la simbologia
    if hasattr(sym, "renderer"):
        sym.updateRenderer("UniqueValueRenderer")
        sym.renderer.fields = field

        # Asignar colores a cada categoría
        for group in sym.renderer.groups:
            for item in group.items:
                valor = item.values[0]
                if valor in colores:
                    item.symbol.color = {"RGB": colores[valor]}

        # Aplicar los cambios a la capa
        lyr.symbology = sym
arcpy.AddMessage("---- FIN ----")
