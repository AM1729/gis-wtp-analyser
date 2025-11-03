import streamlit as st
from psycopg2 import pool, sql
import os


@st.cache_resource
def get_connection_pool():
    """Create one PostgreSQL connection pool shared across all Streamlit sessions."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set.")

    pg_pool = pool.SimpleConnectionPool(
        minconn=5,    # keep a few idle connections ready
        maxconn=30,   # allow up to 30 active connections concurrently
        dsn=database_url
    )
    print("PostgreSQL connection pool created once for the app.")
    return pg_pool


class CRUD:
    """
    Class to handle CRUD operations with PostgreSQL using a shared Streamlit-safe pool.
    """

    insert_query = sql.SQL("""
        INSERT INTO survey_info (response_id, h3index, hexdistancetopark, married, municipality, education, employment, numkids, income, age, hoursWorked, visitFrequency, wtp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """)

    @classmethod
    def add_to_db(cls, payload: dict):
        """Insert or update payload in the database using the shared pool."""
        pg_pool = get_connection_pool()  # fetch the singleton pool
        conn = pg_pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(cls.insert_query, (
                    payload["response_id"],
                    payload["h3Index"],
                    payload["hexDistanceToPark"],
                    payload["married"],
                    payload["municipality"],
                    payload["education"],
                    payload["employment"],
                    payload["numkids"],
                    payload["income"],
                    payload["age"],
                    payload["hoursWorkedPerWeek"],
                    payload["visitFrequency"],
                    payload["wtp"],
                ))
            conn.commit()
        except Exception as e:
            print (e)
            conn.rollback()
            raise e
        finally:
            pg_pool.putconn(conn)

    @classmethod
    def close_pool(cls):
        """Close all connections in the pool (optional, e.g. on shutdown)."""
        pg_pool = get_connection_pool()
        pg_pool.closeall()
        print("🔒 PostgreSQL connection pool closed.")
