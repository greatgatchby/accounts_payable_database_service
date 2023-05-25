import unittest
import uuid
from datetime import date
from unittest import mock
from unittest.mock import MagicMock, patch

from botocore.exceptions import WaiterError
from pymysql import Error

from helpers.approval_hierarchy import ApprovalHierarchy
from helpers.config import connect
from helpers.account import Account
from helpers.customer import Customer
from helpers.discrepancy import Discrepancy
from helpers.integration import Integration
from helpers.invoice import Invoice
from helpers.invoice_item import InvoiceItem
from lambda_functions.process_invoice.process_invoice import process_invoice
from lambda_functions.process_purchase_order import process_purchase_order
from helpers.purchase_order import PurchaseOrder
from helpers.role import Role
from helpers.role_permission import RolePermission
from helpers.supplier import Supplier
from helpers.user_roles import UserRoles


class TestProcessInvoice(unittest.TestCase):
    def setUp(self):
        # Mock the Textract client and its response
        self.mock_textract_client = MagicMock()
        self.mock_textract_client.detect_document_text.return_value = {
            'Blocks': [
                {'BlockType': 'LINE', 'Text': 'INV-001'},
                {'BlockType': 'LINE', 'Text': '2023-05-12'},
                {'BlockType': 'LINE', 'Text': '2023-05-19'},
                {'BlockType': 'LINE', 'Text': 'CUST-001'},
                {'BlockType': 'LINE', 'Text': 'SUPP-001'},
                {'BlockType': 'LINE', 'Text': 'ACC-001'}
            ]
        }

        # Assign the mock Textract client to the function
        process_invoice.textract_client = self.mock_textract_client

    def test_process_invoice(self):
        # Define the test inputs
        s3_bucket = 's3://north-nvoice-rdr/'
        s3_object = 'invoice_upload/'

        # Call the function
        result = process_invoice(s3_bucket, s3_object)

        # Check the Textract client call
        self.mock_textract_client.detect_document_text.assert_called_once_with(
            Document={'S3Object': {'Bucket': s3_bucket, 'Name': s3_object}}
        )

        # Check the database interaction
        # (Assuming you have a proper database mocking mechanism in place)
        # self.assert... database assertions here

        # Check the result
        self.assertEqual(result, 'Invoice processed successfully!')


class TestAccount(unittest.TestCase):
    def setUp(self):
        self.conn = connect()
        self.account = Account()

    def tearDown(self):
        self.account.delete()
        self.conn.close()

    def test_create(self):
        self.account.create(cognito_group_id='123456')
        result = self.account.read()
        self.assertEqual(result['cognito_group_id'], '123456')

    def test_read(self):
        self.account.create(cognito_group_id='123456')
        result = self.account.read()
        self.assertEqual(result['id'], self.account.id)

    def test_update(self):
        self.account.create(cognito_group_id='123456')
        self.account.update(cognito_group_id='654321')
        result = self.account.read()
        self.assertEqual(result['cognito_group_id'], '654321')

    def test_delete(self):
        self.account.create(cognito_group_id='123456')
        self.account.delete()
        result = self.account.read()
        self.assertIsNone(result)

    @patch('pymysql.cursors.Cursor.execute')
    def test_create_error(self, mock_execute):
        mock_execute.side_effect = Error("Test error")
        with self.assertRaises(Error):
            self.account.create(cognito_group_id='123456')

    @patch('pymysql.cursors.Cursor.execute')
    def test_update_error(self, mock_execute):
        mock_execute.side_effect = Error("Test error")
        with self.assertRaises(Error):
            self.account.update(cognito_group_id='654321')


class TestApprovalHierarchy(unittest.TestCase):
    def setUp(self):
        self.conn = connect()
        self.approval_hierarchy = ApprovalHierarchy()

    def tearDown(self):
        self.approval_hierarchy.delete()
        self.conn.close()

    def test_create(self):
        self.approval_hierarchy.create(name='Hierarchy 2', account_id='account_id_1')
        result = self.approval_hierarchy.read()
        self.assertEqual(result['name'], 'Hierarchy 2')
        self.assertEqual(result['account_id'], 'account_id_1')

    def test_read(self):
        self.approval_hierarchy.create(name='Hierarchy 1', account_id='account_id_1')
        result = self.approval_hierarchy.read()
        self.assertEqual(result['id'], self.approval_hierarchy.id)

    def test_update(self):
        self.approval_hierarchy.create(name='Hierarchy 1', account_id='account_id_1')
        self.approval_hierarchy.update(name='Updated Hierarchy', )
        result = self.approval_hierarchy.read()
        self.assertEqual(result['name'], 'Updated Hierarchy')
        self.assertEqual(result['account_id'], 'account_id_1')

    def test_delete(self):
        self.approval_hierarchy.create(name='Hierarchy 2', account_id='account_id_1')
        self.approval_hierarchy.delete()
        result = self.approval_hierarchy.read()
        self.assertIsNone(result)

    @patch('pymysql.cursors.Cursor.execute')
    def test_create_error(self, mock_execute):
        mock_execute.side_effect = Error("Test error")
        with self.assertRaises(Error):
            self.approval_hierarchy.create(name='Hierarchy 1', account_id='123456')

    @patch('pymysql.cursors.Cursor.execute')
    def test_update_error(self, mock_execute):
        mock_execute.side_effect = Error("Test error")
        with self.assertRaises(Error):
            self.approval_hierarchy.update(name='Updated Hierarchy', account_id='654321')


