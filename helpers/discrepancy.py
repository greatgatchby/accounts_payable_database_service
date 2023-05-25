import pymysql

from helpers.config import connect
import uuid


class Discrepancy:
    def __init__(self, id=None, account_id=None):
        self.conn = connect()
        self.id = id if id else str(uuid.uuid4())
        self.account_id = account_id

    def create(
        self,
        document_type=None,
        document_number=None,
        customer_id=None,
        supplier_id=None,
        discrepancy_type=None,
        document_amount=None,
        expected_amount=None,
    ):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                INSERT INTO discrepancy (
                    id,
                    document_type,
                    document_number,
                    customer_id,
                    supplier_id,
                    discrepancy_type,
                    document_amount,
                    expected_amount,
                    account_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                self.id,
                document_type,
                document_number,
                customer_id,
                supplier_id,
                discrepancy_type,
                document_amount,
                expected_amount,
                self.account_id
            ))
            self.conn.commit()

    def read_all(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT * FROM discrepancy WHERE account_id = %s", (self.account_id,))
            result = cur.fetchall()

        return result

    def read(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT * FROM discrepancy WHERE id = %s", (self.id))
            result = cur.fetchone()

        return result

    def update(
        self,
        document_type=None,
        document_number=None,
        customer_id=None,
        supplier_id=None,
        discrepancy_type=None,
        document_amount=None,
        expected_amount=None
    ):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            query = "UPDATE discrepancy SET "
            params = []
            if document_type is not None:
                query += "document_type = %s, "
                params.append(document_type)
            if document_number is not None:
                query += "document_number = %s, "
                params.append(document_number)
            if customer_id is not None:
                query += "customer_id = %s, "
                params.append(customer_id)
            if supplier_id is not None:
                query += "supplier_id = %s, "
                params.append(supplier_id)
            if discrepancy_type is not None:
                query += "discrepancy_type = %s, "
                params.append(discrepancy_type)
            if document_amount is not None:
                query += "document_amount = %s, "
                params.append(document_amount)
            if expected_amount is not None:
                query += "expected_amount = %s, "
                params.append(expected_amount)

            # Remove trailing comma and space
            query = query[:-2]

            query += " WHERE id = %s"
            params.append(self.id)

            cur.execute(query, tuple(params))
            self.conn.commit()

    def delete(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("DELETE FROM discrepancy WHERE id = %s", (self.id,))
            self.conn.commit()
