import pymysql

from helpers.config import connect
import uuid


class PurchaseOrder:
    def __init__(self, id=None, account_id=None):
        self.conn = connect()
        self.id = id if id else str(uuid.uuid4())
        self.account_id = account_id

    def create(self, po_number, po_date, supplier_id, status):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                INSERT INTO purchase_order (id, po_number, po_date, supplier_id, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (self.id, po_number, po_date, supplier_id, status))
            self.conn.commit()

    def read_all(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            # Fetch the invoices
            cur.execute("SELECT * FROM purchase_order WHERE account_id = %s", (self.account_id,))
            purchase_orders = cur.fetchall()

            # Fetch the line items
            cur.execute("SELECT * FROM purchase_order_line_item WHERE po_id IN (%s)" % ','.join(['%s'] * len(purchase_orders)),
                        tuple([po['id'] for po in purchase_orders]))
            line_items = cur.fetchall()

        # Map the line items to their respective invoices
        po_map = {po['id']: po for po in purchase_orders}
        for line_item in line_items:
            po_id = line_item['po_id']
            if po_id in po_map:
                po = po_map[po_id]
                if 'line_items' not in po:
                    po['line_items'] = []
                po['line_items'].append(line_item)

        return purchase_orders

    def read(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT * FROM purchase_order WHERE id = %s", (self.id,))
            result = cur.fetchone()

            if result:
                # Fetch the line items
                cur.execute(
                    "SELECT * FROM purchase_order_line_item WHERE po_id = %s", (self.id,))
                line_items = cur.fetchall()

                # Map the line items to their respective purchase order
                result['line_items'] = line_items

        return result

    def update(self, po_number=None, po_date=None, supplier_id=None, status=None):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            query = "UPDATE purchase_order SET "
            params = []
            if po_number is not None:
                query += "po_number = %s, "
                params.append(po_number)
            if po_date is not None:
                query += "po_date = %s, "
                params.append(po_date)
            if supplier_id is not None:
                query += "supplier_id = %s, "
                params.append(supplier_id)
            if status is not None:
                query += "status = %s, "
                params.append(status)

            # Remove trailing comma and space
            query = query[:-2]

            query += " WHERE id = %s"
            params.append(self.id)

            cur.execute(query, tuple(params))
            self.conn.commit()

    def delete(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("DELETE FROM purchase_order WHERE id = %s", (self.id,))
            self.conn.commit()
