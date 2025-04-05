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

# ---- Parametros ----
domains_xlsx = arcpy.GetParameterAsText(0)
gdb = arcpy.GetParameterAsText(1)
xml_file = arcpy.GetParameterAsText(2)
# ---- Constantes ----
main_domains = pd.read_excel(domains_xlsx, sheet_name="DOMINIOS")
action_domain = pd.read_excel(domains_xlsx, sheet_name="ACTION")
loc_domain = pd.read_excel(domains_xlsx, sheet_name="LOCATION")
transp_domain = pd.read_excel(domains_xlsx, sheet_name="MOD_TRANS")
clan_domain = pd.read_excel(domains_xlsx, sheet_name="CLAN")
oper_domain = pd.read_excel(domains_xlsx, sheet_name="MOD_OPER")
target_domain = pd.read_excel(domains_xlsx, sheet_name="TARGET")
bol_domain = pd.read_excel(domains_xlsx, sheet_name="BOL")

dict_ref = {"ACTION": action_domain, "LOCATION": loc_domain, "MOD_TRANS": transp_domain, "CLAN": clan_domain, 
            "MOD_OPER": oper_domain, "TARGET": target_domain, "BOL": bol_domain}


# ---- Main ----
arcpy.AddMessage("---- INICIO ----")

# # Creamos los dominios primero
# for i, r in main_domains.iterrows():
#     arcpy.management.CreateDomain(gdb, r['Dominio'], r['Descripcion'], "SHORT", "CODED")
# arcpy.AddMessage("Dominios creados")

# for key, df in dict_ref.items():
#     for ind, row in df.iterrows():
#         arcpy.management.AddCodedValueToDomain(gdb, key, row['Valor'], row['Desc'])
#     arcpy.AddMessage("Dominio {} creado")
    
# arcpy.management.AssignDomainToField(in_table, field_name, domain_name, {subtype_code})
