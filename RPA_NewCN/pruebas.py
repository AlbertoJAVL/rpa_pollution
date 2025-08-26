import re
plantillaCN  =r'''CASO: *TRANSFERENCIA*  \r AREA GENERA: "CALL CENTER"  \r DIVISION: "INBOUND Y SOCIAL MEDIA"  \r CATEGORIA: "SERVICIOS"  \r 
MOTIVO: "TRANSFERENCIA"  \r SUBMOTIVO: "SE TRANSFIRE LLAMADA"  \r SOLUCION: "TRANSFERENCIA AL AREA CORRESP"  \r TIPO: "INFORMATIVO"  \r COMENTARIO: (CN GENERADO POR AGENTE IA)'''
# 1) Normaliza separadores: si viene "\r" literal, vuélvelo salto de línea
texto = plantillaCN.replace('\\r', '\n')

# 2) Campos a extraer
campos = ['CATEGORIA', 'MOTIVO', 'SUBMOTIVO', 'SOLUCION','COMENTARIO']

# 3) Regex que captura el valor en 3 formatos: "entre comillas", (entre paréntesis), o suelto
#    - (?m) = modo multilínea
#    - (?=\n|$) = asegura que cortamos al final de la línea
patron_todos = r'''(?m)\b(CATEGORIA|MOTIVO|SUBMOTIVO|SOLUCION|COMENTARIO)\s*:\s*
                  (?:
                      "([^"]*)"           # grupo 2: valor entre comillas
                    | \(([^)]*)\)         # grupo 3: valor entre paréntesis
                    | \*?([^\n]+?)        # grupo 4: valor suelto (opcionalmente iniciado por *)
                  )
                  \s*(?=\n|$)'''

matches = re.findall(patron_todos, texto, flags=re.IGNORECASE | re.VERBOSE)

resultados = {c: '' for c in campos}
for nombre, g1, g2, g3 in matches:
    valor = (g1 or g2 or g3 or '').strip()
    resultados[nombre.upper()] = valor

# Mostrar resultados
for k in campos:
    print(f'{k}: {resultados[k]}')