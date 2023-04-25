import os
import pandas as pd
import sqlalchemy as sa
from sqlalchemy.engine import URL
from sqlalchemy import create_engine

"""Select download route"""
download_route = 'C:/Users/isuarez/Downloads'

"""SERVER Information"""
DRIVER_NAME = 'ODBC Driver 11 for SQL Server'
SERVER_NAME = '172.20.1.220\SQL2014'
DATABASE_NAME = 'AnalyticsMeasDB'
TABLE1 = 'cdr.SessionSummary'
TABLE2 = 'cdr.SessionSummaryData'

start_date = '2022-07-18 00:00:00.001'
end_date = '2022-07-22 23:59:59.999'

# Define the SQL query
sql_query1 = f"SELECT DatasourceId, SessionIdOrCallIndex, SessionType, StartTime, StartLatitude, StartLongitude, " \
             f"StartRadioTechnology, EndTime, EndLatitude, EndLongitude, EndRadioTechnology, SimOperator, IMSI, " \
             f"IMEI, SessionEndStatus FROM {TABLE1} WHERE StartTime BETWEEN '{start_date}' AND '{end_date}';"
sql_query2 = f"SELECT DatasourceId, SessionId, SessionType, StartDateTime, EndDateTime, EndServiceBearer, " \
             f"EndDataRadioBearer, EndFileSize, EndServiceStatus, IPServiceSetupTimeMethodAMethod, " \
             f"DataTransferTimeMethodADuration FROM {TABLE2} WHERE StartDateTime >= '{start_date}' " \
             f"AND StartDateTime <= '{end_date}';"

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
df1.to_csv('data1.csv', index=False, sep=';', encoding='utf-8', header=True)
df2.to_csv('data2.csv', index=False, sep=';', encoding='utf-8', header=True)

# Download the .csv file
os.rename('data1.csv', f'{download_route}/data1.csv')
os.rename('data2.csv', f'{download_route}/data2.csv')