class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.conn = connect()
        self.customer = Customer()

    def tearDown(self):
        self.customer.delete()
        self.conn.close()

    def test_create(self):
        self.customer.create(name='John Doe', address='123 Main St', phone='555-1234', email='john@example.com')
        result = self.customer.read()
        self.assertEqual(result['name'], 'John Doe')
        self.assertEqual(result['address'], '123 Main St')
        self.assertEqual(result['phone'], '555-1234')
        self.assertEqual(result['email'], 'john@example.com')

    def test_read(self):
        self.customer.create(name='John Doe', address='123 Main St', phone='555-1234', email='john@example.com')
        result = self.customer.read()
        self.assertEqual(result['id'], self.customer.id)

    def test_update(self):
        self.customer.create(name='John Doe', address='123 Main St', phone='555-1234', email='john@example.com')
        self.customer.update(name='Jane Doe', phone='555-5678')
        result = self.customer.read()
        self.assertEqual(result['name'], 'Jane Doe')
        self.assertEqual(result['address'], '123 Main St')
        self.assertEqual(result['phone'], '555-5678')
        self.assertEqual(result['email'], 'john@example.com')

    def test_delete(self):
        self.customer.create(name='John Doe', address='123 Main St', phone='555-1234', email='john@example.com')
        self.customer.delete()
        result = self.customer.read()
        self.assertIsNone(result)

    @patch('pymysql.cursors.Cursor.execute')
    def test_create_error(self, mock_execute):
        mock_execute.side_effect = Error("Test error")
        with self.assertRaises(Error):
            self.customer.create(name='John Doe', address='123 Main St', phone='555-1234', email='john@example.com')

    @patch('pymysql.cursors.Cursor.execute')
    def test_update_error(self, mock_execute):
        mock_execute.side_effect = Error("Test error")
        with self.assertRaises(Error):
            self.customer.update(name='Jane Doe', phone='555-5678')


