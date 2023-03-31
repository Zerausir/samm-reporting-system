import pandas as pd
import sqlalchemy as sa
from sqlalchemy.engine import URL
from sqlalchemy import create_engine

DRIVER_NAME = 'ODBC Driver 11 for SQL Server'
SERVER_NAME = '172.20.1.220\SQL2014'
DATABASE_NAME = '8_CZO2'
TABLE = 'dbo.Script_ResultMetric_TEMS_Service_KPIs_HTTP'

# Define the SQL query
sql_query = f'SELECT TOP 100 * FROM {TABLE};'

try:
    # Create the engine according to SQLAlchemy documentation
    connection_string = f"DRIVER={DRIVER_NAME};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};Trusted_Connection=yes;"
    connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
    engine = create_engine(connection_url)

    # Establish a connection to the database, execute the query and create the df with the results
    with engine.begin() as conn:
        df = pd.read_sql_query(sa.text(sql_query), conn)

    # Close the connection object
    conn.close()

    # Print df to see the content of df
    print(df)

except Exception as e:
    print('Database connection failed.')
