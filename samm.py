import os
import tkinter as tk
import tkcalendar as tc
from tkinter import messagebox
import pandas as pd
import sqlalchemy as sa
import datetime
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from keplergl import KeplerGl
from dotenv import load_dotenv

load_dotenv()


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
        self.list_of_operators = ["Claro", "CNT", "Movistar"]
        self.list_of_sessiontype = ["HTTP Download", "HTTP Post"]
        self.list_of_technology = ["LTE", "WCDMA"]
        self.list_of_czo = ["Nacional", "CZO2", "CZO3", "CZO4", "CZO5", "CZO6"]
        self.operadora = tk.StringVar()
        self.operadora.set("Claro")
        self.sessiontype = tk.StringVar()
        self.sessiontype.set("HTTP Download")
        self.technology = tk.StringVar()
        self.technology.set("LTE")
        self.czo = tk.StringVar()
        self.czo.set("Nacional")
        self.create_widgets()
        self.program_is_running = False

    def create_widgets(self):
        """Create the widges to be used with tkinter and tkcalendar"""

        self.lbl_1 = tk.Label(self.master, text="Operadora:", width=20, font=("bold", 11))
        self.lbl_1.grid(row=0, column=0, sticky=tk.W, padx=13)

        self.option_menu1 = tk.OptionMenu(self.master, self.operadora, *self.list_of_operators)
        self.option_menu1.grid(row=0, column=0, sticky=tk.W, padx=145)

        self.lbl_2 = tk.Label(self.master, text="Fecha inicio:", width=10, font=("bold", 11))
        self.lbl_2.grid(row=0, column=0, sticky=tk.W, padx=285)

        self.fecha_inicio = tc.DateEntry(self.master, selectmode='day', date_pattern='yyyy-mm-dd')
        self.fecha_inicio.grid(row=0, column=0, sticky=tk.W, padx=380)

        self.lbl_3 = tk.Label(self.master, text="Fecha fin:", width=10, font=("bold", 11))
        self.lbl_3.grid(row=0, column=0, sticky=tk.W, padx=475)

        self.fecha_fin = tc.DateEntry(self.master, selectmode='day', date_pattern='yyyy-mm-dd')
        self.fecha_fin.grid(row=0, column=0, sticky=tk.W, padx=570)

        self.lbl_4 = tk.Label(self.master, text="Hora inicio:", width=10, font=("bold", 11))
        self.lbl_4.grid(row=1, column=0, sticky=tk.W, padx=275, pady=10)

        self.tiempo_inicio = tk.Entry(self.master)
        self.tiempo_inicio.insert(0, "HH:mm")
        self.tiempo_inicio.grid(row=1, column=0, sticky=tk.W, padx=380, pady=10)

        self.lbl_5 = tk.Label(self.master, text="Hora fin:", width=10, font=("bold", 11))
        self.lbl_5.grid(row=1, column=0, sticky=tk.W, padx=475, pady=10)

        self.tiempo_fin = tk.Entry(self.master)
        self.tiempo_fin.insert(0, "HH:mm")
        self.tiempo_fin.grid(row=1, column=0, sticky=tk.W, padx=570, pady=10)

        self.lbl_6 = tk.Label(self.master, text="Tipo de Sesión:", width=20, font=("bold", 11))
        self.lbl_6.grid(row=1, column=0, sticky=tk.W)

        self.option_menu2 = tk.OptionMenu(self.master, self.sessiontype, *self.list_of_sessiontype)
        self.option_menu2.grid(row=1, column=0, sticky=tk.W, padx=145)

        self.lbl_7 = tk.Label(self.master, text="Tecnología:", width=20, font=("bold", 11))
        self.lbl_7.grid(row=2, column=0, sticky=tk.W, padx=12)

        self.option_menu3 = tk.OptionMenu(self.master, self.technology, *self.list_of_technology)
        self.option_menu3.grid(row=2, column=0, sticky=tk.W, padx=145)

        self.lbl_8 = tk.Label(self.master, text="CZO:", width=20, font=("bold", 11))
        self.lbl_8.grid(row=3, column=0, sticky=tk.W, padx=32)

        self.option_menu4 = tk.OptionMenu(self.master, self.czo, *self.list_of_czo)
        self.option_menu4.grid(row=3, column=0, sticky=tk.W, padx=145)

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
        operadora = self.operadora.get()
        sessiontype = self.sessiontype.get()
        technology = self.technology.get()
        czo = self.czo.get()
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

        # Define the SQL querys to be executed
        sql_query1 = f"SELECT DatasourceId, SessionIdOrCallIndex, SessionType, StartTime, StartLatitude, " \
                     f"StartLongitude, StartRadioTechnology, EndTime, EndLatitude, EndLongitude, EndRadioTechnology, " \
                     f"SimOperator, IMSI, IMEI, SessionEndStatus FROM {os.getenv('TABLE1')} " \
                     f"WHERE StartTime >= '{fecha_inicio}' AND EndTime <= '{fecha_fin}' " \
                     f"AND SessionType = '{sessiontype}' AND StartRadioTechnology = '{technology}' " \
                     f"AND EndRadioTechnology = '{technology}' AND SimOperator = '{operadora}';"
        sql_query2 = f"SELECT DatasourceId, SessionId, SessionType, StartDateTime, EndDateTime, Url, " \
                     f"EndServiceBearer, EndDataRadioBearer, EndFileSize, EndServiceStatus, " \
                     f"IPServiceSetupTimeMethodAMethod, DataTransferTimeMethodADuration " \
                     f"FROM {os.getenv('TABLE2')} WHERE StartDateTime >= '{fecha_inicio}' " \
                     f"AND EndDateTime <= '{fecha_fin}' AND SessionType = '{sessiontype}';"

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
                return (float(row['EndFileSize']) * 8) / total_seconds / 1000000
            else:
                return None

        # Create a new column with the throughput value
        df['ThroughputMbps'] = df.apply(lambda row: throughput(row), axis=1)
        # Round the values in the new column to 1 decimal
        df['ThroughputMbps'] = df['ThroughputMbps'].round(1)

        # Filter the df by the selected parameters
        df = df.loc[df['SimOperator'] == f'{operadora}']
        df = df.loc[df['EndServiceStatus'] == 'Succeeded']
        df = df.loc[df['SessionType'] == f'{sessiontype}']
        df = df.loc[df['StartRadioTechnology'] == f'{technology}']
        df = df.loc[df['EndRadioTechnology'] == f'{technology}']
        if czo != 'Nacional':
            df = df.loc[df['CZO'] == f'{czo}']

        # Drop rows with NaN values in the following columns
        df = df.dropna(subset=['StartLatitude', 'StartLongitude', 'EndLatitude', 'EndLongitude', 'ThroughputMbps'])

        # Pass the df to a .csv file
        df.to_csv(f'SessionSummary_{operadora}_{sessiontype}_{technology}_{czo}.csv', index=False, sep=';',
                  encoding='utf-8',
                  header=True, decimal=',')

        # Remove the previous files if already exist
        if os.path.exists(
                f"{os.getenv('download_route')}/SessionSummary_{operadora}_{sessiontype}_{technology}_{czo}.csv"):
            os.remove(f"{os.getenv('download_route')}/SessionSummary_{operadora}_{sessiontype}_{technology}_{czo}.csv")

        # Download the .csv file
        os.rename(f'SessionSummary_{operadora}_{sessiontype}_{technology}_{czo}.csv',
                  f"{os.getenv('download_route')}/SessionSummary_{operadora}_{sessiontype}_{technology}_{czo}.csv")

        # Create de dataframes to be used for the map and the configuration for the map
        df_downup = df
        if sessiontype == 'HTTP Download':
            df_downup = df[['StartLatitude', 'StartLongitude', 'EndLatitude', 'EndLongitude', 'ThroughputMbps']]
            df_downup = df_downup.rename(columns={'ThroughputMbps': 'Download [Mbps]'})
            config = {'version': 'v1',
                      'config': {'visState': {'filters': [{'dataId': ['data_1'],
                                                           'id': 'z86qtmndf',
                                                           'name': ['Download [Mbps]'],
                                                           'type': 'range',
                                                           'value': [0, 49.54],
                                                           'enlarged': False,
                                                           'plotType': 'histogram',
                                                           'animationWindow': 'free',
                                                           'yAxis': None,
                                                           'speed': 1}],
                                              'layers': [{'id': 'cz8glzu',
                                                          'type': 'point',
                                                          'config': {'dataId': 'data_1',
                                                                     'label': 'Inicio',
                                                                     'color': [18, 147, 154],
                                                                     'highlightColor': [252, 242, 26, 255],
                                                                     'columns': {'lat': 'StartLatitude',
                                                                                 'lng': 'StartLongitude',
                                                                                 'altitude': 'Download [Mbps]'},
                                                                     'isVisible': True,
                                                                     'visConfig': {'radius': 10,
                                                                                   'fixedRadius': False,
                                                                                   'opacity': 0.3,
                                                                                   'outline': False,
                                                                                   'thickness': 2,
                                                                                   'strokeColor': None,
                                                                                   'colorRange': {
                                                                                       'name': 'Uber Viz Qualitative 1',
                                                                                       'type': 'qualitative',
                                                                                       'category': 'Uber',
                                                                                       'colors': ['#12939A', '#DDB27C',
                                                                                                  '#88572C', '#FF991F',
                                                                                                  '#F15C17']},
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
                                                          'visualChannels': {'colorField': {'name': 'Download [Mbps]',
                                                                                            'type': 'real'},
                                                                             'colorScale': 'quantize',
                                                                             'strokeColorField': None,
                                                                             'strokeColorScale': 'quantile',
                                                                             'sizeField': {'name': 'Download [Mbps]',
                                                                                           'type': 'real'},
                                                                             'sizeScale': 'sqrt'}},
                                                         {'id': 'yicfhk',
                                                          'type': 'point',
                                                          'config': {'dataId': 'data_1',
                                                                     'label': 'Fin',
                                                                     'color': [221, 178, 124],
                                                                     'highlightColor': [252, 242, 26, 255],
                                                                     'columns': {'lat': 'EndLatitude',
                                                                                 'lng': 'EndLongitude',
                                                                                 'altitude': 'Download [Mbps]'},
                                                                     'isVisible': True,
                                                                     'visConfig': {'radius': 10,
                                                                                   'fixedRadius': False,
                                                                                   'opacity': 0.3,
                                                                                   'outline': False,
                                                                                   'thickness': 2,
                                                                                   'strokeColor': None,
                                                                                   'colorRange': {
                                                                                       'name': 'Uber Viz Qualitative 1',
                                                                                       'type': 'qualitative',
                                                                                       'category': 'Uber',
                                                                                       'colors': ['#12939A', '#DDB27C',
                                                                                                  '#88572C', '#FF991F',
                                                                                                  '#F15C17']},
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
                                                          'visualChannels': {'colorField': {'name': 'Download [Mbps]',
                                                                                            'type': 'real'},
                                                                             'colorScale': 'quantize',
                                                                             'strokeColorField': None,
                                                                             'strokeColorScale': 'quantile',
                                                                             'sizeField': {'name': 'Download [Mbps]',
                                                                                           'type': 'real'},
                                                                             'sizeScale': 'sqrt'}},
                                                         {'id': 'v2chyjo',
                                                          'type': 'arc',
                                                          'config': {'dataId': 'data_1',
                                                                     'label': 'Arco',
                                                                     'color': [218, 0, 0],
                                                                     'highlightColor': [252, 242, 26, 255],
                                                                     'columns': {'lat0': 'StartLatitude',
                                                                                 'lng0': 'StartLongitude',
                                                                                 'lat1': 'EndLatitude',
                                                                                 'lng1': 'EndLongitude'},
                                                                     'isVisible': True,
                                                                     'visConfig': {'opacity': 0.3,
                                                                                   'thickness': 2,
                                                                                   'colorRange': {
                                                                                       'name': 'Global Warming',
                                                                                       'type': 'sequential',
                                                                                       'category': 'Uber',
                                                                                       'colors': ['#5A1846',
                                                                                                  '#900C3F',
                                                                                                  '#C70039',
                                                                                                  '#E3611C',
                                                                                                  '#F1920E',
                                                                                                  '#FFC300']},
                                                                                   'sizeRange': [0, 10],
                                                                                   'targetColor': None},
                                                                     'hidden': False,
                                                                     'textLabel': [{'field': None,
                                                                                    'color': [255, 255, 255],
                                                                                    'size': 18,
                                                                                    'offset': [0, 0],
                                                                                    'anchor': 'start',
                                                                                    'alignment': 'center'}]},
                                                          'visualChannels': {'colorField': None,
                                                                             'colorScale': 'quantile',
                                                                             'sizeField': {'name': 'Download [Mbps]',
                                                                                           'type': 'real'},
                                                                             'sizeScale': 'linear'}}],
                                              'interactionConfig': {
                                                  'tooltip': {'fieldsToShow': {'data_1': [{'name': 'Download [Mbps]',
                                                                                           'format': None}]},
                                                              'compareMode': True,
                                                              'compareType': 'absolute',
                                                              'enabled': True},
                                                  'brush': {'size': 0.5, 'enabled': False},
                                                  'geocoder': {'enabled': True},
                                                  'coordinate': {'enabled': True}},
                                              'layerBlending': 'normal',
                                              'splitMaps': [],
                                              'animationConfig': {'currentTime': None, 'speed': 1}},
                                 'mapState': {'bearing': 0,
                                              'dragRotate': False,
                                              'latitude': -0.13373389164255878,
                                              'longitude': -78.51443035343762,
                                              'pitch': 0,
                                              'zoom': 11.189030754951633,
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
        elif sessiontype == 'HTTP Post':
            df_downup = df[['StartLatitude', 'StartLongitude', 'EndLatitude', 'EndLongitude', 'ThroughputMbps']]
            df_downup = df_downup.rename(columns={'ThroughputMbps': 'Upload [Mbps]'})
            config = {'version': 'v1',
                      'config': {'visState': {'filters': [{'dataId': ['data_1'],
                                                           'id': 'z86qtmndf',
                                                           'name': ['Upload [Mbps]'],
                                                           'type': 'range',
                                                           'value': [0, 49.54],
                                                           'enlarged': False,
                                                           'plotType': 'histogram',
                                                           'animationWindow': 'free',
                                                           'yAxis': None,
                                                           'speed': 1}],
                                              'layers': [{'id': 'cz8glzu',
                                                          'type': 'point',
                                                          'config': {'dataId': 'data_1',
                                                                     'label': 'Inicio',
                                                                     'color': [18, 147, 154],
                                                                     'highlightColor': [252, 242, 26, 255],
                                                                     'columns': {'lat': 'StartLatitude',
                                                                                 'lng': 'StartLongitude',
                                                                                 'altitude': 'Upload [Mbps]'},
                                                                     'isVisible': True,
                                                                     'visConfig': {'radius': 10,
                                                                                   'fixedRadius': False,
                                                                                   'opacity': 0.3,
                                                                                   'outline': False,
                                                                                   'thickness': 2,
                                                                                   'strokeColor': None,
                                                                                   'colorRange': {
                                                                                       'name': 'Uber Viz Qualitative 1',
                                                                                       'type': 'qualitative',
                                                                                       'category': 'Uber',
                                                                                       'colors': ['#12939A', '#DDB27C',
                                                                                                  '#88572C', '#FF991F',
                                                                                                  '#F15C17']},
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
                                                          'visualChannels': {'colorField': {'name': 'Upload [Mbps]',
                                                                                            'type': 'real'},
                                                                             'colorScale': 'quantize',
                                                                             'strokeColorField': None,
                                                                             'strokeColorScale': 'quantile',
                                                                             'sizeField': {'name': 'Upload [Mbps]',
                                                                                           'type': 'real'},
                                                                             'sizeScale': 'sqrt'}},
                                                         {'id': 'yicfhk',
                                                          'type': 'point',
                                                          'config': {'dataId': 'data_1',
                                                                     'label': 'Fin',
                                                                     'color': [221, 178, 124],
                                                                     'highlightColor': [252, 242, 26, 255],
                                                                     'columns': {'lat': 'EndLatitude',
                                                                                 'lng': 'EndLongitude',
                                                                                 'altitude': 'Upload [Mbps]'},
                                                                     'isVisible': True,
                                                                     'visConfig': {'radius': 10,
                                                                                   'fixedRadius': False,
                                                                                   'opacity': 0.3,
                                                                                   'outline': False,
                                                                                   'thickness': 2,
                                                                                   'strokeColor': None,
                                                                                   'colorRange': {
                                                                                       'name': 'Uber Viz Qualitative 1',
                                                                                       'type': 'qualitative',
                                                                                       'category': 'Uber',
                                                                                       'colors': ['#12939A', '#DDB27C',
                                                                                                  '#88572C', '#FF991F',
                                                                                                  '#F15C17']},
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
                                                          'visualChannels': {'colorField': {'name': 'Upload [Mbps]',
                                                                                            'type': 'real'},
                                                                             'colorScale': 'quantize',
                                                                             'strokeColorField': None,
                                                                             'strokeColorScale': 'quantile',
                                                                             'sizeField': {'name': 'Upload [Mbps]',
                                                                                           'type': 'real'},
                                                                             'sizeScale': 'sqrt'}},
                                                         {'id': 'v2chyjo',
                                                          'type': 'arc',
                                                          'config': {'dataId': 'data_1',
                                                                     'label': 'Arco',
                                                                     'color': [218, 0, 0],
                                                                     'highlightColor': [252, 242, 26, 255],
                                                                     'columns': {'lat0': 'StartLatitude',
                                                                                 'lng0': 'StartLongitude',
                                                                                 'lat1': 'EndLatitude',
                                                                                 'lng1': 'EndLongitude'},
                                                                     'isVisible': True,
                                                                     'visConfig': {'opacity': 0.3,
                                                                                   'thickness': 2,
                                                                                   'colorRange': {
                                                                                       'name': 'Global Warming',
                                                                                       'type': 'sequential',
                                                                                       'category': 'Uber',
                                                                                       'colors': ['#5A1846',
                                                                                                  '#900C3F',
                                                                                                  '#C70039',
                                                                                                  '#E3611C',
                                                                                                  '#F1920E',
                                                                                                  '#FFC300']},
                                                                                   'sizeRange': [0, 10],
                                                                                   'targetColor': None},
                                                                     'hidden': False,
                                                                     'textLabel': [{'field': None,
                                                                                    'color': [255, 255, 255],
                                                                                    'size': 18,
                                                                                    'offset': [0, 0],
                                                                                    'anchor': 'start',
                                                                                    'alignment': 'center'}]},
                                                          'visualChannels': {'colorField': None,
                                                                             'colorScale': 'quantile',
                                                                             'sizeField': {'name': 'Upload [Mbps]',
                                                                                           'type': 'real'},
                                                                             'sizeScale': 'linear'}}],
                                              'interactionConfig': {
                                                  'tooltip': {'fieldsToShow': {'data_1': [{'name': 'Upload [Mbps]',
                                                                                           'format': None}]},
                                                              'compareMode': True,
                                                              'compareType': 'absolute',
                                                              'enabled': True},
                                                  'brush': {'size': 0.5, 'enabled': False},
                                                  'geocoder': {'enabled': True},
                                                  'coordinate': {'enabled': True}},
                                              'layerBlending': 'normal',
                                              'splitMaps': [],
                                              'animationConfig': {'currentTime': None, 'speed': 1}},
                                 'mapState': {'bearing': 0,
                                              'dragRotate': False,
                                              'latitude': -0.13373389164255878,
                                              'longitude': -78.51443035343762,
                                              'pitch': 0,
                                              'zoom': 11.189030754951633,
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

        # Add the data to KeplerGl map
        map_1 = KeplerGl(height=400, data={"data_1": df_downup}, config=config)

        # Remove the previous html file if already exist
        if os.path.exists(
                f"{os.getenv('download_route')}/kepler_map_{operadora}_{sessiontype}_{technology}_{czo}.html"):
            os.remove(f"{os.getenv('download_route')}/kepler_map_{operadora}_{sessiontype}_{technology}_{czo}.html")

        # Download the kepler map as a .html file
        map_1.save_to_html(file_name='kepler_map.html')
        os.rename('kepler_map.html',
                  f"{os.getenv('download_route')}/kepler_map_{operadora}_{sessiontype}_{technology}_{czo}.html")


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
