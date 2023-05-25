import pymysql.cursors

from helpers.config import connect
import uuid


class Role:
    def __init__(self, id=None):
        self.conn = connect()
        self.id = id if id else str(uuid.uuid4())

    def create(self, role_name=None, account_id=None):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                INSERT INTO role (id, role_name, account_id)
                VALUES (%s, %s, %s)
            """, (self.id, role_name, account_id))
            self.conn.commit()

    def read(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                SELECT role.*, role_permission.*
                FROM role
                JOIN role_permission ON role.id = role_permission.role_id
                WHERE role.id = %s
            """, (self.id,))
            result = cur.fetchone()
        return result

    def update(self, role_name=None, account_id=None):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            query = "UPDATE role SET "
            params = []
            if role_name is not None:
                query += "role_name = %s, "
                params.append(role_name)
            if account_id is not None:
                query += "account_id = %s, "
                params.append(account_id)

            # Remove trailing comma and space
            query = query[:-2]

            query += " WHERE id = %s"
            params.append(self.id)

            cur.execute(query, tuple(params))
            self.conn.commit()

    def delete(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("DELETE FROM role WHERE id = %s", (self.id,))
            self.conn.commit()
