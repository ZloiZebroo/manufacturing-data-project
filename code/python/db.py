import pandas as pd
import psycopg2
import psycopg2.extras as extras
import io
import logging

logging.basicConfig(
    format='%(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%s'
)

logger = logging.getLogger(__name__)

def insert_table(df: pd.DataFrame, table: str, login: dict) -> None:

    # connection
    conn = psycopg2.connect(**login)
    conn.autocommit = False
    cursor = conn.cursor()

    # prepare data
    tuples = [tuple(x) for x in df.to_numpy()]
    cols = ', '.join(list(df.columns))

    # query
    query = f'INSERT INTO {table} ({cols}) VALUES %s'

    # safe insert
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
        logger.warning(f'Save data into {table} done | {len(df)} rows added')
    except(Exception, psycopg2.DatabaseError) as e:
        logger.warning(f'Error: {e}')
        conn.rollback()
    cursor.close()
    conn.close()

def overwrite_table(df: pd.DataFrame, table: str, login: dict) -> None:

    # connection
    conn = psycopg2.connect(**login)
    conn.autocommit = False
    cursor = conn.cursor()

    # prepare data
    tuples = [tuple(x) for x in df.to_numpy()]
    cols = ', '.join(list(df.columns))

    # query
    delete_query = f'DELETE FROM {table} *'
    query = f'INSERT INTO {table} ({cols}) VALUES %s'

    # safe insert
    try:
        cursor.execute(delete_query)
        extras.execute_values(cursor, query, tuples)
        conn.commit()
        logger.warning(f'Save data into {table} done | {len(df)} rows added')
    except (Exception, psycopg2.DatabaseError) as e:
        logger.warning(f'Error: {e}')
        conn.rollback()
    cursor.close()
    conn.close()


def query_to_df(query: str, login: dict) -> pd.DataFrame:

    # connection
    conn = psycopg2.connect(**login)
    conn.autocommit = False
    cursor = conn.cursor()

    # buffer
    buf = io.StringIO()

    # save data to buffer
    cursor.copy_expert(f'COPY ({query}) TO STDOUT WITH CSV HEADER', buf)

    # return cursor to bufer start
    buf.seek(0)

    # buf to df
    df = pd.read_csv(buf)

    # close connection
    conn.close()
    cursor.close()

    return df





