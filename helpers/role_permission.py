import pymysql

from helpers.config import connect
import uuid


class RolePermission:
    def __init__(self, id=None):
        self.conn = connect()
        self.id = id if id else str(uuid.uuid4())

    def create(self, role_id=None, permission_id=None):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                INSERT INTO role_permission (id, role_id, permission_id)
                VALUES (%s, %s, %s)
            """, (self.id, role_id, permission_id))
            self.conn.commit()

    def read(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT * FROM role_permission WHERE id = %s", (self.id,))
            result = cur.fetchone()

        return result

    def update(self, role_id=None, permission_id=None):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            query = "UPDATE role_permission SET "
            params = []
            if role_id is not None:
                query += "role_id = %s, "
                params.append(role_id)
            if permission_id is not None:
                query += "permission_id = %s, "
                params.append(permission_id)

            # Remove trailing comma and space
            query = query[:-2]

            query += " WHERE id = %s"
            params.append(self.id)

            cur.execute(query, tuple(params))
            self.conn.commit()

    def delete(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("DELETE FROM role_permission WHERE id = %s", (self.id,))
            self.conn.commit()
