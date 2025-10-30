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
        INSERT INTO people_info (h3index, hexdistancetopark, married, education, employment, numkids, income)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (h3index) DO UPDATE
        SET hexdistancetopark = EXCLUDED.hexdistancetopark,
            married = EXCLUDED.married,
            education = EXCLUDED.education,
            employment = EXCLUDED.employment,
            numkids = EXCLUDED.numkids,
            income = EXCLUDED.income;
    """)

    @classmethod
    def add_to_db(cls, payload: dict):
        """Insert or update payload in the database using the shared pool."""
        pg_pool = get_connection_pool()  # fetch the singleton pool
        conn = pg_pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(cls.insert_query, (
                    payload["h3Index"],
                    payload["hexDistanceToPark"],
                    payload["married"],
                    payload["education"],
                    payload["employment"],
                    payload["numKids"],
                    payload["income"]
                ))
            conn.commit()
        except Exception as e:
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
