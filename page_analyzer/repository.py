"""
DB functions
"""

import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


class GetCursor:
    """
    Creates DB connection and returns cursor
    At exit, closes cursor and DB connection
    """
    def __init__(self, db_url, cursor_factory=None):
        """
        Saves db_url and cursor_factory values
        """
        self.db_url = db_url
        self.cursor_factory = cursor_factory

    def __enter__(self):
        """
        Creates DB connection and returns cursor
        """
        self.conn = psycopg2.connect(self.db_url, sslmode="disable")
        self.cursor = self.conn.cursor(cursor_factory=self.cursor_factory)
        return self.cursor
        
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Performs commit and closes cursor and DB connection
        """
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        return False


class SitesRepository:
    """
    Page analyzer DB functions
    """
    def __init__(self):
        """
        SitesRepository initialization
        Created DB connection
        """
        self.conn = psycopg2.connect(DATABASE_URL, sslmode="disable")

    def get_sites(self):
        """
        Returns list of sites
        Last added goes first
        """
        with GetCursor(DATABASE_URL, RealDictCursor) as cur:
            cur.execute("""
                SELECT DISTINCT ON (u.created_at, u.id) 
                u.id, u.name, u.created_at::date as created_at,
                c.status_code as last_check_status, 
                c.created_at::date as last_check_date
                FROM pa.urls u
                LEFT JOIN pa.url_checks c ON c.url_id = u.id
                ORDER BY u.created_at DESC, u.id DESC, c.created_at DESC;"""
            )

            return [dict(row) for row in cur]

    def get_checks(self, url_id):
        """
        Returns list of checks for url_id
        Last added goes first
        """
        with GetCursor(DATABASE_URL, RealDictCursor) as cur:
            cur.execute("""SELECT c.id, c.status_code, c.h1, c.title,
                            c.description, c.created_at::date
                        FROM pa.url_checks c 
                        WHERE c.url_id = %s
                        ORDER BY c.created_at DESC
                        """, (url_id,))

            return [dict(row) for row in cur]

    def find(self, name):
        """
        Returns site by it's URL (name)
        None if not found
        """
        with GetCursor(DATABASE_URL, RealDictCursor) as cur:
            cur.execute("SELECT * FROM pa.urls WHERE name = %s", (name,))
            row = cur.fetchone()

        return dict(row) if row else None

    def get_by_id(self, url_id):
        """
        Returns site by it's ID
        None if not found
        """
        with GetCursor(DATABASE_URL, RealDictCursor) as cur:
            cur.execute("""SELECT u.id, u.name, u.created_at::date
            FROM pa.urls u WHERE id = %s""", (url_id,))
            row = cur.fetchone()

        return dict(row) if row else None

    def add_site(self, url):
        """
        Adds new site
        returns site.id
        """
        with GetCursor(DATABASE_URL) as cur:
            cur.execute(
                """INSERT INTO pa.urls (name) VALUES
                (%s) RETURNING id, created_at""",
                (url, )
            )
            row = cur.fetchone()

        return {"id": row[0], "name": url, "created_at": row[1]}

    def add_check(self, url_id, status_code, h1, title, description):
        """
        Adds new site check
        returns check.id
        """
        with GetCursor(DATABASE_URL) as cur:
            cur.execute(
                """INSERT INTO pa.url_checks
                (url_id, status_code, h1, title, description) 
                VALUES(%s, %s, %s, %s, %s)
                RETURNING id, created_at""",
                (url_id, status_code, h1, title, description)
            )
            row = cur.fetchone()

        return {
            "id": row[0],
            "url_id": url_id,
            "status_code": status_code,
            "h1": h1,
            "title": title,
            "description": description,
        }