class TestDiscrepancy(unittest.TestCase):
    def setUp(self):
        self.conn = connect()
        self.discrepancy = Discrepancy()

    def tearDown(self):
        self.discrepancy.delete()
        self.conn.close()

    def test_create(self):
        self.discrepancy.create(
            document_type='Invoice',
            document_number='INV-123',
            customer_id='12345',
            supplier_id='54321',
            discrepancy_type='Amount Mismatch',
            document_amount=100.0,
            expected_amount=120.0
        )
        result = self.discrepancy.read()
        self.assertEqual(result['document_type'], 'Invoice')
        self.assertEqual(result['document_number'], 'INV-123')
        self.assertEqual(result['customer_id'], '12345')
        self.assertEqual(result['supplier_id'], '54321')
        self.assertEqual(result['discrepancy_type'], 'Amount Mismatch')
        self.assertEqual(result['document_amount'], 100.0)
        self.assertEqual(result['expected_amount'], 120.0)

    def test_read(self):
        self.discrepancy.create(
            document_type='Invoice',
            document_number='INV-123',
            customer_id='12345',
            supplier_id='54321',
            discrepancy_type='Amount Mismatch',
            document_amount=100.0,
            expected_amount=120.0
        )
        result = self.discrepancy.read()
        self.assertEqual(result['id'], self.discrepancy.id)

    def test_update(self):
        self.discrepancy.create(
            document_type='Invoice',
            document_number='INV-123',
            customer_id='12345',
            supplier_id='54321',
            discrepancy_type='Amount Mismatch',
            document_amount=100.0,
            expected_amount=120.0
        )
        self.discrepancy.update(
            document_type='Invoice',
            document_number='RCPT-456',
            customer_id='54321',
            supplier_id='12345',
            discrepancy_type='Quantity Discrepancy',
            document_amount=200.0,
            expected_amount=220.0
        )
        result = self.discrepancy.read()
        self.assertEqual(result['document_type'], 'Invoice')
        self.assertEqual(result['document_number'], 'RCPT-456')
        self.assertEqual(result['customer_id'], '54321')
        self.assertEqual(result['supplier_id'], '12345')
        self.assertEqual(result['discrepancy_type'], 'Quantity Discrepancy')
        self.assertEqual(result['document_amount'], 200.0)
        self.assertEqual(result['expected_amount'], 220.0)

    def test_delete(self):
        self.discrepancy.create(
            document_type='Invoice',
            document_number='INV-123',
            customer_id='12345',
            supplier_id='54321',
            discrepancy_type='Amount Mismatch',
            document_amount=100.0,
            expected_amount=120.0
        )
        self.discrepancy.delete()
        result = self.discrepancy.read()
        self.assertIsNone(result)

    @patch('pymysql.cursors.Cursor.execute')
    def test_create_error(self, mock_execute):
        mock_execute.side_effect = Error("Test error")
        with self.assertRaises(Error):
            self.discrepancy.create(
                document_type='Invoice',
                document_number='INV-123',
                customer_id='12345',
                supplier_id='54321',
                discrepancy_type='Amount Mismatch',
                document_amount=100.0,
                expected_amount=120.0
            )

    @patch('pymysql.cursors.Cursor.execute')
    def test_update_error(self, mock_execute):
        self.discrepancy.create(
            document_type='Invoice',
            document_number='INV-123',
            customer_id='12345',
            supplier_id='54321',
            discrepancy_type='Amount Mismatch',
            document_amount=100.0,
            expected_amount=120.0
        )
        mock_execute.side_effect = Error("Test error")
        with self.assertRaises(Error):
            self.discrepancy.update(
                document_type='Receipt',
                document_number='RCPT-456',
                customer_id='54321',
                supplier_id='12345',
                discrepancy_type='Quantity Discrepancy',
                document_amount=200.0,
                expected_amount=220.0
            )

    @patch('pymysql.cursors.Cursor.execute')
    def test_delete_error(self, mock_execute):
        self.discrepancy.create(
            document_type='Invoice',
            document_number='INV-123',
            customer_id='12345',
            supplier_id='54321',
            discrepancy_type='Amount Mismatch',
            document_amount=100.0,
            expected_amount=120.0
        )
        mock_execute.side_effect = Error("Test error")
        with self.assertRaises(Error):
            self.discrepancy.delete()


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.integration = Integration()
        self.conn = connect()
        with self.conn.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS integration (id VARCHAR(36) PRIMARY KEY, "
                        "name VARCHAR(255), kms_key_arn VARCHAR(255), "
                        "endpoint_url VARCHAR(255), status VARCHAR(255), "
                        "account_id VARCHAR(36))")

    def tearDown(self):
        with self.conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS integration")

    @patch('pymysql.cursors.Cursor.execute')
    def test_create(self, mock_execute):
        self.integration.create(
            name='Integration 1',
            kms_key_arn='arn:aws:kms:us-east-1:123456789:key/abcd-1234',
            endpoint_url='https://api.example.com',
            status='Active',
            account_id='12345'
        )
        mock_execute.assert_called_once()

    @patch('pymysql.cursors.Cursor.execute')
    def test_create_error(self, mock_execute):
        mock_execute.side_effect = Error("Test error")
        with self.assertRaises(Error):
            self.integration.create(
                name='Integration 1',
                kms_key_arn='arn:aws:kms:us-east-1:123456789:key/abcd-1234',
                endpoint_url='https://api.example.com',
                status='Active',
                account_id='12345'
            )

    @patch('pymysql.cursors.Cursor.execute')
    def test_update(self, mock_execute):
        self.integration.create(
            name='Integration 1',
            kms_key_arn='arn:aws:kms:us-east-1:123456789:key/abcd-1234',
            endpoint_url='https://api.example.com',
            status='Active',
            account_id='12345'
        )
        self.integration.update(
            name='Integration 2',
            kms_key_arn='arn:aws:kms:us-east-1:123456789:key/abcd-5678',
            endpoint_url='https://api.example2.com',
            status='Inactive',
            account_id='54321'
        )
        mock_execute.assert_called()

    @patch('pymysql.cursors.Cursor.execute')
    def test_update_error(self, mock_execute):
        self.integration.create(
            name='Integration 1',
            kms_key_arn='arn:aws:kms:us-east-1:123456789:key/abcd-1234',
            endpoint_url='https://api.example.com',
            status='Active',
            account_id='12345'
        )
        mock_execute.side_effect = Error("Test error")
        with self.assertRaises(Error):
            self.integration.update(
                name='Integration 2',
                kms_key_arn='arn:aws:kms:us-east-1:123456789:key/abcd-5678',
                endpoint_url='https://api.example2.com',
                status='Inactive',
                account_id='54321'
            )

    @patch('pymysql.cursors.Cursor.execute')
    def test_delete(self, mock_execute):
        self.integration.create(
            name='Integration 1',
            kms_key_arn='arn:aws:kms:us-east-1:123456789:key/abcd-1234',
            endpoint_url='https://api.example.com',
            status='Active',
            account_id='12345'
        )
        self.integration.delete()
        mock_execute.assert_called()

    @patch('pymysql.cursors.Cursor.execute')
    def test_delete_error(self, mock_execute):
        self.integration.create(
            name='Integration 1',
            kms_key_arn='arn:aws:kms:us-east-1:123456789:key/abcd-1234',
            endpoint_url='https://api.example.com',
            status='Active',
            account_id='12345'
        )
        mock_execute.side_effect = Error("Test error")
        with self.assertRaises(Error):
            self.integration.delete()

    @patch('pymysql.cursors.Cursor.execute')
    class IntegrationTests(unittest.TestCase):
        def setUp(self):
            self.integration = Integration()

        @patch('helpers.integration.pymysql')
        def test_read(self, mock_pymysql):
            # Create a mock cursor object and set its execute return value
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = {'id': '1', 'name': 'Integration 1',
                                                 'kms_key_arn': 'arn:aws:kms:us-east-1:123456789:key/abcd-1234',
                                                 'endpoint_url': 'https://api.example.com',
                                                 'status': 'Active',
                                                 'account_id': '12345'}
            # Set the cursor return value for the connection's cursor method
            mock_pymysql.connect.return_value.__enter__.return_value.cursor.return_value = mock_cursor

            # Call the read method
            result = self.integration.read()

            # Assert the result
            self.assertEqual(result['name'], 'Integration 1')
            self.assertEqual(result['status'], 'Active')

    @patch('pymysql.cursors.Cursor.execute')
    def test_read_error(self, mock_execute):
        mock_execute.side_effect = Error("Test error")
        with self.assertRaises(Error):
            self.integration.read()


