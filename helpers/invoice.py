import pymysql

from helpers.config import connect
import uuid


class Invoice:
    def __init__(self, id=None, account_id=None):
        self.conn = connect()
        self.id = id if id else str(uuid.uuid4())
        self.account_id = account_id

    def create(self, invoice_number, invoice_date, due_date, customer_id, supplier_id, account_id, status, total):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                INSERT INTO invoice (id, invoice_number, invoice_date, due_date, customer_id, supplier_id, account_id, status, total)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (self.id, invoice_number, invoice_date, due_date, customer_id, supplier_id, account_id, status, total))
            self.conn.commit()
        return self.id

    def read(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT * FROM invoice WHERE id = %s", (self.id,))
            result = cur.fetchone()

            if result:
                # Fetch the line items
                cur.execute(
                    "SELECT * FROM invoice_line_item WHERE invoice_id = %s", (self.id,))
                line_items = cur.fetchall()

                # Map the line items to their respective purchase order
                result['line_items'] = line_items

        return result

    def read_all(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            # Fetch the invoices
            cur.execute("SELECT * FROM invoice WHERE account_id = %s", (self.account_id,))
            invoices = cur.fetchall()

            # Fetch the line items
            cur.execute("SELECT * FROM invoice_line_item WHERE invoice_id IN (%s)" % ','.join(['%s'] * len(invoices)),
                        tuple([invoice['id'] for invoice in invoices]))
            line_items = cur.fetchall()

        # Map the line items to their respective invoices
        invoice_map = {invoice['id']: invoice for invoice in invoices}
        for line_item in line_items:
            invoice_id = line_item['invoice_id']
            if invoice_id in invoice_map:
                invoice = invoice_map[invoice_id]
                if 'line_items' not in invoice:
                    invoice['line_items'] = []
                invoice['line_items'].append(line_item)

        return invoices

    def update(self, invoice_number=None, invoice_date=None, due_date=None, supplier_id=None, status=None):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            query = "UPDATE invoice SET "
            params = []
            if invoice_number is not None:
                query += "invoice_number = %s, "
                params.append(invoice_number)
            if invoice_date is not None:
                query += "invoice_date = %s, "
                params.append(invoice_date)
            if due_date is not None:
                query += "due_date = %s, "
                params.append(due_date)
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
            cur.execute("DELETE FROM invoice WHERE id = %s", (self.id,))
            self.conn.commit()
