"""
DB functions
"""

import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


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
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                WITH last_check AS (
                SELECT url_id, last_check_status, last_check_date
                FROM
                (
                    SELECT c.url_id, 
                    FIRST_VALUE(c.status_code) OVER w as last_check_status,
                    FIRST_VALUE(c.created_at) OVER w as last_check_date,
                    ROW_NUMBER() OVER w as rn
                    FROM pa.url_checks c
                    WINDOW w AS (
                    PARTITION BY c.url_id ORDER BY c.created_at DESC
                    )    
                ) l WHERE rn = 1
                )
                SELECT u.id, u.name, u.created_at::date, 
                l.last_check_status, l.last_check_date::date
                FROM pa.urls u
                LEFT JOIN last_check l ON l.url_id = u.id
                ORDER BY u.created_at DESC
            """)
            self.conn.commit()
            
            return [dict(row) for row in cur]

    def get_checks(self, url_id):
        """
        Returns list of checks for url_id
        Last added goes first
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
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
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM pa.urls WHERE name = %s", (name,))
            row = cur.fetchone()

            return dict(row) if row else None

    def get_by_id(self, url_id):
        """
        Returns site by it's ID
        None if not found
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""SELECT u.id, u.name, u.created_at::date
            FROM pa.urls u WHERE id = %s""", (url_id,))
            row = cur.fetchone()

            return dict(row) if row else None

    def add_site(self, url):
        """
        Adds new site
        returns site.id
        """
        with self.conn.cursor() as cur:
            cur.execute(
                """INSERT INTO pa.urls (name) VALUES
                (%s) RETURNING id, created_at""",
                (url, )
            )
            row = cur.fetchone()
            self.conn.commit()
        return {"id": row[0], "name": url, "created_at": row[1]}

    def add_check(self, url_id, status_code, h1, title, description):
        """
        Adds new site check
        returns check.id
        """
        with self.conn.cursor() as cur:
            cur.execute(
                """INSERT INTO pa.url_checks
                (url_id, status_code, h1, title, description) 
                VALUES(%s, %s, %s, %s, %s)
                RETURNING id, created_at""",
                (url_id, status_code, h1, title, description)
            )
            row = cur.fetchone()
            self.conn.commit()
        return {"id": row[0], "url_id": url_id, "status_code": status_code,
                "h1": h1, "title": title, "description": description
        }