class TestInvoice(unittest.TestCase):
    def setUp(self):
        self.invoice_id = str(uuid.uuid4())
        self.invoice = Invoice(self.invoice_id)
        self.conn = MagicMock()
        self.cursor = MagicMock()
        self.conn.cursor.return_value = self.cursor

        # Patch the connect function to return the mock connection
        patcher = patch('helpers.config.connect', return_value=self.conn)
        self.addCleanup(patcher.stop)  # This will stop the patcher after the test
        patcher.start()

    def tearDown(self):
        self.conn.reset_mock()

    def test_create(self):
        self.invoice.create(
            invoice_number='INV-123',
            invoice_date='2023-05-12',
            due_date='2023-06-12',
            customer_id='customer_id_1',
            supplier_id='supplier_id_1',
            account_id='account_id_1',
            status='pending',
            total=300.00
        )
        result = self.invoice.read()
        self.assertEqual(result['invoice_number'], 'INV-123')
        self.assertEqual(result['customer_id'], 'customer_id_1')
        self.assertEqual(result['supplier_id'], 'supplier_id_1')
        self.assertEqual(result['account_id'], 'account_id_1')
        self.assertEqual(result['status'], 'pending')
        self.assertEqual(result['total'], 300.00)
        self.invoice.delete()

    def test_read(self):
        expected_result = {'id': self.invoice_id, 'invoice_number': 'INV-123', 'invoice_date': '2023-05-12',
                           'due_date': '2023-06-12', 'supplier_id': 'SUP-456', 'status': 'pending'}
        self.conn.cursor.return_value.__enter__.return_value.fetchone.return_value = expected_result

        result = self.invoice.read()

        self.assertEqual(result, expected_result)
        self.conn.cursor.return_value.__enter__.return_value.execute.assert_called_once_with(
            "SELECT * FROM invoice WHERE id = %s", (self.invoice_id,)
        )

    def test_update(self):
        self.invoice.update(status='paid')
        self.conn.cursor.return_value.__enter__.return_value.execute.assert_called_once_with(
            "UPDATE invoice SET status = %s WHERE id = %s", ('paid', self.invoice_id)
        )
        self.conn.commit.assert_called_once()

    @patch('pymysql.cursors.Cursor.execute')
    def test_delete(self,mock_execute):
        self.invoice.create(
            invoice_number='INV-123',
            invoice_date='2023-05-12',
            due_date='2023-06-12',
            customer_id='customer_id_1',
            supplier_id='supplier_id_1',
            account_id='account_id_1',
            status='pending',
            total=300.00
        )
        self.invoice.delete()
        mock_execute.assert_called()

