import pymysql

from helpers.config import connect
import uuid


class ApprovalHierarchy:
    def __init__(self, id=None, account_id=None):
        self.conn = connect()
        self.id = id if id else str(uuid.uuid4())
        self.account_id = account_id

    def create(self, name=None, account_id=None):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                INSERT INTO approval_hierarchy (id, name, account_id)
                VALUES (%s, %s, %s)
            """, (self.id, name, account_id))
            self.conn.commit()

    def read(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            # Fetch the approval hierarchy
            cur.execute("SELECT * FROM approval_hierarchy WHERE id = %s", (self.id,))
            approval_hierarchy = cur.fetchone()

            if approval_hierarchy is not None:
                # Fetch the associated approvers
                cur.execute("SELECT * FROM approver WHERE hierarchy_id = %s", (self.id,))
                approvers = cur.fetchall()

                # Add the approvers to the approval hierarchy
                approval_hierarchy['approvers'] = approvers

        return approval_hierarchy

    def read_all(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            # Fetch the approval hierarchies
            cur.execute("SELECT * FROM approval_hierarchy WHERE account_id = %s", (self.account_id,))
            approval_hierarchies = cur.fetchall()

            # Fetch the approvers
            cur.execute(
                "SELECT * FROM approver WHERE hierarchy_id IN (%s)" % ','.join(['%s'] * len(approval_hierarchies)),
                tuple([hierarchy['id'] for hierarchy in approval_hierarchies]))
            approvers = cur.fetchall()

        # Map the approvers to their respective approval hierarchies
        hierarchy_map = {hierarchy['id']: hierarchy for hierarchy in approval_hierarchies}
        for approver in approvers:
            hierarchy_id = approver['hierarchy_id']
            if hierarchy_id in hierarchy_map:
                hierarchy = hierarchy_map[hierarchy_id]
                if 'approvers' not in hierarchy:
                    hierarchy['approvers'] = []
                hierarchy['approvers'].append(approver)

        return approval_hierarchies

    def update(self, name=None, account_id=None):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            query = "UPDATE approval_hierarchy SET "
            params = []
            if name is not None:
                query += "name = %s, "
                params.append(name)
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
            cur.execute("DELETE FROM approval_hierarchy WHERE id = %s", (self.id,))
            self.conn.commit()
