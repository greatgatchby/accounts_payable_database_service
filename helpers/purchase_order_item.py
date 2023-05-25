import pymysql

from helpers.config import connect
import uuid


class PurchaseOrderItem:
    def __init__(self, id=None):
        self.conn = connect()
        self.id = id if id else str(uuid.uuid4())

    def create(self, po_id, description, quantity, unit_price):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                INSERT INTO purchase_order_line_item (id, po_id, description, quantity, unit_price)
                VALUES (%s, %s, %s, %s, %s)
            """, (self.id, po_id, description, quantity, unit_price))
            self.conn.commit()

    def read(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT * FROM purchase_order_line_item WHERE id = %s", (self.id,))
            result = cur.fetchone()

        return result

    def update(self, po_id=None, description=None, quantity=None, unit_price=None):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            query = "UPDATE purchase_order_line_item SET "
            params = []
            if po_id is not None:
                query += "po_id = %s, "
                params.append(po_id)
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
            cur.execute("DELETE FROM purchase_order_line_item WHERE id = %s", (self.id,))
            self.conn.commit()
