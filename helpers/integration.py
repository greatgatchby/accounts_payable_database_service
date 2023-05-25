import pymysql

from helpers.config import connect
import uuid


class Integration:
    def __init__(self, id=None, account_id=None):
        self.conn = connect()
        self.id = id if id else str(uuid.uuid4())
        self.account_id = account_id

    def create(
        self,
        name=None,
        kms_key_arn=None,
        endpoint_url=None,
        status=None,
        account_id=None
    ):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                INSERT INTO integration (
                    id,
                    name,
                    kms_key_arn,
                    endpoint_url,
                    status,
                    account_id
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                self.id,
                name,
                kms_key_arn,
                endpoint_url,
                status,
                account_id
            ))
            self.conn.commit()

    def read(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT * FROM integration WHERE id = %s", (self.id,))
            result = cur.fetchone()

        return result

    def read_all(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT * FROM integration WHERE account_id = %s", (self.account_id,))
            result = cur.fetchall()

        return result

    def update(
        self,
        name=None,
        kms_key_arn=None,
        endpoint_url=None,
        status=None,
        account_id=None
    ):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            query = "UPDATE integration SET "
            params = []
            if name is not None:
                query += "name = %s, "
                params.append(name)
            if kms_key_arn is not None:
                query += "kms_key_arn = %s, "
                params.append(kms_key_arn)
            if endpoint_url is not None:
                query += "endpoint_url = %s, "
                params.append(endpoint_url)
            if status is not None:
                query += "status = %s, "
                params.append(status)
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
            cur.execute("DELETE FROM integration WHERE id = %s", (self.id,))
            self.conn.commit()