class TestInvoiceItem(unittest.TestCase):
    def setUp(self):
        self.invoice_item_id = str(uuid.uuid4())
        self.invoice_item = InvoiceItem(self.invoice_item_id)
        self.conn = connect()

    def tearDown(self):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM invoice_line_item WHERE id = %s", (self.invoice_item_id,))
            self.conn.commit()
        self.conn.close()

    @patch('pymysql.cursors.Cursor.execute')
    def test_create(self, mock_execute):
        invoice_id = '8341000a-a183-4b44-8fe7-42788d0a4fb0'
        description = 'Product A'
        quantity = 5
        unit_price = 10.99
        self.invoice_item.create(invoice_id, description, quantity, unit_price)
        mock_execute.assert_called_with(
            """
            INSERT INTO invoice_line_item (id, invoice_id, description, quantity, unit_price)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (self.invoice_item_id, invoice_id, description, quantity, unit_price)
        )

    @patch('pymysql.cursors.Cursor.execute')
    def test_read(self, mock_execute):
        expected_result = {
            'id': self.invoice_id,
            'invoice_number': 'INV-123',
            'invoice_date': '2023-05-12',
            'due_date': '2023-06-12',
            'supplier_id': 'SUP-456',
            'status': 'pending'
        }
        self.conn.cursor.return_value.__enter__.return_value.fetchone.return_value = expected_result

        result = self.invoice.read()

        self.assertEqual(result, expected_result)
        self.conn.cursor.return_value.__enter__.return_value.execute.assert_called_once_with(
            "SELECT * FROM invoice WHERE id = %s", (self.invoice_id,)
        )

    @patch('pymysql.cursors.Cursor.execute')
    def test_update(self, mock_execute):
        self.invoice.update(status='paid')
        self.conn.cursor.return_value.__enter__.return_value.execute.assert_called_once_with(
            "UPDATE invoice SET status = %s WHERE id = %s", ('paid', self.id)
        )
        self.conn.commit.assert_called_once()

    @patch('pymysql.cursors.Cursor.execute')
    def test_delete(self, mock_execute):
        # Call the delete method
        self.invoice_item.delete()

        # Assert that the execute method was called with the expected query and parameters
        self.conn.cursor.execute.assert_called_once_with(
            "DELETE FROM invoice WHERE id = %s", (self.id,)
        )

        # Assert that the commit method was called once
        self.conn.commit.assert_called_once()


class TestPurchaseOrderUpload(unittest.TestCase):
    def setUp(self):
        self.s3_bucket = 'your-s3-bucket'
        self.s3_object = 'your-s3-object'
        self.expected_po_number = 'PO-123'
        self.expected_po_date = date(2023, 1, 1)
        self.expected_supplier_id = 'SUPPLIER-123'
        self.expected_account_id = 'ACCOUNT-123'

    @patch('boto3.client')
    def test_process_purchase_order_success(self, mock_boto3_client):
        textract_client_mock = MagicMock()
        mock_boto3_client.return_value = textract_client_mock

        response_mock = {
            'JobId': 'job-id',
            'Blocks': [
                {
                    'BlockType': 'KEY_VALUE_SET',
                    'EntityTypes': [
                        {
                            'Key': {'Text': 'Purchase Order Number'},
                            'Value': {'Text': self.expected_po_number}
                        },
                        {
                            'Key': {'Text': 'Purchase Order Date'},
                            'Value': {'Text': '2023-01-01'}
                        },
                        {
                            'Key': {'Text': 'Supplier ID'},
                            'Value': {'Text': self.expected_supplier_id}
                        },
                        {
                            'Key': {'Text': 'Account ID'},
                            'Value': {'Text': self.expected_account_id}
                        }
                    ]
                },
                {
                    'BlockType': 'LINE',
                    'Text': 'Item 1'
                },
                {
                    'BlockType': 'LINE',
                    'Text': 'Item 2'
                }
            ]
        }

        textract_client_mock.analyze_expense.return_value = response_mock
        textract_client_mock.get_waiter.return_value.wait.side_effect = WaiterError(
            name='text_detection_completed', reason='', last_response=None
        )

        with patch('helpers.config.connect'), patch('pymysql.cursors.Cursor.execute') as mock_cursor_execute:
            result = process_purchase_order(self.s3_bucket, self.s3_object)

        self.assertEqual(result, 'Purchase order processed successfully!')

        mock_boto3_client.assert_called_with('textract', region_name='eu-west-2')
        textract_client_mock.analyze_expense.assert_called_with(
            DocumentLocation={
                'S3Object': {
                    'Bucket': self.s3_bucket,
                    'Name': self.s3_object
                }
            }
        )
        textract_client_mock.get_waiter.assert_called_with('text_detection_completed')
        textract_client_mock.get_waiter.return_value.wait.assert_called_with(JobId='job-id')
        textract_client_mock.get_document_text_detection.assert_called_with(JobId='job-id')

        mock_cursor_execute.assert_any_call("""
            INSERT INTO purchase_order (id, po_number, po_date, supplier_id, status, account_id) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (mock.ANY, self.expected_po_number, self.expected_po_date, self.expected_supplier_id, 'pending-approval',
              self.expected_account_id))

        mock_cursor_execute.assert_any_call("""
            INSERT INTO purchase_order_line_item (id, po_id, description)
            VALUES (%s, %s, %s)
        """, (mock.ANY, mock.ANY, 'Item 1'))
        mock_cursor_execute.assert_any_call("""
                    INSERT INTO purchase_order_line_item (id, po_id, description)
                    VALUES (%s, %s, %s)
                """, (mock.ANY, mock.ANY, 'Item 2'))

    @patch('boto3.client')
    def test_process_purchase_order_waiter_error(self, mock_boto3_client):
        textract_client_mock = MagicMock()
        mock_boto3_client.return_value = textract_client_mock

        response_mock = {
            'JobId': 'job-id',
            'Blocks': [
                {
                    'BlockType': 'KEY_VALUE_SET',
                    'EntityTypes': [
                        {
                            'Key': {'Text': 'Purchase Order Number'},
                            'Value': {'Text': self.expected_po_number}
                        },
                        {
                            'Key': {'Text': 'Purchase Order Date'},
                            'Value': {'Text': '2023-01-01'}
                        },
                        {
                            'Key': {'Text': 'Supplier ID'},
                            'Value': {'Text': self.expected_supplier_id}
                        },
                        {
                            'Key': {'Text': 'Account ID'},
                            'Value': {'Text': self.expected_account_id}
                        }
                    ]
                },
                {
                    'BlockType': 'LINE',
                    'Text': 'Item 1'
                },
                {
                    'BlockType': 'LINE',
                    'Text': 'Item 2'
                }
            ]
        }

        textract_client_mock.analyze_expense.return_value = response_mock
        textract_client_mock.get_waiter.return_value.wait.side_effect = WaiterError(
            name='text_detection_completed', reason='', last_response=None
        )

        with patch('helpers.config.connect'), patch('pymysql.cursors.Cursor.execute'):
            result = process_purchase_order(self.s3_bucket, self.s3_object)

        self.assertEqual(result, 'Purchase order processed successfully!')

        mock_boto3_client.assert_called_with('textract', region_name='eu-west-2')
        textract_client_mock.analyze_expense.assert_called_with(
            DocumentLocation={
                'S3Object': {
                    'Bucket': self.s3_bucket,
                    'Name': self.s3_object
                }
            }
        )
        textract_client_mock.get_waiter.assert_called_with('text_detection_completed')
        textract_client_mock.get_waiter.return_value.wait.assert_called_with(JobId='job-id')
        textract_client_mock.get_document_text_detection.assert_called_with(JobId='job-id')

    def test_process_purchase_order_failure(self):
        with patch('boto3.client') as mock_boto3_client:
            textract_client_mock = MagicMock()
            mock_boto3_client.return_value = textract_client_mock

            textract_client_mock.analyze_expense.side_effect = Exception('An error occurred')

            with patch('helpers.config.connect'), patch('pymysql.cursors.Cursor.execute'):
                result = process_purchase_order(self.s3_bucket, self.s3_object)

        self.assertEqual(result, None)

        mock_boto3_client.assert_called_with('textract', region_name='eu-west-2')
        textract_client_mock.analyze_expense.assert_called_with(
            DocumentLocation={
                'S3Object': {
                    'Bucket': self.s3_bucket,
                    'Name': self.s3_object
                }
            }
        )


