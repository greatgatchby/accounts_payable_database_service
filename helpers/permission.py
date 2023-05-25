import pymysql

from helpers.config import connect
import uuid


class Permission:
    def __init__(self, id=None):
        self.conn = connect()
        self.id = id if id else str(uuid.uuid4())

    def create(self, permission_name=None):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                INSERT INTO permission (id, permission_name)
                VALUES (%s, %s)
            """, (self.id, permission_name))
            self.conn.commit()

    def read(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT * FROM permission WHERE id = %s", (self.id,))
            result = cur.fetchone()

        return result

    def update(self, permission_name=None):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            query = "UPDATE permission SET "
            params = []
            if permission_name is not None:
                query += "permission_name = %s, "
                params.append(permission_name)

            # Remove trailing comma and space
            query = query[:-2]

            query += " WHERE id = %s"
            params.append(self.id)

            cur.execute(query, tuple(params))
            self.conn.commit()

    def delete(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("DELETE FROM permission WHERE id = %s", (self.id,))
            self.conn.commit()
