import os
import tkinter as tk

import numpy as np
import tkcalendar as tc
from tkinter import messagebox
import pandas as pd
import sqlalchemy as sa
import datetime
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from keplergl import KeplerGl
import geopandas as gpd
from shapely.geometry import Point, LineString
from dotenv import load_dotenv

load_dotenv()

# read the GeoJSON file
gdf = gpd.read_file(f"{os.getenv('geojson_route')}/shapefile.shp")
gdf = gdf.sort_values(['DPA_DESPRO', 'DPA_DESCAN', 'DPA_DESPAR'])
d_options = gdf.loc[:, ['DPA_DESPRO', 'DPA_DESCAN', 'DPA_DESPAR']].reset_index(drop=True)


class SammApp(tk.Frame):
    """Create the tkinter application class"""

    def __init__(self, master=None):
        """This is a constructor method for a class in Python. It initializes the object's internal state and is
        automatically called when an object is created."""

        # Use the built-in constructor method of the tkinter module in Python. The super() function is used to call the
        # constructor of the parent class of the current class, and __init__() is the method that is called when creating
        # a new instance of the class. In this case, master is the parameter being passed to the constructor method, which
        # is the main window object that's being created. This line of code is used to initialize an instance of a tkinter
        # widget or frame.
        super().__init__(master)

        # Initialize all the variables
        self.master = master
        self.master.title("Reportes SAMM")
        self.master.geometry("800x450")
        self.list_of_czo = ["Nacional", "CZO2", "CZO3", "CZO4", "CZO5", "CZO6"]
        self.list_of_provincia = d_options['DPA_DESPRO'].unique().tolist()
        self.provincia = tk.StringVar()
        self.repgen = tk.BooleanVar()
        self.mapa = tk.BooleanVar()
        self.mapaparroquia = tk.BooleanVar()
        self.operadora1 = tk.BooleanVar()
        self.operadora2 = tk.BooleanVar()
        self.operadora3 = tk.BooleanVar()
        self.technology1 = tk.BooleanVar()
        self.technology2 = tk.BooleanVar()
        self.sessiontype1 = tk.BooleanVar()
        self.sessiontype2 = tk.BooleanVar()
        self.sessiontype3 = tk.BooleanVar()
        self.sessiontype4 = tk.BooleanVar()
        self.czo = tk.StringVar()
        self.czo.set("Nacional")
        self.canton = tk.StringVar()
        self.parroquia = tk.StringVar()
        # Bind update_options to provincia and canton
        self.provincia.trace('w', self.update_options)
        self.canton.trace('w', self.update_options)
        self.create_widgets()
        self.program_is_running = False

    def update_options(self, *args):
        self.list_of_canton = d_options[d_options['DPA_DESPRO'] == self.provincia.get()]['DPA_DESCAN'].unique().tolist()
        self.option_menu2['menu'].delete(0, 'end')
        if self.list_of_canton:
            for canton in self.list_of_canton:
                self.option_menu2['menu'].add_command(label=canton, command=tk._setit(self.canton, canton))
            if self.canton.get() not in self.list_of_canton:
                self.canton.set(self.list_of_canton[0])
        else:
            self.canton.set("Escoja un Cantón")
            self.parroquia.set("Escoja una Parroquia")
            self.option_menu3['menu'].delete(0, 'end')
            return

        self.list_of_parroquia = \
            d_options[
                (d_options['DPA_DESPRO'] == self.provincia.get()) & (d_options['DPA_DESCAN'] == self.canton.get())][
                'DPA_DESPAR'].unique().tolist()
        self.option_menu3['menu'].delete(0, 'end')
        if self.list_of_parroquia:
            for parroquia in self.list_of_parroquia:
                self.option_menu3['menu'].add_command(label=parroquia, command=tk._setit(self.parroquia, parroquia))
            if self.parroquia.get() not in self.list_of_parroquia:
                self.parroquia.set(self.list_of_parroquia[0])
        else:
            self.parroquia.set("Escoja una Parroquia")

    def create_widgets(self):
        """Create the widges to be used with tkinter and tkcalendar"""

        self.button0 = tk.Checkbutton(self.master, text="Reporte General.", variable=self.repgen,
                                      command=lambda: self.toggle_button0_state())
        self.button0.grid(row=0, column=0, sticky=tk.W, padx=30, pady=5)

        self.button1 = tk.Checkbutton(self.master, text="Mapa General.", variable=self.mapa,
                                      command=lambda: self.toggle_button1_state())
        self.button1.grid(row=0, column=0, sticky=tk.W, padx=150, pady=5)

        self.button2 = tk.Checkbutton(self.master, text="Mapa Parroquial.", variable=self.mapaparroquia,
                                      command=lambda: self.toggle_button2_state())
        self.button2.grid(row=0, column=0, sticky=tk.W, padx=270, pady=5)

        self.lbl_1 = tk.Label(self.master, text="Operadora:", width=20, font=("bold", 11))
        self.lbl_1.grid(row=1, column=0, sticky=tk.W, padx=13)

        self.button3 = tk.Checkbutton(self.master, text="Claro", variable=self.operadora1)
        self.button3.grid(row=1, column=0, sticky=tk.W, padx=145)

        self.button4 = tk.Checkbutton(self.master, text="CNT", variable=self.operadora2)
        self.button4.grid(row=1, column=0, sticky=tk.W, padx=260)

        self.button5 = tk.Checkbutton(self.master, text="Movistar", variable=self.operadora3)
        self.button5.grid(row=1, column=0, sticky=tk.W, padx=375)

        self.lbl_2 = tk.Label(self.master, text="Tecnología:", width=20, font=("bold", 11))
        self.lbl_2.grid(row=2, column=0, sticky=tk.W, padx=12)

        self.button6 = tk.Checkbutton(self.master, text="WCDMA", variable=self.technology1)
        self.button6.grid(row=2, column=0, sticky=tk.W, padx=145)

        self.button7 = tk.Checkbutton(self.master, text="LTE", variable=self.technology2)
        self.button7.grid(row=2, column=0, sticky=tk.W, padx=260)

        self.lbl_3 = tk.Label(self.master, text="Tipo de Sesión:", width=20, font=("bold", 11))
        self.lbl_3.grid(row=3, column=0, sticky=tk.W)

        self.button8 = tk.Checkbutton(self.master, text="HTTP Download", variable=self.sessiontype1)
        self.button8.grid(row=3, column=0, sticky=tk.W, padx=145)

        self.button9 = tk.Checkbutton(self.master, text="HTTP Post", variable=self.sessiontype2)
        self.button9.grid(row=3, column=0, sticky=tk.W, padx=260)

        self.button10 = tk.Checkbutton(self.master, text="FTP Download", variable=self.sessiontype3)
        self.button10.grid(row=3, column=0, sticky=tk.W, padx=375)

        self.button11 = tk.Checkbutton(self.master, text="FTP Post", variable=self.sessiontype4)
        self.button11.grid(row=3, column=0, sticky=tk.W, padx=490)

        self.lbl_4 = tk.Label(self.master, text="CZO:", width=20, font=("bold", 11))
        self.lbl_4.grid(row=4, column=0, sticky=tk.W, padx=32)

        self.option_menu0 = tk.OptionMenu(self.master, self.czo, *self.list_of_czo)
        self.option_menu0.grid(row=4, column=0, sticky=tk.W, padx=145)

        self.lbl_5 = tk.Label(self.master, text="Provincia:", width=20, font=("bold", 11))
        self.lbl_5.grid(row=5, column=0, sticky=tk.W, padx=14)

        self.option_menu1 = tk.OptionMenu(self.master, self.provincia, *self.list_of_provincia,
                                          command=self.update_options)
        self.option_menu1.grid(row=5, column=0, sticky=tk.W, padx=145)

        self.lbl_6 = tk.Label(self.master, text="Cantón:", width=20, font=("bold", 11))
        self.lbl_6.grid(row=6, column=0, sticky=tk.W, padx=14)

        self.option_menu2 = tk.OptionMenu(self.master, self.canton, "Escoja un Cantón")
        self.option_menu2.grid(row=6, column=0, sticky=tk.W, padx=145)

        self.lbl_7 = tk.Label(self.master, text="Parroquia:", width=20, font=("bold", 11))
        self.lbl_7.grid(row=7, column=0, sticky=tk.W, padx=14)

        self.option_menu3 = tk.OptionMenu(self.master, self.parroquia, "Escoja una Parroquia")
        self.option_menu3.grid(row=7, column=0, sticky=tk.W, padx=145)

        self.lbl_8 = tk.Label(self.master, text="Fecha inicio:", width=20, font=("bold", 11))
        self.lbl_8.grid(row=8, column=0, sticky=tk.W)

        self.fecha_inicio = tc.DateEntry(self.master, selectmode='day', date_pattern='yyyy-mm-dd')
        self.fecha_inicio.grid(row=8, column=0, sticky=tk.W, padx=145)

        self.lbl_9 = tk.Label(self.master, text="Fecha fin:", width=20, font=("bold", 11))
        self.lbl_9.grid(row=8, column=0, sticky=tk.W, padx=240)

        self.fecha_fin = tc.DateEntry(self.master, selectmode='day', date_pattern='yyyy-mm-dd')
        self.fecha_fin.grid(row=8, column=0, sticky=tk.W, padx=370)

        self.lbl_10 = tk.Label(self.master, text="Hora inicio:", width=20, font=("bold", 11))
        self.lbl_10.grid(row=9, column=0, sticky=tk.W, pady=10)

        self.tiempo_inicio = tk.Entry(self.master)
        self.tiempo_inicio.insert(0, "00:01")
        self.tiempo_inicio.grid(row=9, column=0, sticky=tk.W, padx=145, pady=10)

        self.lbl_11 = tk.Label(self.master, text="Hora fin:", width=20, font=("bold", 11))
        self.lbl_11.grid(row=9, column=0, sticky=tk.W, padx=240, pady=10)

        self.tiempo_fin = tk.Entry(self.master)
        self.tiempo_fin.insert(0, "23:59")
        self.tiempo_fin.grid(row=9, column=0, sticky=tk.W, padx=370, pady=10)

        self.lbl_12 = tk.Label(self.master, text="Umbral Leyenda [Mbps]:", width=20, font=("bold", 11))
        self.lbl_12.grid(row=10, column=0, sticky=tk.W, pady=10)

        self.umbral = tk.Entry(self.master)
        self.umbral.insert(0, "20")
        self.umbral.grid(row=10, column=0, sticky=tk.W, padx=175, pady=10)

    def toggle_button0_state(self):
        """Define button0 state conditions"""
        if self.repgen.get():
            self.button1.config(state=tk.DISABLED)
            self.button2.config(state=tk.DISABLED)
            self.button3.config(state=tk.DISABLED)
            self.button4.config(state=tk.DISABLED)
            self.button5.config(state=tk.DISABLED)
            self.button6.config(state=tk.DISABLED)
            self.button7.config(state=tk.DISABLED)
            self.button8.config(state=tk.DISABLED)
            self.button9.config(state=tk.DISABLED)
            self.button10.config(state=tk.DISABLED)
            self.button11.config(state=tk.DISABLED)
            self.option_menu0.config(state=tk.DISABLED)
        else:
            self.button1.config(state=tk.NORMAL)
            self.button2.config(state=tk.NORMAL)
            self.button3.config(state=tk.NORMAL)
            self.button4.config(state=tk.NORMAL)
            self.button5.config(state=tk.NORMAL)
            self.button6.config(state=tk.NORMAL)
            self.button7.config(state=tk.NORMAL)
            self.button8.config(state=tk.NORMAL)
            self.button9.config(state=tk.NORMAL)
            self.button10.config(state=tk.NORMAL)
            self.button11.config(state=tk.NORMAL)
            self.option_menu0.config(state=tk.NORMAL)

    def toggle_button1_state(self):
        """Define button1 state conditions"""
        if self.mapa.get():
            self.button0.config(state=tk.DISABLED)
            self.button2.config(state=tk.DISABLED)
            self.option_menu1.config(state=tk.DISABLED)
            self.option_menu2.config(state=tk.DISABLED)
            self.option_menu3.config(state=tk.DISABLED)
        else:
            self.button0.config(state=tk.NORMAL)
            self.button2.config(state=tk.NORMAL)
            self.option_menu1.config(state=tk.NORMAL)
            self.option_menu2.config(state=tk.NORMAL)
            self.option_menu3.config(state=tk.NORMAL)

    def toggle_button2_state(self):
        """Define button1 state conditions"""
        if self.mapaparroquia.get():
            self.button0.config(state=tk.DISABLED)
            self.button1.config(state=tk.DISABLED)
            self.option_menu0.config(state=tk.DISABLED)
        else:
            self.button0.config(state=tk.NORMAL)
            self.button1.config(state=tk.NORMAL)
            self.option_menu0.config(state=tk.NORMAL)

    def start(self):
        """Define start button actions"""
        if start_button['text'] == 'Iniciar':
            self.program_is_running = True
            start_button['text'] = "Detener"
            self.program()

        else:
            self.program_is_running = False
            start_button['text'] = "Iniciar"

    def quit(self):
        """Define quit button actions"""
        really_quit = messagebox.askyesno("Cerrar?", "Desea cerrar el programa?")
        if really_quit:
            self.master.destroy()

    def program(self):
        """Define base program actions. All data analysis is presented in this section of the code."""

        # define a function to build the technology_types tuple
        def get_operadora():
            operadora_sel = []
            if self.operadora1.get():
                operadora_sel.append('Claro')
            if self.operadora2.get():
                operadora_sel.append('CNT')
            if self.operadora3.get():
                operadora_sel.append('Movistar')
            if len(operadora_sel) == 1:  # if only one operator is selected, return string instead of tuple
                return operadora_sel[0]
            else:
                return tuple(operadora_sel)

        operadora = get_operadora()

        # define a function to build the technology_types tuple
        def get_technology_types():
            technology_types = []
            if self.technology1.get():
                technology_types.append('WCDMA')
            if self.technology2.get():
                technology_types.append('LTE')
            if len(technology_types) == 1:  # if only one tecknology is selected, return string instead of tuple
                return technology_types[0]
            else:
                return tuple(technology_types)

        technology = get_technology_types()

        # define a function to build the session_types tuple
        def get_session_types():
            session_types = []
            if self.sessiontype1.get():
                session_types.append('HTTP Download')
            if self.sessiontype2.get():
                session_types.append('HTTP Post')
            if self.sessiontype3.get():
                session_types.append('FTP Download')
            if self.sessiontype4.get():
                session_types.append('FTP Post')
            if len(session_types) == 1:  # if only one session type is selected, return string instead of tuple
                return session_types[0]
            else:
                return tuple(session_types)

        sessiontype = get_session_types()

        czo = self.czo.get()
        provincia = self.provincia.get()
        canton = self.canton.get()
        parroquia = self.parroquia.get()
        fecha_inicio = self.fecha_inicio.get_date().strftime("%Y-%m-%d")
        fecha_fin = self.fecha_fin.get_date().strftime("%Y-%m-%d")
        tiempo_inicio = self.tiempo_inicio.get()
        tiempo_fin = self.tiempo_fin.get()

        # Add HH:MM:SS to fecha_inicio and fecha_fin so the range of dates we want to show in the report is correct
        add_string1 = f' {tiempo_inicio}:00'
        add_string2 = f' {tiempo_fin}:00'
        fecha_inicio += add_string1
        fecha_fin += add_string2

        def convert(date_time):
            """function to convert a string to datetime object"""
            date_format = '%Y-%m-%d %H:%M:%S'  # The format
            datetime_str = datetime.datetime.strptime(date_time, date_format)
            return datetime_str

        # Convert fecha_inicio and fecha_fin to datetime object
        fecha_inicio = convert(fecha_inicio)
        fecha_fin = convert(fecha_fin)
        umbral = float(self.umbral.get())

        # Define the SQL querys to be executed
        if isinstance(operadora, tuple):  # if operadora is a tuple, use IN operator in SQL query
            operadora_query = f"SimOperator IN {operadora}"
        else:  # if operadora is a string, use = operator in SQL query
            operadora_query = f"SimOperator = '{operadora}'"
        if isinstance(sessiontype, tuple):  # if sessiontype is a tuple, use IN operator in SQL query
            sessiontype_query = f"SessionType IN {sessiontype}"
        else:  # if sessiontype is a string, use = sessiontype in SQL query
            sessiontype_query = f"SessionType = '{sessiontype}'"
        if isinstance(technology, tuple):  # if technology is a tuple, use IN operator in SQL query
            technology_query1 = f"StartRadioTechnology IN {technology}"
            technology_query2 = f"EndRadioTechnology IN {technology}"
        else:  # if technology is a string, use = technology in SQL query
            technology_query1 = f"StartRadioTechnology = '{technology}'"
            technology_query2 = f"EndRadioTechnology = '{technology}'"

        if self.repgen.get():
            sql_query1 = f"SELECT DatasourceId, SessionIdOrCallIndex, SessionType, StartTime, StartLatitude, " \
                         f"StartLongitude, StartRadioTechnology, EndTime, EndLatitude, EndLongitude, " \
                         f"EndRadioTechnology, SimOperator, IMSI, IMEI, SessionEndStatus " \
                         f"FROM {os.getenv('TABLE1')} " \
                         f"WHERE StartTime >= '{fecha_inicio}' AND EndTime <= '{fecha_fin}';"
            sql_query2 = f"SELECT DatasourceId, SessionId, SessionType, StartDateTime, EndDateTime, Url, " \
                         f"EndServiceBearer, EndDataRadioBearer, EndFileSize, EndServiceStatus, " \
                         f"IPServiceSetupTimeMethodAMethod, DataTransferTimeMethodADuration " \
                         f"FROM {os.getenv('TABLE2')} " \
                         f"WHERE StartDateTime >= '{fecha_inicio}' AND EndDateTime <= '{fecha_fin}';"
        elif self.mapa.get() or self.mapaparroquia.get():
            sql_query1 = f"SELECT DatasourceId, SessionIdOrCallIndex, SessionType, StartTime, StartLatitude, " \
                         f"StartLongitude, StartRadioTechnology, EndTime, EndLatitude, EndLongitude, " \
                         f"EndRadioTechnology, SimOperator, IMSI, IMEI, SessionEndStatus " \
                         f"FROM {os.getenv('TABLE1')} " \
                         f"WHERE StartTime >= '{fecha_inicio}' AND EndTime <= '{fecha_fin}' " \
                         f"AND {sessiontype_query} " \
                         f"AND {technology_query1} " \
                         f"AND {technology_query2} " \
                         f"AND {operadora_query};"

            sql_query2 = f"SELECT DatasourceId, SessionId, SessionType, StartDateTime, EndDateTime, Url, " \
                         f"EndServiceBearer, EndDataRadioBearer, EndFileSize, EndServiceStatus, " \
                         f"IPServiceSetupTimeMethodAMethod, DataTransferTimeMethodADuration " \
                         f"FROM {os.getenv('TABLE2')} " \
                         f"WHERE StartDateTime >= '{fecha_inicio}' AND EndDateTime <= '{fecha_fin}' " \
                         f"AND {sessiontype_query};"

        try:
            # Create the engine according to SQLAlchemy documentation
            connection_string = f"DRIVER={os.getenv('DRIVER_NAME')};SERVER={os.getenv('SERVER_NAME')};" \
                                f"DATABASE={os.getenv('DATABASE_NAME')};Trusted_Connection=yes;"
            connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
            engine = create_engine(connection_url)

            # Define decimal separator as comma
            decimal_sep = ","

            # Establish a connection to the database, execute the query and create the df with the results
            with engine.begin() as conn:
                df1 = pd.read_sql_query(sa.text(sql_query1), conn, params={"decimal": decimal_sep})
                df2 = pd.read_sql_query(sa.text(sql_query2), conn, params={"decimal": decimal_sep})

            # Close the connection object
            conn.close()

        except Exception as e:
            # If the connection to the database fails, print the error message and close the program
            print('Database connection failed.')

        # Rename columns in the dataframes
        df1 = df1.rename(columns={'SessionIdOrCallIndex': 'SessionId', 'SessionEndStatus': 'EndServiceStatus'})
        df2 = df2.rename(columns={'StartDateTime': 'StartTime', 'EndDateTime': 'EndTime'})

        # DATA CLEANING
        # Convert time columns to datetime in a specific format. Convert coordinates and file size to float
        df1['StartTime'] = pd.to_datetime(df1['StartTime'], format='%Y-%m-%d %H:%M:%S.%f')
        df1['EndTime'] = pd.to_datetime(df1['EndTime'], format='%Y-%m-%d %H:%M:%S.%f')
        df1['StartLatitude'] = df1['StartLatitude'].astype(float)
        df1['StartLongitude'] = df1['StartLongitude'].astype(float)
        df1['EndLatitude'] = df1['EndLatitude'].astype(float)
        df1['EndLongitude'] = df1['EndLongitude'].astype(float)
        df1['IMSI'] = df1['IMSI'].astype(str)
        df1['IMEI'] = df1['IMEI'].astype(str)
        df2['StartTime'] = pd.to_datetime(df2['StartTime'], format='%Y-%m-%d %H:%M:%S.%f')
        df2['EndTime'] = pd.to_datetime(df2['EndTime'], format='%Y-%m-%d %H:%M:%S.%f')
        df2['EndFileSize'] = df2['EndFileSize'].astype(float)

        # Merge df1 and df2 by: 'DatasourceId', 'SessionId', 'SessionType', 'StartTime', 'EndTime', 'EndServiceStatus'
        df = df1.merge(df2, how='right', on=['DatasourceId', 'SessionId', 'SessionType', 'StartTime', 'EndTime',
                                             'EndServiceStatus'])

        # dfsense: read the data in sense_file file and convert it to a pandas dataframe
        columnsSense = ['Device', 'IMSI', 'IMEI', 'CZO']
        dfsense = pd.read_excel(os.getenv('sense_file'), usecols=columnsSense)
        dfsense['IMSI'] = dfsense['IMSI'].astype(str)
        dfsense['IMEI'] = dfsense['IMEI'].astype(str)

        # Merge df and dfsense by: 'IMSI', 'IMEI'
        df = df.merge(dfsense, how='left', on=['IMSI', 'IMEI'])

        def throughput(row):
            """function to return the throughput value """
            if row['EndFileSize'] != 0 and row['EndServiceStatus'] == 'Succeeded' and isinstance(
                    row['DataTransferTimeMethodADuration'], datetime.time):
                total_seconds = (row['DataTransferTimeMethodADuration'].hour * 3600) + (
                        row['DataTransferTimeMethodADuration'].minute * 60) + row[
                                    'DataTransferTimeMethodADuration'].second + row[
                                    'DataTransferTimeMethodADuration'].microsecond / 1000000
                try:
                    return (float(row['EndFileSize']) * 8) / total_seconds / 1024 / 1024
                except ZeroDivisionError:
                    return None
            else:
                return None

        # Create a new column with the throughput value
        df['ThroughputMbps'] = df.apply(lambda row: throughput(row), axis=1)

        # Remove the previous files if already exist
        if os.path.exists(
                f"{os.getenv('download_route')}/FullSessionSummary.csv"):
            os.remove(
                f"{os.getenv('download_route')}/FullSessionSummary.csv")

        # Pass the df to a .csv file
        df.to_csv(f"{os.getenv('download_route')}/FullSessionSummary.csv", index=False, sep=';', encoding='utf-8',
                  header=True, decimal=',')

        # Filter the df by the selected parameters
        if self.repgen.get():
            # create a geometry column in the normal dataframe
            df['geometry'] = df.apply(lambda row: LineString(
                [(row['StartLongitude'], row['StartLatitude']), (row['EndLongitude'], row['EndLatitude'])]), axis=1)
            df = gpd.GeoDataFrame(df, geometry='geometry', crs=4326)

            # filter by geo_data dataframe (gdf)
            gdf1 = gdf.loc[
                (gdf['DPA_DESPRO'] == provincia) & (gdf['DPA_DESCAN'] == canton) & (gdf['DPA_DESPAR'] == parroquia)]
            gdf1 = gdf1.to_crs(df.crs)

            # Convert the geometry of the geopandas dataframe to a GeoJSON format
            gdf_json = gdf1.to_json()

            df = df[df.apply(lambda row: Point(row['StartLongitude'], row['StartLatitude']).within(
                gdf1['geometry'].iloc[0]) and Point(row['EndLongitude'], row['EndLatitude']).within(
                gdf1['geometry'].iloc[0]), axis=1)].drop(columns=['geometry'])

            # write to .csv file
            filename = f'SessionSummary_{provincia}_{canton}_{parroquia}'
            if fecha_inicio.strftime('%Y-%m-%d') == fecha_fin.strftime('%Y-%m-%d'):
                filename = f'{filename}_{fecha_inicio.strftime("%Y-%m-%d")}.csv'
            else:
                filename = f'{filename}_{fecha_inicio.strftime("%Y-%m-%d")}_{fecha_fin.strftime("%Y-%m-%d")}.csv'

            df.to_csv(filename, index=False, sep=';', encoding='utf-8', header=True, decimal=',')

            filePath = f"{os.getenv('download_route')}/{filename}"

            if os.path.exists(filePath):
                os.remove(filePath)
            os.rename(filename, filePath)

            def get_dataframes(df):
                operators = ['Claro', 'CNT', 'Movistar']
                technologies = {'3g': 'WCDMA', '4g': 'LTE'}
                session_types = {'ul_http': 'HTTP Post', 'dl_http': 'HTTP Download', 'ul_ftp': 'FTP Post',
                                 'dl_ftp': 'FTP Download'}
                df_dict = {}

                for op in operators:
                    for tech in technologies:
                        for st in session_types:
                            df_name = f"df_{op.lower()}_{tech}_{st}"
                            df_dict[df_name] = df.loc[(df['SimOperator'] == op) &
                                                      (df['StartRadioTechnology'] == technologies[tech]) &
                                                      (df['EndRadioTechnology'] == technologies[tech]) &
                                                      (df['SessionType'] == session_types[st])]
                            for st in session_types:
                                df_type_name = f"{df_name.lower()}"
                                df_dict[f"{df_type_name}_fail"] = df_dict[df_type_name].loc[
                                    df_dict[df_type_name]['EndServiceStatus'] == 'Failed']
                                df_dict[f"{df_type_name}_succ"] = df_dict[df_type_name].loc[
                                    df_dict[df_type_name]['EndServiceStatus'] == 'Succeeded']

                return df_dict

            df_dict = get_dataframes(df)

            def divide_or_nan(x, y):
                with np.errstate(divide='ignore', invalid='ignore'):
                    try:
                        result = x / y
                    except ZeroDivisionError:
                        result = np.nan
                return result

            # Create the first dataframe for the report
            datos1 = {'Prestador': ['Conecel', 'CNT EP', 'Otecel'],
                      '% Sesiones HTTP Fallidas 3G': [divide_or_nan((df_dict['df_claro_3g_ul_http_fail'][
                                                                         'EndServiceStatus'].count() +
                                                                     df_dict['df_claro_3g_dl_http_fail'][
                                                                         'EndServiceStatus'].count()), (
                                                                            df_dict['df_claro_3g_ul_http_succ'][
                                                                                'EndServiceStatus'].count() +
                                                                            df_dict['df_claro_3g_dl_http_succ'][
                                                                                'EndServiceStatus'].count())) * 100,
                                                      divide_or_nan((df_dict['df_cnt_3g_ul_http_fail'][
                                                                         'EndServiceStatus'].count() +
                                                                     df_dict['df_cnt_3g_dl_http_fail'][
                                                                         'EndServiceStatus'].count()), (
                                                                            df_dict['df_cnt_3g_ul_http_succ'][
                                                                                'EndServiceStatus'].count() +
                                                                            df_dict['df_cnt_3g_dl_http_succ'][
                                                                                'EndServiceStatus'].count())) * 100,
                                                      divide_or_nan((df_dict['df_movistar_3g_ul_http_fail'][
                                                                         'EndServiceStatus'].count() +
                                                                     df_dict['df_movistar_3g_dl_http_fail'][
                                                                         'EndServiceStatus'].count()), (
                                                                            df_dict['df_movistar_3g_ul_http_succ'][
                                                                                'EndServiceStatus'].count() +
                                                                            df_dict['df_movistar_3g_dl_http_succ'][
                                                                                'EndServiceStatus'].count())) * 100],
                      '% Sesiones HTTP Fallidas 4G': [divide_or_nan((df_dict['df_claro_4g_ul_http_fail'][
                                                                         'EndServiceStatus'].count() +
                                                                     df_dict['df_claro_4g_dl_http_fail'][
                                                                         'EndServiceStatus'].count()), (
                                                                            df_dict['df_claro_4g_ul_http_succ'][
                                                                                'EndServiceStatus'].count() +
                                                                            df_dict['df_claro_4g_dl_http_succ'][
                                                                                'EndServiceStatus'].count())) * 100,
                                                      divide_or_nan((df_dict['df_cnt_4g_ul_http_fail'][
                                                                         'EndServiceStatus'].count() +
                                                                     df_dict['df_cnt_4g_dl_http_fail'][
                                                                         'EndServiceStatus'].count()), (
                                                                            df_dict['df_cnt_4g_ul_http_succ'][
                                                                                'EndServiceStatus'].count() +
                                                                            df_dict['df_cnt_4g_dl_http_succ'][
                                                                                'EndServiceStatus'].count())) * 100,
                                                      divide_or_nan((df_dict['df_movistar_4g_ul_http_fail'][
                                                                         'EndServiceStatus'].count() +
                                                                     df_dict['df_movistar_4g_dl_http_fail'][
                                                                         'EndServiceStatus'].count()), (
                                                                            df_dict['df_movistar_4g_ul_http_succ'][
                                                                                'EndServiceStatus'].count() +
                                                                            df_dict['df_movistar_4g_dl_http_succ'][
                                                                                'EndServiceStatus'].count())) * 100],
                      'Promedio HTTP UL 3G Mbps': [df_dict['df_claro_3g_ul_http']['ThroughputMbps'].mean(),
                                                   df_dict['df_cnt_3g_ul_http']['ThroughputMbps'].mean(),
                                                   df_dict['df_movistar_3g_ul_http']['ThroughputMbps'].mean()],
                      'Promedio HTTP DL 3G Mbps': [df_dict['df_claro_3g_dl_http']['ThroughputMbps'].mean(),
                                                   df_dict['df_cnt_3g_dl_http']['ThroughputMbps'].mean(),
                                                   df_dict['df_movistar_3g_dl_http']['ThroughputMbps'].mean()],
                      'Promedio HTTP UL 4G Mbps': [df_dict['df_claro_4g_ul_http']['ThroughputMbps'].mean(),
                                                   df_dict['df_cnt_4g_ul_http']['ThroughputMbps'].mean(),
                                                   df_dict['df_movistar_4g_ul_http']['ThroughputMbps'].mean()],
                      'Promedio HTTP DL 4G Mbps': [df_dict['df_claro_4g_dl_http']['ThroughputMbps'].mean(),
                                                   df_dict['df_cnt_4g_dl_http']['ThroughputMbps'].mean(),
                                                   df_dict['df_movistar_4g_dl_http']['ThroughputMbps'].mean()],
                      '% Sesiones FTP Fallidas 3G': [divide_or_nan((df_dict['df_claro_3g_ul_ftp_fail'][
                                                                        'EndServiceStatus'].count() +
                                                                    df_dict['df_claro_3g_dl_ftp_fail'][
                                                                        'EndServiceStatus'].count()), (
                                                                           df_dict['df_claro_3g_ul_ftp_succ'][
                                                                               'EndServiceStatus'].count() +
                                                                           df_dict['df_claro_3g_dl_ftp_succ'][
                                                                               'EndServiceStatus'].count())) * 100,
                                                     divide_or_nan((df_dict['df_cnt_3g_ul_ftp_fail'][
                                                                        'EndServiceStatus'].count() +
                                                                    df_dict['df_cnt_3g_dl_ftp_fail'][
                                                                        'EndServiceStatus'].count()), (
                                                                           df_dict['df_cnt_3g_ul_ftp_succ'][
                                                                               'EndServiceStatus'].count() +
                                                                           df_dict['df_cnt_3g_dl_ftp_succ'][
                                                                               'EndServiceStatus'].count())) * 100,
                                                     divide_or_nan((df_dict['df_movistar_3g_ul_ftp_fail'][
                                                                        'EndServiceStatus'].count() +
                                                                    df_dict['df_movistar_3g_dl_ftp_fail'][
                                                                        'EndServiceStatus'].count()), (
                                                                           df_dict['df_movistar_3g_ul_ftp_succ'][
                                                                               'EndServiceStatus'].count() +
                                                                           df_dict['df_movistar_3g_dl_ftp_succ'][
                                                                               'EndServiceStatus'].count())) * 100],
                      '% Sesiones FTP Fallidas 4G': [divide_or_nan((df_dict['df_claro_4g_ul_ftp_fail'][
                                                                        'EndServiceStatus'].count() +
                                                                    df_dict['df_claro_4g_dl_ftp_fail'][
                                                                        'EndServiceStatus'].count()), (
                                                                           df_dict['df_claro_4g_ul_ftp_succ'][
                                                                               'EndServiceStatus'].count() +
                                                                           df_dict['df_claro_4g_dl_ftp_succ'][
                                                                               'EndServiceStatus'].count())) * 100,
                                                     divide_or_nan((df_dict['df_cnt_4g_ul_ftp_fail'][
                                                                        'EndServiceStatus'].count() +
                                                                    df_dict['df_cnt_4g_dl_ftp_fail'][
                                                                        'EndServiceStatus'].count()), (
                                                                           df_dict['df_cnt_4g_ul_ftp_succ'][
                                                                               'EndServiceStatus'].count() +
                                                                           df_dict['df_cnt_4g_dl_ftp_succ'][
                                                                               'EndServiceStatus'].count())) * 100,
                                                     divide_or_nan((df_dict['df_movistar_4g_ul_ftp_fail'][
                                                                        'EndServiceStatus'].count() +
                                                                    df_dict['df_movistar_4g_dl_ftp_fail'][
                                                                        'EndServiceStatus'].count()), (
                                                                           df_dict['df_movistar_4g_ul_ftp_succ'][
                                                                               'EndServiceStatus'].count() +
                                                                           df_dict['df_movistar_4g_dl_ftp_succ'][
                                                                               'EndServiceStatus'].count())) * 100],
                      'Promedio FTP UL 3G Mbps': [df_dict['df_claro_3g_ul_ftp']['ThroughputMbps'].mean(),
                                                  df_dict['df_cnt_3g_ul_ftp']['ThroughputMbps'].mean(),
                                                  df_dict['df_movistar_3g_ul_ftp']['ThroughputMbps'].mean()],
                      'Promedio FTP DL 3G Mbps': [df_dict['df_claro_3g_dl_ftp']['ThroughputMbps'].mean(),
                                                  df_dict['df_cnt_3g_dl_ftp']['ThroughputMbps'].mean(),
                                                  df_dict['df_movistar_3g_dl_ftp']['ThroughputMbps'].mean()],
                      'Promedio FTP UL 4G Mbps': [df_dict['df_claro_4g_ul_ftp']['ThroughputMbps'].mean(),
                                                  df_dict['df_cnt_4g_ul_ftp']['ThroughputMbps'].mean(),
                                                  df_dict['df_movistar_4g_ul_ftp']['ThroughputMbps'].mean()],
                      'Promedio FTP DL 4G Mbps': [df_dict['df_claro_4g_dl_ftp']['ThroughputMbps'].mean(),
                                                  df_dict['df_cnt_4g_dl_ftp']['ThroughputMbps'].mean(),
                                                  df_dict['df_movistar_4g_dl_ftp']['ThroughputMbps'].mean()]}
            df_1 = pd.DataFrame(data=datos1)
            df_1['% Sesiones HTTP Fallidas 3G'] = df_1['% Sesiones HTTP Fallidas 3G'].round(2)
            df_1['% Sesiones HTTP Fallidas 4G'] = df_1['% Sesiones HTTP Fallidas 4G'].round(2)
            df_1['Promedio HTTP UL 3G Mbps'] = df_1['Promedio HTTP UL 3G Mbps'].round(1)
            df_1['Promedio HTTP DL 3G Mbps'] = df_1['Promedio HTTP DL 3G Mbps'].round(1)
            df_1['Promedio HTTP UL 4G Mbps'] = df_1['Promedio HTTP UL 4G Mbps'].round(1)
            df_1['Promedio HTTP DL 4G Mbps'] = df_1['Promedio HTTP DL 4G Mbps'].round(1)
            df_1['% Sesiones FTP Fallidas 3G'] = df_1['% Sesiones FTP Fallidas 3G'].round(2)
            df_1['% Sesiones FTP Fallidas 4G'] = df_1['% Sesiones FTP Fallidas 4G'].round(2)
            df_1['Promedio FTP UL 3G Mbps'] = df_1['Promedio FTP UL 3G Mbps'].round(1)
            df_1['Promedio FTP DL 3G Mbps'] = df_1['Promedio FTP DL 3G Mbps'].round(1)
            df_1['Promedio FTP UL 4G Mbps'] = df_1['Promedio FTP UL 4G Mbps'].round(1)
            df_1['Promedio FTP DL 4G Mbps'] = df_1['Promedio FTP DL 4G Mbps'].round(1)
            df_1 = df_1.fillna('-')

            # Create the second dataframe for the report
            datos2 = {'Prestador': ['Conecel', 'CNT EP', 'Otecel'],
                      'Total Sesiones HTTP UL 3G': [df_dict['df_claro_3g_ul_http']['EndServiceStatus'].count(),
                                                    df_dict['df_cnt_3g_ul_http']['EndServiceStatus'].count(),
                                                    df_dict['df_movistar_3g_ul_http']['EndServiceStatus'].count()],
                      'Total Sesiones HTTP DL 3G': [df_dict['df_claro_3g_dl_http']['EndServiceStatus'].count(),
                                                    df_dict['df_cnt_3g_dl_http']['EndServiceStatus'].count(),
                                                    df_dict['df_movistar_3g_dl_http']['EndServiceStatus'].count()],
                      'Total tareas HTTP UL 3G': [df_dict['df_claro_3g_ul_http']['ThroughputMbps'].count(),
                                                  df_dict['df_cnt_3g_ul_http']['ThroughputMbps'].count(),
                                                  df_dict['df_movistar_3g_ul_http']['ThroughputMbps'].count()],
                      'Total tareas HTTP DL 3G': [df_dict['df_claro_3g_dl_http']['ThroughputMbps'].count(),
                                                  df_dict['df_cnt_3g_dl_http']['ThroughputMbps'].count(),
                                                  df_dict['df_movistar_3g_dl_http']['ThroughputMbps'].count()],
                      'Total Sesiones FTP UL 3G': [df_dict['df_claro_3g_ul_ftp']['EndServiceStatus'].count(),
                                                   df_dict['df_cnt_3g_ul_ftp']['EndServiceStatus'].count(),
                                                   df_dict['df_movistar_3g_ul_ftp']['EndServiceStatus'].count()],
                      'Total Sesiones FTP DL 3G': [df_dict['df_claro_3g_dl_ftp']['EndServiceStatus'].count(),
                                                   df_dict['df_cnt_3g_dl_ftp']['EndServiceStatus'].count(),
                                                   df_dict['df_movistar_3g_dl_ftp']['EndServiceStatus'].count()],
                      'Total tareas FTP UL 3G': [df_dict['df_claro_3g_ul_ftp']['ThroughputMbps'].count(),
                                                 df_dict['df_cnt_3g_ul_ftp']['ThroughputMbps'].count(),
                                                 df_dict['df_movistar_3g_ul_ftp']['ThroughputMbps'].count()],
                      'Total tareas FTP DL 3G': [df_dict['df_claro_3g_dl_ftp']['ThroughputMbps'].count(),
                                                 df_dict['df_cnt_3g_dl_ftp']['ThroughputMbps'].count(),
                                                 df_dict['df_movistar_3g_dl_ftp']['ThroughputMbps'].count()]}
            df_2 = pd.DataFrame(data=datos2)
            df_2 = df_2.fillna('-')

            # Create the final dataframe for the report
            datos3 = {'Prestador': ['Conecel', 'CNT EP', 'Otecel'],
                      'Total Sesiones HTTP UL 4G': [df_dict['df_claro_4g_ul_http']['EndServiceStatus'].count(),
                                                    df_dict['df_cnt_4g_ul_http']['EndServiceStatus'].count(),
                                                    df_dict['df_movistar_4g_ul_http']['EndServiceStatus'].count()],
                      'Total Sesiones HTTP DL 4G': [df_dict['df_claro_4g_dl_http']['EndServiceStatus'].count(),
                                                    df_dict['df_cnt_4g_dl_http']['EndServiceStatus'].count(),
                                                    df_dict['df_movistar_4g_dl_http']['EndServiceStatus'].count()],
                      'Total tareas HTTP UL 4G': [df_dict['df_claro_4g_ul_http']['ThroughputMbps'].count(),
                                                  df_dict['df_cnt_4g_ul_http']['ThroughputMbps'].count(),
                                                  df_dict['df_movistar_4g_ul_http']['ThroughputMbps'].count()],
                      'Total tareas HTTP DL 4G': [df_dict['df_claro_4g_dl_http']['ThroughputMbps'].count(),
                                                  df_dict['df_cnt_4g_dl_http']['ThroughputMbps'].count(),
                                                  df_dict['df_movistar_4g_dl_http']['ThroughputMbps'].count()],
                      'Total Sesiones FTP UL 4G': [df_dict['df_claro_4g_ul_ftp']['EndServiceStatus'].count(),
                                                   df_dict['df_cnt_4g_ul_ftp']['EndServiceStatus'].count(),
                                                   df_dict['df_movistar_4g_ul_ftp']['EndServiceStatus'].count()],
                      'Total Sesiones FTP DL 4G': [df_dict['df_claro_4g_dl_ftp']['EndServiceStatus'].count(),
                                                   df_dict['df_cnt_4g_dl_ftp']['EndServiceStatus'].count(),
                                                   df_dict['df_movistar_4g_dl_ftp']['EndServiceStatus'].count()],
                      'Total tareas FTP UL 4G': [df_dict['df_claro_4g_ul_ftp']['ThroughputMbps'].count(),
                                                 df_dict['df_cnt_4g_ul_ftp']['ThroughputMbps'].count(),
                                                 df_dict['df_movistar_4g_ul_ftp']['ThroughputMbps'].count()],
                      'Total tareas FTP DL 4G': [df_dict['df_claro_4g_dl_ftp']['ThroughputMbps'].count(),
                                                 df_dict['df_cnt_4g_dl_ftp']['ThroughputMbps'].count(),
                                                 df_dict['df_movistar_4g_dl_ftp']['ThroughputMbps'].count()]}
            df_3 = pd.DataFrame(data=datos3)
            df_3 = df_3.fillna('-')

            """REPORT CREATION"""
            """create, write and save"""
            with pd.ExcelWriter(f"{os.getenv('download_route')}/Reporte.xlsx") as writer:
                df_1.set_index('Prestador').to_excel(writer, sheet_name='Reporte')

                """Get the xlsxwriter workbook and worksheet objects."""
                workbook = writer.book
                worksheet = writer.sheets[f'Reporte']

                """Add a format."""
                format1 = workbook.add_format({'border': 1, 'border_color': 'black'})

                """Get the dimensions of the first dataframe."""
                (max_row1, max_col1) = df_1.set_index('Prestador').shape

                """Apply a conditional format to the required cell range."""
                worksheet.conditional_format(1, 1, int(max_row1), int(max_col1),
                                             {'type': 'no_errors',
                                              'format': format1})

                """Get the dimensions of the second dataframe."""
                (max_row2, max_col2) = df_2.set_index('Prestador').shape

                """Write the second dataframe without conditional format."""
                df_2.set_index('Prestador').to_excel(writer, sheet_name='Reporte', startrow=int(max_row1) + 3)

                """Apply a conditional format to the required cell range."""
                worksheet.conditional_format(int(max_row1) + 4, 1, int(max_row1) + int(max_row2) + 3, int(max_col2),
                                             {'type': 'no_errors',
                                              'format': format1})

                """Get the dimensions of the final dataframe."""
                (max_row3, max_col3) = df_3.set_index('Prestador').shape

                """Write the final dataframe without conditional format."""
                df_3.set_index('Prestador').to_excel(writer, sheet_name='Reporte',
                                                     startrow=int(max_row1) + int(max_row2) + 6)

                """Apply a conditional format to the required cell range."""
                worksheet.conditional_format(int(max_row1) + int(max_row2) + 7, 1,
                                             int(max_row1) + int(max_row2) + int(max_row3) + 6, int(max_col3),
                                             {'type': 'no_errors',
                                              'format': format1})

            # write to .xlsx file
            oldname = 'Reporte.xlsx'
            if fecha_inicio.strftime('%Y-%m-%d') == fecha_fin.strftime('%Y-%m-%d'):
                filename = f'Reporte_{provincia}_{canton}_{parroquia}_{fecha_inicio.strftime("%Y-%m-%d")}.xlsx'
            else:
                filename = f'Reporte_{provincia}_{canton}_{parroquia}_{fecha_inicio.strftime("%Y-%m-%d")}_{fecha_fin.strftime("%Y-%m-%d")}.xlsx'

            filePath1 = f"{os.getenv('download_route')}/{oldname}"
            filePath2 = f"{os.getenv('download_route')}/{filename}"
            if os.path.exists(filePath2):
                os.remove(filePath2)
            os.rename(filePath1, filePath2)

        elif self.mapa.get():
            if czo != 'Nacional':
                df = df.loc[df['CZO'] == f'{czo}']
            df = df.loc[df['EndServiceStatus'] == 'Succeeded']
            if isinstance(operadora, tuple):
                df = df.loc[df['SimOperator'].isin(operadora)]
            else:
                df = df.loc[df['SimOperator'] == operadora]
            if isinstance(sessiontype, tuple):
                df = df.loc[df['SessionType'].isin(sessiontype)]
            else:
                df = df.loc[df['SessionType'] == sessiontype]
            if isinstance(technology, tuple):
                df = df.loc[df['StartRadioTechnology'].isin(technology)]
                df = df.loc[df['EndRadioTechnology'].isin(technology)]
                df = df.loc[df['StartRadioTechnology'] == df['EndRadioTechnology']]
            else:
                df = df.loc[df['StartRadioTechnology'] == technology]
                df = df.loc[df['EndRadioTechnology'] == technology]

            # Drop rows with NaN values in the following columns
            df = df.dropna(subset=['StartLatitude', 'StartLongitude', 'EndLatitude', 'EndLongitude', 'ThroughputMbps'])
            # Pass the df to a .csv file
            df.to_csv(f'SessionSummary_{operadora}_{sessiontype}_{technology}_{czo}.csv', index=False, sep=';',
                      encoding='utf-8',
                      header=True, decimal=',')

            # Remove the previous files if already exist
            if os.path.exists(
                    f"{os.getenv('download_route')}/SessionSummary_{operadora}_{sessiontype}_{technology}_{czo}.csv"):
                os.remove(
                    f"{os.getenv('download_route')}/SessionSummary_{operadora}_{sessiontype}_{technology}_{czo}.csv")

            # Download the .csv file
            os.rename(f'SessionSummary_{operadora}_{sessiontype}_{technology}_{czo}.csv',
                      f"{os.getenv('download_route')}/SessionSummary_{operadora}_{sessiontype}_{technology}_{czo}.csv")

        elif self.mapaparroquia.get():
            df = df.loc[df['EndServiceStatus'] == 'Succeeded']
            if isinstance(operadora, tuple):
                df = df.loc[df['SimOperator'].isin(operadora)]
            else:
                df = df.loc[df['SimOperator'] == operadora]
            if isinstance(sessiontype, tuple):
                df = df.loc[df['SessionType'].isin(sessiontype)]
            else:
                df = df.loc[df['SessionType'] == sessiontype]
            if isinstance(technology, tuple):
                df = df.loc[df['StartRadioTechnology'].isin(technology)]
                df = df.loc[df['EndRadioTechnology'].isin(technology)]
                df = df.loc[df['StartRadioTechnology'] == df['EndRadioTechnology']]
            else:
                df = df.loc[df['StartRadioTechnology'] == technology]
                df = df.loc[df['EndRadioTechnology'] == technology]
            # Drop rows with NaN values in the following columns
            df = df.dropna(subset=['StartLatitude', 'StartLongitude', 'EndLatitude', 'EndLongitude', 'ThroughputMbps'])

            # create a geometry column in the normal dataframe
            df['geometry'] = df.apply(lambda row: LineString(
                [(row['StartLongitude'], row['StartLatitude']), (row['EndLongitude'], row['EndLatitude'])]), axis=1)
            df = gpd.GeoDataFrame(df, geometry='geometry', crs=4326)

            # read the GeoJSON file
            gdf1 = gdf.loc[gdf['DPA_DESPRO'] == provincia]
            gdf1 = gdf1.loc[gdf1['DPA_DESCAN'] == canton]
            gdf1 = gdf1.loc[gdf1['DPA_DESPAR'] == parroquia]
            gdf1 = gdf1.to_crs(df.crs)

            # filter the rows in normal dataframe matching start and end points in geo dataframe
            df = df[df.apply(lambda row: Point(row['StartLongitude'], row['StartLatitude']).within(
                gdf1['geometry'].iloc[0]) and Point(row['EndLongitude'], row['EndLatitude']).within(
                gdf1['geometry'].iloc[0]), axis=1)].drop(columns=['geometry'])

            # Convert the geometry of the geopandas dataframe to a GeoJSON format
            gdf_json = gdf1.to_json()

            # Pass the df to a .csv file
            df.to_csv(f'SessionSummary_{operadora}_{sessiontype}_{technology}_{provincia}_{canton}_{parroquia}.csv',
                      index=False, sep=';',
                      encoding='utf-8',
                      header=True, decimal=',')

            # Remove the previous files if already exist
            if os.path.exists(
                    f"{os.getenv('download_route')}/SessionSummary_{operadora}_{sessiontype}_{technology}_{provincia}_{canton}_{parroquia}.csv"):
                os.remove(
                    f"{os.getenv('download_route')}/SessionSummary_{operadora}_{sessiontype}_{technology}_{provincia}_{canton}_{parroquia}.csv")

            # Download the .csv file
            os.rename(f'SessionSummary_{operadora}_{sessiontype}_{technology}_{provincia}_{canton}_{parroquia}.csv',
                      f"{os.getenv('download_route')}/SessionSummary_{operadora}_{sessiontype}_{technology}_{provincia}_{canton}_{parroquia}.csv")

        # Create de dataframes to be used for the map and the configuration for the map
        if self.repgen.get() or self.mapa.get() or self.mapaparroquia.get():
            # Round the values in the new column to 1 decimal
            df = df.dropna(subset=['StartLatitude', 'StartLongitude', 'EndLatitude', 'EndLongitude', 'ThroughputMbps'])
            df['ThroughputMbps'] = df['ThroughputMbps'].round(4)
            df_downup = df[
                ['SimOperator', 'StartRadioTechnology', 'SessionType', 'StartTime', 'StartLatitude', 'StartLongitude',
                 'EndTime', 'EndLatitude', 'EndLongitude', 'ThroughputMbps']].copy()
            df_downup['StartTime'] = df_downup['StartTime'].dt.strftime('%Y-%m-%d %H:%M:%S')
            df_downup['EndTime'] = df_downup['EndTime'].dt.strftime('%Y-%m-%d %H:%M:%S')
            df_downup = df_downup.rename(
                columns={'ThroughputMbps': 'Throughput [Mbps]', 'StartRadioTechnology': 'Technology'})

            umbral_step = float(umbral / 10)
            bins = np.arange(0, float(umbral + umbral_step), float(umbral_step))
            labels = [chr(i) for i in range(65, 65 + len(bins) - 1)]

            df_downup['Throughput Range [Mbps]'] = pd.cut(df_downup['Throughput [Mbps]'], bins=bins, labels=labels)
            df_downup['Throughput Range [Mbps]'] = df_downup['Throughput Range [Mbps]'].astype(str)

            for i in range(len(bins) - 1):
                start = bins[i]
                end = bins[i + 1]
                label = labels[i]
                df_downup['Throughput Range [Mbps]'] = df_downup['Throughput Range [Mbps]'].str.replace(str(label),
                                                                                                        label + '(' + str(
                                                                                                            start) + ' to ' + str(
                                                                                                            end) + ')')

            config = {'version': 'v1',
                      'config': {'visState': {'filters': [{'dataId': ['dataframe'],
                                                           'id': 'achvy8ihs',
                                                           'name': ['Throughput [Mbps]'],
                                                           'type': 'range',
                                                           'value': [0, umbral],
                                                           'enlarged': False,
                                                           'plotType': 'histogram',
                                                           'animationWindow': 'free',
                                                           'yAxis': None,
                                                           'speed': 1},
                                                          {'dataId': ['dataframe'],
                                                           'id': '1awb6ya3v',
                                                           'name': ['SessionType'],
                                                           'type': 'multiSelect',
                                                           'value': ['HTTP Download'],
                                                           'enlarged': False,
                                                           'plotType': 'histogram',
                                                           'animationWindow': 'free',
                                                           'yAxis': None,
                                                           'speed': 1},
                                                          {'dataId': ['dataframe'],
                                                           'id': '3f22rdabb',
                                                           'name': ['Technology'],
                                                           'type': 'multiSelect',
                                                           'value': ['LTE'],
                                                           'enlarged': False,
                                                           'plotType': 'histogram',
                                                           'animationWindow': 'free',
                                                           'yAxis': None,
                                                           'speed': 1},
                                                          {'dataId': ['dataframe'],
                                                           'id': 'ry0oxdv67',
                                                           'name': ['SimOperator'],
                                                           'type': 'multiSelect',
                                                           'value': ['CNT'],
                                                           'enlarged': False,
                                                           'plotType': 'histogram',
                                                           'animationWindow': 'free',
                                                           'yAxis': None,
                                                           'speed': 1}],
                                              'layers': [{'id': 'e2wg9g',
                                                          'type': 'point',
                                                          'config': {'dataId': 'dataframe',
                                                                     'label': 'inicio',
                                                                     'color': [18, 147, 154],
                                                                     'highlightColor': [252, 242, 26, 255],
                                                                     'columns': {'lat': 'StartLatitude',
                                                                                 'lng': 'StartLongitude',
                                                                                 'altitude': None},
                                                                     'isVisible': True,
                                                                     'visConfig': {'radius': 10,
                                                                                   'fixedRadius': False,
                                                                                   'opacity': 0.2,
                                                                                   'outline': False,
                                                                                   'thickness': 2,
                                                                                   'strokeColor': None,
                                                                                   'colorRange': {
                                                                                       'name': 'ColorBrewer RdBu-10',
                                                                                       'type': 'diverging',
                                                                                       'category': 'ColorBrewer',
                                                                                       'colors': ['#053061',
                                                                                                  '#2166ac',
                                                                                                  '#4393c3',
                                                                                                  '#92c5de',
                                                                                                  '#d1e5f0',
                                                                                                  '#fddbc7',
                                                                                                  '#f4a582',
                                                                                                  '#d6604d',
                                                                                                  '#b2182b',
                                                                                                  '#67001f'],
                                                                                       'reversed': True},
                                                                                   'strokeColorRange': {
                                                                                       'name': 'Global Warming',
                                                                                       'type': 'sequential',
                                                                                       'category': 'Uber',
                                                                                       'colors': ['#5A1846',
                                                                                                  '#900C3F',
                                                                                                  '#C70039',
                                                                                                  '#E3611C',
                                                                                                  '#F1920E',
                                                                                                  '#FFC300']},
                                                                                   'radiusRange': [0, 50],
                                                                                   'filled': True},
                                                                     'hidden': False,
                                                                     'textLabel': [{'field': None,
                                                                                    'color': [255, 255, 255],
                                                                                    'size': 18,
                                                                                    'offset': [0, 0],
                                                                                    'anchor': 'start',
                                                                                    'alignment': 'center'}]},
                                                          'visualChannels': {
                                                              'colorField': {'name': 'Throughput Range [Mbps]',
                                                                             'type': 'string'},
                                                              'colorScale': 'ordinal',
                                                              'strokeColorField': None,
                                                              'strokeColorScale': 'quantile',
                                                              'sizeField': {'name': 'Throughput [Mbps]',
                                                                            'type': 'real'},
                                                              'sizeScale': 'sqrt'}},
                                                         {'id': '6atv04',
                                                          'type': 'point',
                                                          'config': {'dataId': 'dataframe',
                                                                     'label': 'fin',
                                                                     'color': [18, 147, 154],
                                                                     'highlightColor': [252, 242, 26, 255],
                                                                     'columns': {'lat': 'EndLatitude',
                                                                                 'lng': 'EndLongitude',
                                                                                 'altitude': None},
                                                                     'isVisible': True,
                                                                     'visConfig': {'radius': 10,
                                                                                   'fixedRadius': False,
                                                                                   'opacity': 0.2,
                                                                                   'outline': False,
                                                                                   'thickness': 2,
                                                                                   'strokeColor': None,
                                                                                   'colorRange': {
                                                                                       'name': 'ColorBrewer RdBu-10',
                                                                                       'type': 'diverging',
                                                                                       'category': 'ColorBrewer',
                                                                                       'colors': ['#053061',
                                                                                                  '#2166ac',
                                                                                                  '#4393c3',
                                                                                                  '#92c5de',
                                                                                                  '#d1e5f0',
                                                                                                  '#fddbc7',
                                                                                                  '#f4a582',
                                                                                                  '#d6604d',
                                                                                                  '#b2182b',
                                                                                                  '#67001f'],
                                                                                       'reversed': True},
                                                                                   'strokeColorRange': {
                                                                                       'name': 'Global Warming',
                                                                                       'type': 'sequential',
                                                                                       'category': 'Uber',
                                                                                       'colors': ['#5A1846',
                                                                                                  '#900C3F',
                                                                                                  '#C70039',
                                                                                                  '#E3611C',
                                                                                                  '#F1920E',
                                                                                                  '#FFC300']},
                                                                                   'radiusRange': [0, 50],
                                                                                   'filled': True},
                                                                     'hidden': False,
                                                                     'textLabel': [{'field': None,
                                                                                    'color': [255, 255, 255],
                                                                                    'size': 18,
                                                                                    'offset': [0, 0],
                                                                                    'anchor': 'start',
                                                                                    'alignment': 'center'}]},
                                                          'visualChannels': {
                                                              'colorField': {'name': 'Throughput Range [Mbps]',
                                                                             'type': 'string'},
                                                              'colorScale': 'ordinal',
                                                              'strokeColorField': None,
                                                              'strokeColorScale': 'quantile',
                                                              'sizeField': {'name': 'Throughput [Mbps]',
                                                                            'type': 'real'},
                                                              'sizeScale': 'sqrt'}},
                                                         {'id': 'vi88h2r',
                                                          'type': 'arc',
                                                          'config': {'dataId': 'dataframe',
                                                                     'label': 'start -> end arc',
                                                                     'color': [146, 38, 198],
                                                                     'highlightColor': [252, 242, 26, 255],
                                                                     'columns': {'lat0': 'StartLatitude',
                                                                                 'lng0': 'StartLongitude',
                                                                                 'lat1': 'EndLatitude',
                                                                                 'lng1': 'EndLongitude'},
                                                                     'isVisible': True,
                                                                     'visConfig': {'opacity': 0.8,
                                                                                   'thickness': 2,
                                                                                   'colorRange': {
                                                                                       'name': 'ColorBrewer RdBu-10',
                                                                                       'type': 'diverging',
                                                                                       'category': 'ColorBrewer',
                                                                                       'colors': ['#053061',
                                                                                                  '#2166ac',
                                                                                                  '#4393c3',
                                                                                                  '#92c5de',
                                                                                                  '#d1e5f0',
                                                                                                  '#fddbc7',
                                                                                                  '#f4a582',
                                                                                                  '#d6604d',
                                                                                                  '#b2182b',
                                                                                                  '#67001f'],
                                                                                       'reversed': True},
                                                                                   'sizeRange': [0, 1],
                                                                                   'targetColor': None},
                                                                     'hidden': False,
                                                                     'textLabel': [{'field': None,
                                                                                    'color': [255, 255, 255],
                                                                                    'size': 18,
                                                                                    'offset': [0, 0],
                                                                                    'anchor': 'start',
                                                                                    'alignment': 'center'}]},
                                                          'visualChannels': {'colorField': {'name': 'Throughput [Mbps]',
                                                                                            'type': 'real'},
                                                                             'colorScale': 'quantize',
                                                                             'sizeField': {'name': 'Throughput [Mbps]',
                                                                                           'type': 'real'},
                                                                             'sizeScale': 'linear'}},
                                                         {'id': 'hot34ar',
                                                          'type': 'geojson',
                                                          'config': {'dataId': 'shapefile',
                                                                     'label': 'shapefile',
                                                                     'color': [71, 211, 217],
                                                                     'highlightColor': [252, 242, 26, 255],
                                                                     'columns': {'geojson': '_geojson'},
                                                                     'isVisible': True,
                                                                     'visConfig': {'opacity': 0.05,
                                                                                   'strokeOpacity': 0.8,
                                                                                   'thickness': 0.5,
                                                                                   'strokeColor': [71, 211, 217],
                                                                                   'colorRange': {
                                                                                       'name': 'Uber Viz Diverging 1.5',
                                                                                       'type': 'diverging',
                                                                                       'category': 'Uber',
                                                                                       'colors': ['#00939C',
                                                                                                  '#5DBABF',
                                                                                                  '#BAE1E2',
                                                                                                  '#F8C0AA',
                                                                                                  '#DD7755',
                                                                                                  '#C22E00']},
                                                                                   'strokeColorRange': {
                                                                                       'name': 'Global Warming',
                                                                                       'type': 'sequential',
                                                                                       'category': 'Uber',
                                                                                       'colors': ['#5A1846',
                                                                                                  '#900C3F',
                                                                                                  '#C70039',
                                                                                                  '#E3611C',
                                                                                                  '#F1920E',
                                                                                                  '#FFC300']},
                                                                                   'radius': 10,
                                                                                   'sizeRange': [0, 10],
                                                                                   'radiusRange': [0, 50],
                                                                                   'heightRange': [0, 500],
                                                                                   'elevationScale': 0.1,
                                                                                   'enableElevationZoomFactor': True,
                                                                                   'stroked': True,
                                                                                   'filled': True,
                                                                                   'enable3d': True,
                                                                                   'wireframe': False},
                                                                     'hidden': False,
                                                                     'textLabel': [{'field': None,
                                                                                    'color': [255, 255, 255],
                                                                                    'size': 18,
                                                                                    'offset': [0, 0],
                                                                                    'anchor': 'start',
                                                                                    'alignment': 'center'}]},
                                                          'visualChannels': {'colorField': None,
                                                                             'colorScale': 'quantile',
                                                                             'strokeColorField': None,
                                                                             'strokeColorScale': 'quantile',
                                                                             'sizeField': None,
                                                                             'sizeScale': 'linear',
                                                                             'heightField': None,
                                                                             'heightScale': 'linear',
                                                                             'radiusField': None,
                                                                             'radiusScale': 'linear'}}],
                                              'interactionConfig': {'tooltip': {
                                                  'fieldsToShow': {'dataframe': [{'name': 'Throughput [Mbps]',
                                                                                  'format': None},
                                                                                 {'name': 'StartTime', 'format': None},
                                                                                 {'name': 'EndTime', 'format': None}],
                                                                   'shapefile': [{'name': 'DPA_DESPAR', 'format': None},
                                                                                 {'name': 'DPA_DESCAN',
                                                                                  'format': None}]},
                                                  'compareMode': False,
                                                  'compareType': 'absolute',
                                                  'enabled': True},
                                                  'brush': {'size': 0.5, 'enabled': False},
                                                  'geocoder': {'enabled': True},
                                                  'coordinate': {'enabled': True}},
                                              'layerBlending': 'additive',
                                              'splitMaps': [],
                                              'animationConfig': {'currentTime': None, 'speed': 1}},
                                 'mapState': {'bearing': 0,
                                              'dragRotate': False,
                                              'latitude': -0.15395903451561738,
                                              'longitude': -78.59933372976111,
                                              'pitch': 0,
                                              'zoom': 9.806468013004356,
                                              'isSplit': False},
                                 'mapStyle': {'styleType': 'dark',
                                              'topLayerGroups': {},
                                              'visibleLayerGroups': {'label': True,
                                                                     'road': True,
                                                                     'border': False,
                                                                     'building': True,
                                                                     'water': True,
                                                                     'land': True,
                                                                     '3d building': False},
                                              'threeDBuildingColor': [9.665468314072013,
                                                                      17.18305478057247,
                                                                      31.1442867897876],
                                              'mapStyles': {}}}}

            # Create a new KeplerGL map object
            map_1 = KeplerGl(height=400)

            # Add df_downup data as a map layer
            map_1.add_data(data=df_downup, name='dataframe')

            if self.repgen.get() or self.mapaparroquia.get():
                # Add .shp file as a map layer
                map_1.add_data(data=gdf_json, name='shapefile')

            # Customize your map layer
            map_1.config = config

        if self.repgen.get():
            # Remove the previous html file if already exist
            if os.path.exists(
                    f"{os.getenv('download_route')}/mapa_{provincia}_{canton}_{parroquia}.html"):
                os.remove(
                    f"{os.getenv('download_route')}/mapa_{provincia}_{canton}_{parroquia}.html")

            # Download the kepler map as a .html file
            map_1.save_to_html(file_name='kepler_map.html')
            os.rename('kepler_map.html',
                      f"{os.getenv('download_route')}/mapa_{provincia}_{canton}_{parroquia}.html")

        elif self.mapa.get():
            # Remove the previous html file if already exist
            if os.path.exists(
                    f"{os.getenv('download_route')}/mapa_{operadora}_{sessiontype}_{technology}_{czo}.html"):
                os.remove(f"{os.getenv('download_route')}/mapa_{operadora}_{sessiontype}_{technology}_{czo}.html")

            # Download the kepler map as a .html file
            map_1.save_to_html(file_name='kepler_map.html')
            os.rename('kepler_map.html',
                      f"{os.getenv('download_route')}/mapa_{operadora}_{sessiontype}_{technology}_{czo}.html")

        elif self.mapaparroquia.get():
            # Remove the previous html file if already exist
            if os.path.exists(
                    f"{os.getenv('download_route')}/mapa_{operadora}_{sessiontype}_{technology}_{provincia}_{canton}_{parroquia}.html"):
                os.remove(
                    f"{os.getenv('download_route')}/mapa_{operadora}_{sessiontype}_{technology}_{provincia}_{canton}_{parroquia}.html")

            # Download the kepler map as a .html file
            map_1.save_to_html(file_name='kepler_map.html')
            os.rename('kepler_map.html',
                      f"{os.getenv('download_route')}/mapa_{operadora}_{sessiontype}_{technology}_{provincia}_{canton}_{parroquia}.html")


if __name__ == "__main__":
    # Creates a new instance of the Tkinter class, which represents a main window or root window of
    # a GUI application. The variable root is commonly used to reference this root window throughout the program.
    root = tk.Tk()

    # Creates an object of the SammApp class with the root window. The SammApp class is a custom class defined in the
    # code, and the master is the root window that serves as the parent window for any widgets or components that the
    # SammApp class will create or manage.
    app = SammApp(master=root)

    # app.grid() is a method used to configure the grid layout of widgets in a tkinter GUI (Graphical User Interface)
    # application. The method arranges widgets in rows and columns, allowing them to be aligned and spaced out evenly.
    app.grid()

    # Define start_button command execution
    start_button = tk.Button(root, text="Iniciar", command=app.start)
    start_button.grid(row=12, column=0, sticky=tk.W, padx=30, pady=5)

    # Define quit_button command execution
    quit_button = tk.Button(root, text="Cerrar", command=app.quit)
    quit_button.grid(row=13, column=0, sticky=tk.W, padx=30, pady=5)

    # When root.mainloop() is called, it starts the event loop of the Tkinter application and waits for user input or
    # any event-driven inputs to occur. This method is essential in making sure that the GUI remains responsive and
    # interactive.
    root.mainloop()
