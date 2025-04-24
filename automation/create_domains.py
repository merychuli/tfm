"""
Nombre:     Creacion de dominios

Objectivo:  Esta herramienta busca crear los dominios necesarios para las Feature Classes de la GDB
            y los asigna automáticamente a los campos

Output:     La salida de esta herramienta es una GDB con todos los dominios modificados y las Feature
            Classes con sus dominios asignados y listo para usar

Copyright:  © 2025 María Pedrote Sanz

"""
# ---- Modulos ----
import arcpy
import pandas as pd
import os

# ---- Parametros ----
domains_xlsx = arcpy.GetParameterAsText(0)
gdb = arcpy.GetParameterAsText(1)

# ---- Constantes ----
main_domains = pd.read_excel(domains_xlsx, sheet_name="DOMINIOS")
action_domain = pd.read_excel(domains_xlsx, sheet_name="ACTION")
loc_domain = pd.read_excel(domains_xlsx, sheet_name="LOCATION")
transp_domain = pd.read_excel(domains_xlsx, sheet_name="MOD_TRANS")
clan_domain = pd.read_excel(domains_xlsx, sheet_name="CLAN")
oper_domain = pd.read_excel(domains_xlsx, sheet_name="MOD_OPER")
target_domain = pd.read_excel(domains_xlsx, sheet_name="TARGET")
bol_domain = pd.read_excel(domains_xlsx, sheet_name="BOL")
assign_domain = pd.read_excel(domains_xlsx, sheet_name="ASSIGN")

dict_ref = {"ACTION": action_domain, "LOCATION": loc_domain, "MOD_TRANS": transp_domain, "CLAN": clan_domain,
            "MOD_OPER": oper_domain, "TARGET": target_domain, "BOL": bol_domain}
fc_list = []

# ---- Main ----
arcpy.AddMessage("---- INICIO ----")

# # Creamos los dominios primero
# for i, r in main_domains.iterrows():
#     arcpy.management.CreateDomain(gdb, r['Dominio'], r['Descripcion'], "SHORT", "CODED")
# arcpy.AddMessage("Dominios creados")

# Creamos los valores de cada dominio
for key, df in dict_ref.items():
    for ind, row in df.iterrows():
        arcpy.management.AddCodedValueToDomain(gdb, key, row['Valor'], row['Desc'])
arcpy.AddMessage("Valores de dominios creados")

# Recorremos la GDB para tener todas la FCs
arcpy.env.workspace = gdb
datasets = arcpy.ListDatasets()
for dataset in datasets:
    fcs = arcpy.ListFeatureClasses(feature_dataset=dataset)
    for fc in fcs:
        fc_path = os.path.join(gdb, dataset, fc)
        fc_list.append(fc_path)
arcpy.AddMessage("List de FCs extraida")
arcpy.AddMessage(fc_list)
# Asignamos los dominios a sus campos correspondientes
for ind, row in assign_domain.iterrows():
    fc = [fc for fc in fc_list if row['FC'] in fc]
    if fc == []:
        arcpy.AddError("FC not found for row {}".format(row))
    else:
        arcpy.AddMessage(fc)
        fc = fc[0]
        fields = [field.name for field in arcpy.ListFields(fc)]
        arcpy.AddMessage(row["Campo"])
        arcpy.AddMessage(fields)
        arcpy.AddMessage(row["Dominio"])
        arcpy.management.AssignDomainToField(fc, row['Campo'], row['Dominio'])
arcpy.AddMessage("Dominios asignados a los campos")

arcpy.AddMessage("---- FIN ----")