class TestPurchaseOrder(unittest.TestCase):
    def setUp(self):
        self.po_id = 'po-id'
        self.po_number = 'PO-123'
        self.po_date = '2023-01-01'
        self.supplier_id = 'SUPPLIER-123'
        self.status = 'pending-approval'

    def test_create(self):
        with patch('helpers.config.connect'), patch('pymysql.cursors.Cursor.execute') as mock_cursor_execute:
            po = PurchaseOrder(self.po_id)
            po.create(self.po_number, self.po_date, self.supplier_id, self.status)

        mock_cursor_execute.assert_called_once_with("""
            INSERT INTO purchase_order (id, po_number, po_date, supplier_id, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (self.po_id, self.po_number, self.po_date, self.supplier_id, self.status))

    def test_read(self):
        expected_result = {
            'id': self.po_id,
            'po_number': self.po_number,
            'po_date': self.po_date,
            'supplier_id': self.supplier_id,
            'status': self.status
        }

        with patch('helpers.config.connect'), patch('pymysql.cursors.Cursor.execute') as mock_cursor_execute:
            mock_cursor_execute.return_value.fetchone.return_value = expected_result

            po = PurchaseOrder(self.po_id)
            result = po.read()

        self.assertEqual(result, expected_result)
        mock_cursor_execute.assert_called_once_with("SELECT * FROM purchase_order WHERE id = %s", (self.po_id,))

    def test_update(self):
        with patch('helpers.config.connect'), patch('pymysql.cursors.Cursor.execute') as mock_cursor_execute:
            po = PurchaseOrder(self.po_id)
            po.update(po_number='PO-456', status='approved')

        mock_cursor_execute.assert_called_once_with("""
            UPDATE purchase_order SET po_number = %s, status = %s WHERE id = %s
        """, ('PO-456', 'approved', self.po_id))

    def test_delete(self):
        with patch('helpers.config.connect'), patch('pymysql.cursors.Cursor.execute') as mock_cursor_execute:
            po = PurchaseOrder(self.po_id)
            po.delete()

        mock_cursor_execute.assert_called_once_with("DELETE FROM purchase_order WHERE id = %s", (self.po_id,))


class TestRole(unittest.TestCase):
    def setUp(self):
        self.role_id = 'role-id'
        self.role_name = 'Admin'
        self.account_id = 'account-id'

    def test_create(self):
        with patch('helpers.config.connect'), patch('pymysql.cursors.Cursor.execute') as mock_cursor_execute:
            role = Role(self.role_id)
            role.create(self.role_name, self.account_id)

        mock_cursor_execute.assert_called_once_with("""
            INSERT INTO role (id, role_name, account_id)
            VALUES (%s, %s, %s)
        """, (self.role_id, self.role_name, self.account_id))

    def test_read(self):
        expected_result = {
            'id': self.role_id,
            'role_name': self.role_name,
            'account_id': self.account_id,
            'permission_id': 'permission-id',
            'permission_name': 'Permission 1'
        }

        with patch('helpers.config.connect'), patch('pymysql.cursors.Cursor.execute') as mock_cursor_execute:
            mock_cursor_execute.return_value.fetchone.return_value = expected_result

            role = Role(self.role_id)
            result = role.read()

        self.assertEqual(result, expected_result)
        mock_cursor_execute.assert_called_once_with("""
            SELECT role.*, role_permission.*
            FROM role
            JOIN role_permission ON role.id = role_permission.role_id
            WHERE role.id = %s
        """, (self.role_id,))

    def test_update(self):
        with patch('helpers.config.connect'), patch('pymysql.cursors.Cursor.execute') as mock_cursor_execute:
            role = Role(self.role_id)
            role.update(role_name='Editor')

        mock_cursor_execute.assert_called_once_with("""
            UPDATE role SET role_name = %s WHERE id = %s
        """, ('Editor', self.role_id))

    def test_delete(self):
        with patch('helpers.config.connect'), patch('pymysql.cursors.Cursor.execute') as mock_cursor_execute:
            role = Role(self.role_id)
            role.delete()

        mock_cursor_execute.assert_called_once_with("DELETE FROM role WHERE id = %s", (self.role_id,))


class TestRolePermission(unittest.TestCase):
    def setUp(self):
        self.role_permission_id = 'role-permission-id'
        self.role_id = 'role-id'
        self.permission_id = 'permission-id'

    def test_create(self):
        with patch('helpers.config.connect'), patch('pymysql.cursors.Cursor.execute') as mock_cursor_execute:
            role_permission = RolePermission(self.role_permission_id)
            role_permission.create(self.role_id, self.permission_id)

        mock_cursor_execute.assert_called_once_with("""
            INSERT INTO role_permission (id, role_id, permission_id)
            VALUES (%s, %s, %s)
        """, (self.role_permission_id, self.role_id, self.permission_id))

    def test_read(self):
        expected_result = {
            'id': self.role_permission_id,
            'role_id': self.role_id,
            'permission_id': self.permission_id
        }

        with patch('helpers.config.connect'), patch('pymysql.cursors.Cursor.execute') as mock_cursor_execute:
            mock_cursor_execute.return_value.fetchone.return_value = expected_result

            role_permission = RolePermission(self.role_permission_id)
            result = role_permission.read()

        self.assertEqual(result, expected_result)
        mock_cursor_execute.assert_called_once_with("SELECT * FROM role_permission WHERE id = %s",
                                                    (self.role_permission_id,))

    def test_update(self):
        with patch('helpers.config.connect'), patch('pymysql.cursors.Cursor.execute') as mock_cursor_execute:
            role_permission = RolePermission(self.role_permission_id)
            role_permission.update(role_id='new-role-id')

        mock_cursor_execute.assert_called_once_with("""
            UPDATE role_permission SET role_id = %s WHERE id = %s
        """, ('new-role-id', self.role_permission_id))

    def test_delete(self):
        with patch('helpers.config.connect'), patch('pymysql.cursors.Cursor.execute') as mock_cursor_execute:
            role_permission = RolePermission(self.role_permission_id)
            role_permission.delete()

        mock_cursor_execute.assert_called_once_with("DELETE FROM role_permission WHERE id = %s",
                                                    (self.role_permission_id,))


class TestSupplier(unittest.TestCase):
    def setUp(self):
        self.supplier_id = 'supplier-id'
        self.name = 'Supplier Name'
        self.address = 'Supplier Address'
        self.phone = 'Supplier Phone'
        self.email = 'supplier@example.com'

    def test_create(self):
        with patch('helpers.config.connect'), patch('pymysql.cursors.Cursor.execute') as mock_cursor_execute:
            supplier = Supplier(self.supplier_id)
            supplier.create(self.name, self.address, self.phone, self.email)

        mock_cursor_execute.assert_called_once_with("""
            INSERT INTO supplier (id, name, address, phone, email)
            VALUES (%s, %s, %s, %s, %s)
        """, (self.supplier_id, self.name, self.address, self.phone, self.email))

    def test_read(self):
        expected_result = {
            'id': self.supplier_id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'email': self.email
        }

        with patch('helpers.config.connect'), patch('pymysql.cursors.Cursor.execute') as mock_cursor_execute:
            mock_cursor_execute.return_value.fetchone.return_value = expected_result

            supplier = Supplier(self.supplier_id)
            result = supplier.read()

        self.assertEqual(result, expected_result)
        mock_cursor_execute.assert_called_once_with("SELECT * FROM supplier WHERE id = %s", (self.supplier_id,))

    def test_update(self):
        with patch('helpers.config.connect'), patch('pymysql.cursors.Cursor.execute') as mock_cursor_execute:
            supplier = Supplier(self.supplier_id)
            supplier.update(name='New Supplier Name')

        mock_cursor_execute.assert_called_once_with("""
            UPDATE supplier SET name = %s WHERE id = %s
        """, ('New Supplier Name', self.supplier_id))

    def test_delete(self):
        with patch('helpers.config.connect'), patch('pymysql.cursors.Cursor.execute') as mock_cursor_execute:
            supplier = Supplier(self.supplier_id)
            supplier.delete()

        mock_cursor_execute.assert_called_once_with("DELETE FROM supplier WHERE id = %s", (self.supplier_id,))


class TestUserRoles(unittest.TestCase):
    def setUp(self):
        self.user_id = 'user-id'
        self.role_id = 'role-id'

    def test_create(self):
        with patch('helpers.config.connect'), patch('pymysql.cursors.Cursor.execute') as mock_cursor_execute:
            user_roles = UserRoles(self.user_id, self.role_id)
            user_roles.create()

        mock_cursor_execute.assert_called_once_with("""
            INSERT INTO user_roles (user_id, role_id)
            VALUES (%s, %s)
        """, (self.user_id, self.role_id))

    def test_delete(self):
        with patch('helpers.config.connect'), patch('pymysql.cursors.Cursor.execute') as mock_cursor_execute:
            user_roles = UserRoles(self.user_id, self.role_id)
            user_roles.delete()

        mock_cursor_execute.assert_called_once_with("""
            DELETE FROM user_roles
            WHERE user_id = %s AND role_id = %s
        """, (self.user_id, self.role_id))


if __name__ == '__unit_test__':
    unittest.main()
