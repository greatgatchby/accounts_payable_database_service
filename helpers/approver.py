import pymysql
from helpers.config import connect
import uuid

class Approver:
    def __init__(self, id=None, level=None, approver=None, hierarchy_id=None):
        self.conn = connect()
        self.id = id if id else str(uuid.uuid4())
        self.level = level
        self.approver = approver
        self.hierarchy_id = hierarchy_id

    def create(self, created_at=None):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                INSERT INTO approver (id, level, approver, hierarchy_id, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (self.id, self.level, self.approver, self.hierarchy_id, created_at))
            self.conn.commit()

    def read(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT * FROM approver WHERE id = %s", (self.id,))
            result = cur.fetchone()

        return result

    def read_all(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT * FROM approver WHERE hierarchy_id = %s", (self.hierarchy_id,))
            result = cur.fetchall()

        return result

    def update(self, level=None, approver=None, hierarchy_id=None, created_at=None):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            query = "UPDATE approver SET "
            params = []
            if level is not None:
                query += "level = %s, "
                params.append(level)
            if approver is not None:
                query += "approver = %s, "
                params.append(approver)
            if hierarchy_id is not None:
                query += "hierarchy_id = %s, "
                params.append(hierarchy_id)
            if created_at is not None:
                query += "created_at = %s, "
                params.append(created_at)

            # Remove trailing comma and space
            query = query[:-2]

            query += " WHERE id = %s"
            params.append(self.id)

            cur.execute(query, tuple(params))
            self.conn.commit()

    def delete(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("DELETE FROM approver WHERE id = %s", (self.id,))
            self.conn.commit()
