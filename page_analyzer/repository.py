"""
DB functions
"""

import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

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
        self.conn = psycopg.connect(DATABASE_URL, sslmode="disable")

    def list_sites(self):
        """
        Returns list of sites
        Last added goes first
        """
        with self.conn.cursor(row_factory=dict_row) as cur:
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

    def list_checks(self, url_id):
        """
        Returns list of checks for url_id
        Last added goes first
        """
        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""SELECT c.id, c.status_code, c.h1, c.title,
                            c.description, c.created_at::date
                        FROM pa.url_checks c 
                        WHERE c.url_id = %s
                        ORDER BY c.created_at DESC
                        """, (url_id,))
            self.conn.commit()
            return [dict(row) for row in cur]

    def find(self, name):
        """
        Returns site by it's URL (name)
        None if not found
        """
        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM pa.urls WHERE name = %s", (name,))
            row = cur.fetchone()
            self.conn.commit()
            return dict(row) if row else None

    def get_by_id(self, url_id):
        """
        Returns site by it's ID
        None if not found
        """
        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""SELECT u.id, u.name, u.created_at::date
            FROM pa.urls u WHERE id = %s""", (url_id,))
            row = cur.fetchone()
            self.conn.commit()
            return dict(row) if row else None

    def save_site(self, site):
        """
        Adds new site
        returns site.id
        """
        if 'id' not in site or not site['id']:
            with self.conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO pa.urls (name) VALUES
                    (%s) RETURNING id, created_at""",
                    (site['name'], )
                )
                row = cur.fetchone()
                site['id'] = row[0]
                site['created_at'] = row[1]
            self.conn.commit()

    def save_check(self, check):
        """
        Adds new site check
        returns check.id
        """
        if 'id' not in check or not check['id']:
            with self.conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO pa.url_checks
                    (url_id, status_code, h1, title, description) 
                    VALUES(%s, %s, %s, %s, %s)
                    RETURNING id, created_at""",
                    (check.get('url_id'), check.get('status_code'), check.get('h1'),
                     check.get('title'), check.get('description')
                     )
                )
                row = cur.fetchone()
                check['id'] = row[0]
                check['created_at'] = row[1]
            self.conn.commit()
