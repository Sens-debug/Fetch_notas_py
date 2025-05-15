*-PLANTEMIENTO DEL PROBLEMA*
    Proyecto orientado a optimizar procesos dentro de una empresa real, con programacion afín a un sistema "SaaS".
    La compañia legalmente constituida que fue objetivo de la optimizacion, dispone de un Sistema Web hosteado de forma local, el cual les sirve para su gestion Financiera y Asistencial
    El objetivo del programa era hacer un fetch a una Base de datos preexistente, la cual utilizaba "StoredProcedures" para sus consultas web
    La base de datos del Sistema Web fue contruida en SQL Server con SQLServerManager

-*PRIMEROS PASOS*
    -Para empezar el proyecto vimos la necesidad del usuario en mejorar su forma de auditar las notas de los auxiliares de enfermeria,
    posterior a eso se empleo la herramienta "SQLProfiler" para interceptar las consultas que realizaba la Web durante su ejecucion.

    -Se filtraron las consultas para encontrar la necesaria, esto debido a que no fueron planas sino StoredProcedures con variables, tablas secundarias,etc.

    -Una vez con el conocimiento de la consulta adecuada empezamos la prueba en la Query de SQLServerManager para explorar, comporbar y verificar la Query y su contenido.

    -Posterior a la finalizacion del "Filtro" con la Query (¿Que traia? ¿Que podría traer? así como el ¿De que forma podría 'adaptarse'?).
    *INICIAMOS CON LAS BASES DEL PROYECTO*

    -Construimos un Aplicativo con despliegue por consola->Todo con el afán de comprobar conexion y retorno de los Fetch.
    *UNA VEZ CONSTRUIDA LA CONEXION, EMPIEZA LA INTERFAZ*

-*GUI*
    -Elegimos Flet debido a su estetica y potencial para la tarea.
        Usamos campos "Entry" para almacenar la cc del paciente, la cual con una consulta obtiene su #Estudio, para a tráves del estudio traer sus notas.
        Tambien otros 2 campos "Entry" para Establecer los rangos de fecha bajo los cuales la consulta principal podrá retornar el Array de Tuplas que contiene los datos.

        El contenedor de los datos es una DataTable de Flet, la cual se ajusta dinamicamente a los resultados de las consultas

*-LA FUNCION SaaS*
    La funcion Saas se basa en un Early Raise IOException, que se activa si el estado de un usuario es Diferente a "Activo", lo cual imposibilita su ejecucion

*-COMPILACION*
    Se ofusca el programa con "pyarmor", para despues compilar con "pyinstaller" -> Sentencias por consola ---->  
    
    1.  Se usó "venv" para el manejo de pendencias, y "pip freeze > requerimientos.txt" para establecer las usadas, así como sus versiones
    2.  pyarmor gen app.py   
    3.  pyinstaller --onefile --hidden-import asyncio --hidden-import os --hidden-import sys --hidden-import pymssql --hidden-import flet --hidden-import ThreadPoolExecutor --noconsole dist/app.py
            Debido a la ofuscacion hay que usar el "--hidden-impor" para importar todas las dependencias del Proyecto

*EJECUCION .EXE*
    El archivo app.exe se encuentra en la ruta /dist/app.exe -> El app.py que se encuentra en esta misma ruta es el archivo ofuscado por pyarmor

    Debido que la compilacion fue --onefile no se necesita nada mas que el unico .exe
