import pymysql

from helpers.config import connect
import uuid


class InvoiceItem:
    def __init__(self, id=None):
        self.conn = connect()
        self.id = id if id else str(uuid.uuid4())

    def create(self, invoice_id, description, quantity, unit_price):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
            INSERT INTO invoice_line_item (id, invoice_id, description, quantity, unit_price)
            VALUES (%s, %s, %s, %s, %s)
            """, (self.id, invoice_id, description, quantity, unit_price))
            self.conn.commit()

    def read(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT * FROM invoice_line_item WHERE id = %s", (self.id,))
            result = cur.fetchone()

        return result

    def update(self, invoice_id=None, description=None, quantity=None, unit_price=None):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            query = "UPDATE invoice_line_item SET "
            params = []
            if invoice_id is not None:
                query += "invoice_id = %s, "
                params.append(invoice_id)
            if description is not None:
                query += "description = %s, "
                params.append(description)
            if quantity is not None:
                query += "quantity = %s, "
                params.append(quantity)
            if unit_price is not None:
                query += "unit_price = %s, "
                params.append(unit_price)

            # Remove trailing comma and space
            query = query[:-2]

            query += " WHERE id = %s"
            params.append(self.id)

            cur.execute(query, tuple(params))
            self.conn.commit()

    def delete(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("DELETE FROM invoice_line_item WHERE id = %s", (self.id,))
            self.conn.commit()