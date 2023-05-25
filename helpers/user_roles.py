import pymysql

from helpers.config import connect

class UserRoles:
    def __init__(self, user_id=None, role_id=None):
        self.conn = connect()
        self.user_id = user_id
        self.role_id = role_id

    def create(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                INSERT INTO user_roles (user_id, role_id)
                VALUES (%s, %s)
            """, (self.user_id, self.role_id))
            self.conn.commit()

    def delete(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                DELETE FROM user_roles
                WHERE user_id = %s AND role_id = %s
            """, (self.user_id, self.role_id))
            self.conn.commit()
