import os
import tkinter as tk
import tkcalendar as tc
from tkinter import messagebox
import pandas as pd
import datetime
import sqlalchemy as sa
from sqlalchemy.engine import URL
from sqlalchemy import create_engine

# Select download route
download_route = 'C:/Users/isuarez/Downloads'

# SERVER Information
DRIVER_NAME = 'ODBC Driver 11 for SQL Server'
SERVER_NAME = '172.20.1.220\SQL2014'
DATABASE_NAME = 'AnalyticsMeasDB'
TABLE1 = 'cdr.SessionSummary'
TABLE2 = 'cdr.SessionSummaryData'


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

        self.RepGen = tk.BooleanVar()
        self.create_widgets()
        self.program_is_running = False

    def create_widgets(self):
        """Create the widges to be used with tkinter and tkcalendar"""

        self.lbl_3 = tk.Label(self.master, text="Fecha inicio:", width=10, font=("bold", 11))
        self.lbl_3.grid(row=0, column=0, sticky=tk.W, padx=250)

        self.fecha_inicio = tc.DateEntry(self.master, selectmode='day', date_pattern='yyyy-mm-dd')
        self.fecha_inicio.grid(row=0, column=0, sticky=tk.W, padx=355)

        self.lbl_4 = tk.Label(self.master, text="Fecha fin:", width=10, font=("bold", 11))
        self.lbl_4.grid(row=0, column=0, sticky=tk.W, padx=450)

        self.fecha_fin = tc.DateEntry(self.master, selectmode='day', date_pattern='yyyy-mm-dd')
        self.fecha_fin.grid(row=0, column=0, sticky=tk.W, padx=545)

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
        fecha_inicio = self.fecha_inicio.get_date().strftime("%Y-%m-%d")
        fecha_fin = self.fecha_fin.get_date().strftime("%Y-%m-%d")

        # Add HH:MM:SS to fecha_inicio and fecha_fin so the range of dates we want to show in the report is correct
        # (reminder: the dates we enter in the form is just a string with format 2022-01-12, that is why we made this
        # change to not lose information when we present the data at the end)
        add_string1 = ' 00:00:01'
        add_string2 = ' 23:59:59'
        fecha_inicio += add_string1
        fecha_fin += add_string2

        def convert(date_time):
            """function to convert a string to datetime object"""
            format = '%Y-%m-%d %H:%M:%S'  # The format
            datetime_str = datetime.datetime.strptime(date_time, format)
            return datetime_str

        # Convert fecha_inicio and fecha_fin to datetime object
        fecha_inicio = convert(fecha_inicio)
        fecha_fin = convert(fecha_fin)

        # Define the SQL query
        sql_query1 = f"SELECT DatasourceId, SessionIdOrCallIndex, SessionType, StartTime, StartLatitude, StartLongitude, " \
                     f"StartRadioTechnology, EndTime, EndLatitude, EndLongitude, EndRadioTechnology, SimOperator, IMSI, " \
                     f"IMEI, SessionEndStatus FROM {TABLE1} WHERE StartTime BETWEEN '{fecha_inicio}' AND '{fecha_fin}';"
        sql_query2 = f"SELECT DatasourceId, SessionId, SessionType, StartDateTime, EndDateTime, EndServiceBearer, " \
                     f"EndDataRadioBearer, EndFileSize, EndServiceStatus, IPServiceSetupTimeMethodAMethod, " \
                     f"DataTransferTimeMethodADuration FROM {TABLE2} WHERE StartDateTime >= '{fecha_inicio}' " \
                     f"AND StartDateTime <= '{fecha_fin}';"

        try:
            # Create the engine according to SQLAlchemy documentation
            connection_string = f"DRIVER={DRIVER_NAME};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};Trusted_Connection=yes;"
            connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
            engine = create_engine(connection_url)

            # Establish a connection to the database, execute the query and create the df with the results
            with engine.begin() as conn:
                df1 = pd.read_sql_query(sa.text(sql_query1), conn)
                df2 = pd.read_sql_query(sa.text(sql_query2), conn)

            # Close the connection object
            conn.close()

        except Exception as e:
            print('Database connection failed.')

        # Pass the df to a .csv file
        df1.to_csv('SessionSummary.csv', index=False, sep=';', encoding='utf-8', header=True)
        df2.to_csv('SessionSummaryData.csv', index=False, sep=';', encoding='utf-8', header=True)

        # Remove the previous files if already exist
        if os.path.exists(f'{download_route}/SessionSummary.csv'):
            os.remove(f'{download_route}/SessionSummary.csv')

        if os.path.exists(f'{download_route}/SessionSummaryData.csv'):
            os.remove(f'{download_route}/SessionSummaryData.csv')

        # Download the .csv file
        os.rename('SessionSummary.csv', f'{download_route}/SessionSummary.csv')
        os.rename('SessionSummaryData.csv', f'{download_route}/SessionSummaryData.csv')


if __name__ == "__main__":
    """Creates a new instance of the Tkinter class, which represents a main window or root window of
    a GUI application. The variable root is commonly used to reference this root window throughout the program."""
    root = tk.Tk()

    """Creates an object of the SacerApp class with the root window. The SacerApp class is a custom class defined in the
    code, and the master is the root window that serves as the parent window for any widgets or components that the
    SacerApp class will create or manage."""
    app = SammApp(master=root)

    """app.grid() is a method used to configure the grid layout of widgets in a tkinter GUI (Graphical User Interface)
    application. The method arranges widgets in rows and columns, allowing them to be aligned and spaced out evenly."""
    app.grid()

    """Define start_button command execution"""
    start_button = tk.Button(root, text="Iniciar", command=app.start)
    start_button.grid(row=12, column=0, sticky=tk.W, padx=30, pady=5)

    """Define quit_button command execution"""
    quit_button = tk.Button(root, text="Cerrar", command=app.quit)
    quit_button.grid(row=13, column=0, sticky=tk.W, padx=30, pady=5)

    """When root.mainloop() is called, it starts the event loop of the Tkinter application and waits for user input or
    any event-driven inputs to occur. This method is essential in making sure that the GUI remains responsive and
    interactive."""
    root.mainloop()
