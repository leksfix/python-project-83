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
    def __init__(self):
        self.conn = psycopg.connect(DATABASE_URL)

    def list_sites(self):
        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
WITH last_check AS (
  SELECT url_id, last_check_resp, last_check_date
  FROM
  (
    SELECT c.url_id, 
      FIRST_VALUE(c.resp_code) OVER w as last_check_resp,
      FIRST_VALUE(c.created_at) OVER w as last_check_date,
      ROW_NUMBER() OVER w as rn
    FROM pa.url_checks c
    WINDOW w AS (
      PARTITION BY c.url_id ORDER BY c.created_at DESC
    )    
  ) l WHERE rn = 1
)
SELECT u.id, u.name, u.created_at::date, 
  l.last_check_resp, l.last_check_date::date
FROM pa.urls u
LEFT JOIN last_check l ON l.url_id = u.id
ORDER BY u.created_at DESC
                        """)
            return [dict(row) for row in cur]

    def list_checks(self, id):
        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""SELECT c.id, c.resp_code, c.h1, c.title, 
                            c.description, c.created_at::date
                        FROM pa.url_checks c 
                        WHERE c.url_id = %s
                        ORDER BY created_at DESC
                        """, (id,))
            return [dict(row) for row in cur]

    def find(self, name):
        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM pa.urls WHERE name = %s", (name,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_by_id(self, id):
        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""SELECT u.id, u.name, u.created_at::date
            FROM pa.urls u WHERE id = %s""", (id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def save(self, site):
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
