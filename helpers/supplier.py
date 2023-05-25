import pymysql

from helpers.config import connect
import uuid


class Supplier:
    def __init__(self, id=None, account_id=None):
        self.conn = connect()
        self.id = id if id else str(uuid.uuid4())
        self.account_id = account_id

    def create(self, name, address=None, phone=None, email=None):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                INSERT INTO supplier (id, name, address, phone, email)
                VALUES (%s, %s, %s, %s, %s)
            """, (self.id, name, address, phone, email))
            self.conn.commit()

    def read(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT * FROM supplier WHERE id = %s", (self.id,))
            result = cur.fetchone()

        return result

    def read_all(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT * FROM supplier WHERE account_id = %s", (self.account_id,))
            result = cur.fetchall()

        return result

    def update(self, name=None, address=None, phone=None, email=None):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            query = "UPDATE supplier SET "
            params = []
            if name is not None:
                query += "name = %s, "
                params.append(name)
            if address is not None:
                query += "address = %s, "
                params.append(address)
            if phone is not None:
                query += "phone = %s, "
                params.append(phone)
            if email is not None:
                query += "email = %s, "
                params.append(email)

            # Remove trailing comma and space
            query = query[:-2]

            query += " WHERE id = %s"
            params.append(self.id)

            cur.execute(query, tuple(params))
            self.conn.commit()

    def delete(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("DELETE FROM supplier WHERE id = %s", (self.id,))
            self.conn.commit()
