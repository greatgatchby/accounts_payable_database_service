import pymysql

from helpers.config import connect
import uuid


class Account:
    def __init__(self, id=None):
        self.conn = connect()
        self.id = id if id else str(uuid.uuid4())

    def create(self, cognito_group_id=None):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                INSERT INTO account (id, cognito_group_id)
                VALUES (%s, %s)
            """, (self.id, cognito_group_id))
            self.conn.commit()

    def read(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT * FROM account WHERE id = %s", (self.id,))
            result = cur.fetchone()

        return result

    def update(self, cognito_group_id=None):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            query = "UPDATE account SET "
            params = []
            if cognito_group_id is not None:
                query += "cognito_group_id = %s, "
                params.append(cognito_group_id)

            # Remove trailing comma and space
            query = query[:-2]

            query += " WHERE id = %s"
            params.append(self.id)

            cur.execute(query, tuple(params))
            self.conn.commit()

    def delete(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("DELETE FROM account WHERE id = %s", (self.id,))
            self.conn.commit()
