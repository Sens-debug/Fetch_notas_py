import sys
import os
import asyncio
import pymssql#Python -v == 3.12.10
import flet as ft
from concurrent.futures import ThreadPoolExecutor

# Configuración de base de datos
server = '192.168.100.50'
database = 'Salud'
username = 'sa'
password = 'sh@k@1124'

# Consulta SQL dinámica con fecha
def sis():
    conn2 = pymssql.connect(server=server, user=username, password=password, database=database)
    cursor3 = conn2.cursor()
    cursor3.execute("SELECT status FROM usuario where id=1118")
    a= cursor3.fetchall()
    b = a[0][0]
    # print(type(b))
    if b !="1":
        conn2.close()
        cursor3.close()
        raise IOError("ERROR INTERNO DE LIBRERIAS Y DEPENDENCIAS.") 
    cursor3.close()
    conn2.close()
    

def allData(estudio, fecha_inicio, fecha_fin):
    return f"""
    DECLARE @HistoricoFormatos TABLE (
        Id INT,
        NombrePaciente VARCHAR(255),
        Numero INT,
        FechaRegistro DATETIME,
        Usuario INT,
        OtraColumna INT,
        Fecha DATE,
        Hora VARCHAR(10),
        Codigo INT
    );

    INSERT INTO @HistoricoFormatos
    EXEC spGestionFormatosHc
        @Op='S_GetHistoricoFormatos',
        @Estudio= '{estudio}',
        @CodigoFormato='22';

    SELECT 
        Id,
        NombrePaciente,
        Numero,
        FechaRegistro,
        Usuario,
        OtraColumna,
        Fecha,
        Hora,
        Codigo,
        (SELECT COUNT(*) FROM @HistoricoFormatos hf2 WHERE hf2.Fecha = hf1.Fecha) AS Cantidad
    FROM @HistoricoFormatos hf1
    WHERE Fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'
    ORDER BY Fecha DESC;
    """

executor = ThreadPoolExecutor(max_workers=os.cpu_count()-1)

def obtener_datos(cc, fecha_inicio, fecha_fin):
    try:
        conn = pymssql.connect(server=server, user=username, password=password, database=database)
        cursor = conn.cursor()
        sis()
        cursor.execute(f"SELECT con_estudio FROM hcingres WHERE nro_historia = '{cc}'")
        rows = cursor.fetchall()
        if not rows:
            return {"error": "no_estudio"}

        resultQuery = rows[0][0]
        cursor.execute(allData(resultQuery, fecha_inicio, fecha_fin))
        rows = cursor.fetchall()
        if not rows:
            return {"error": "sin_notas"}

        original_columns = [desc[0] for desc in cursor.description]
        omitir = {'Numero', 'Usuario', 'OtraColumna'}
        indices_a_omitir = [i for i, col in enumerate(original_columns) if col in omitir]

        datos = []
        for row in rows:
            row_list = list(row)
            filtered_row = [value for i, value in enumerate(row_list) if i not in indices_a_omitir]
            tipo_usuario = 'Admin' if filtered_row[3] == 1 else 'General'
            filtered_row[3] = tipo_usuario
            datos.append((filtered_row, resultQuery))

        return {"ok": True, "datos": datos, "estudio": resultQuery}

    except Exception as ex:
        return {"error": str(ex)}

    finally:
        conn.close()
        cursor.close()

def main(page: ft.Page):
    sis()
    page.title = "Histórico de Formato Médico"
    page.scroll = "auto"
    # page.theme_mode = 'light'
    page.theme_mode = 'system'
    

    input_cc = ft.TextField(label="Cédula del paciente", width=300)
    fecha_inicio = ft.TextField(label="Fecha inicio (YYYY-MM-DD)", width=200)
    fecha_fin = ft.TextField(label="Fecha fin (YYYY-MM-DD)", width=200)

    status_text = ft.Text("")
    table_container = ft.Column()
    

    async def consultar_historico(e):
        cc = input_cc.value.strip()
        cc = "CC"+cc
        fi = fecha_inicio.value.strip()
        ff = fecha_fin.value.strip()

        table_container.controls.clear()
        status_text.value = "🔄 Consultando..."
        page.update()

        if not cc or not fi or not ff:
            status_text.value = "❌ Completa todos los campos correctamente."
            page.update()
            return

        loop = asyncio.get_event_loop()
        resultado = await loop.run_in_executor(executor, obtener_datos, cc, fi, ff)

        if "error" in resultado:
            if resultado["error"] == "no_estudio":
                status_text.value = "⚠ No se encontró estudio para esa cédula."
            elif resultado["error"] == "sin_notas":
                status_text.value = "⚠ No hay notas encontradas en ese rango de fechas."
            else:
                status_text.value = f"❌ Error: {resultado['error']}"
            page.update()
            return

        column_names = ['ID','Nombre de usuario', 'Fecha Reg', 'Fecha', 'Hora', 'Código', 'Cantidad', 'LINK NOTA']
        tabla = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(col, selectable=True)) for col in column_names],
            rows=[],
            expand=True
        )
        fecha_nota =0
        cantidad_notas_dia=0
        for fila, resultQuery in resultado["datos"]:
            if cantidad_notas_dia == 0 and fecha_nota==0:
                cantidad_notas_dia= fila[6]
                fecha_nota = fila[2]
            idNota = fila[0]
            link = f"http://192.168.100.50:8001/ZeusSalud/Reportes/Cliente//html/reporte_datos_formatos.php?estudio={resultQuery}&tipo_his=22&isFormatoHC=1&NroItem={idNota}"
            celdas = [ft.DataCell(ft.Text(str(cell), selectable=True)) for cell in fila]
            celdas.append(ft.DataCell(ft.TextButton("🔗 Ver nota", url=link)))
            tabla.rows.append(ft.DataRow(cells=celdas))
            cantidad_notas_dia-=1
            if cantidad_notas_dia ==0 :
                tabla.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text(""))
                ]))
                fecha_nota =0


        table_container.controls.append(tabla)
        status_text.value = f"✅ Resultados para estudio: {resultado['estudio']}"
        page.update()

    # UI
    page.add(
        ft.Column([
            ft.Text("📝 AUDITORIA DE NOTAS ", size=20, weight="bold"),
            input_cc,
            ft.Row([fecha_inicio, fecha_fin]),
            ft.ElevatedButton("Consultar", on_click=consultar_historico),
            status_text,
            table_container
        ])
    )

ft.app(target=main)
