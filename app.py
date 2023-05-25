from flask import Flask, request, jsonify

from helpers.approver import Approver
from helpers.account import Account
from helpers.approval_hierarchy import ApprovalHierarchy
from helpers.customer import Customer
from helpers.discrepancy import Discrepancy
from helpers.integration import Integration
from helpers.invoice_item import InvoiceItem
from helpers.permission import Permission
from helpers.purchase_order_item import PurchaseOrderItem
from helpers.role import Role
from helpers.role_permission import RolePermission
from helpers.supplier import Supplier
from helpers.invoice import Invoice
from helpers.purchase_order import PurchaseOrder
from helpers.user_roles import UserRoles

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/process-invoice', methods=['POST'])
def process_invoice_endpoint():
    # Get the request data
    data = request.get_json()
    s3_bucket = data['s3_bucket']
    s3_object = data['s3_object']

    try:
        # Process the invoice
        result = process_invoice(s3_bucket, s3_object)
        return result
    except Exception as e:
        return str(e), 500


@app.route('/supplier/get-all/<account_id>', methods=['GET'])
def create_supplier(account_id):
    supplier = Supplier('', account_id)
    result = supplier.read_all()
    return jsonify(result), 200


@app.route('/supplier/<supplier_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_supplier(supplier_id):
    supplier = Supplier(supplier_id)

    if request.method == 'GET':
        result = supplier.read()
        if result is None:
            return jsonify({'message': 'Supplier not found'}), 404
        else:
            return jsonify(result), 200

    elif request.method == 'PUT':
        data = request.json
        supplier.update(data.get('name'), data.get('address'), data.get('phone'), data.get('email'))
        return jsonify({'message': 'Supplier updated successfully'}), 200

    elif request.method == 'DELETE':
        supplier.delete()
        return jsonify({'message': 'Supplier deleted successfully'}), 200


@app.route('/invoice/get-all/<account_id>')
def handle_get_all_invoices(account_id):
    invoice = Invoice('', account_id)
    if request.method == 'GET':
        result = invoice.read_all()
        if result is None:
            return jsonify({'message': 'No invoices found'}), 404
        else:
            return jsonify(result), 200


@app.route('/invoice/<invoice_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_invoice(invoice_id):
    invoice = Invoice(invoice_id, '')

    if request.method == 'GET':
        result = invoice.read()
        if result is None:
            return jsonify({'message': 'Invoice not found'}), 404
        else:
            return jsonify(result), 200

    elif request.method == 'PUT':
        data = request.json
        invoice.update(data.get('invoice_number'), data.get('invoice_date'), data.get('due_date'),
                       data.get('supplier_id'), data.get('status'))
        return jsonify({'message': 'Invoice updated successfully'}), 200

    elif request.method == 'DELETE':
        invoice.delete()
        return jsonify({'message': 'Invoice deleted successfully'}), 200


@app.route('/purchase_order/get-all/<account_id>')
def handle_get_all_purchase_orders(account_id):
    purchase_order = PurchaseOrder('', account_id)
    if request.method == 'GET':
        result = purchase_order.read_all()
        if result is None:
            return jsonify({'message': 'No invoices found'}), 404
        else:
            return jsonify(result), 200


@app.route('/purchase_order_line_item/', methods=['POST'])
def create_purchase_order_line_item():
    data = request.json
    purchase_order_line_item = PurchaseOrderItem()
    purchase_order_line_item.create(data['po_id'], data['description'], data.get('quantity'), data.get('unit_price'))
    return jsonify({'message': 'Line item added successfully', 'id': purchase_order_line_item.id}), 201


@app.route('/purchase_order/<purchase_order_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_purchase_order(purchase_order_id):
    purchase_order = PurchaseOrder(purchase_order_id)

    if request.method == 'GET':
        result = purchase_order.read()
        if result is None:
            return jsonify({'message': 'Purchase order not found'}), 404
        else:
            return jsonify(result), 200

    elif request.method == 'PUT':
        data = request.json
        purchase_order.update(data.get('po_number'), data.get('po_date'), data.get('supplier_id'), data.get('status'))
        return jsonify({'message': 'Purchase order updated successfully'}), 200

    elif request.method == 'DELETE':
        purchase_order.delete()
        return jsonify({'message': 'Purchase order deleted successfully'}), 200


@app.route('/purchase_order_item/<purchase_order_item_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_purchase_order_item(purchase_order_item_id):
    purchase_order_item = PurchaseOrderItem(purchase_order_item_id)

    if request.method == 'GET':
        result = purchase_order_item.read()
        if result is None:
            return jsonify({'message': 'Purchase order item not found'}), 404
        else:
            return jsonify(result), 200

    elif request.method == 'PUT':
        data = request.json
        purchase_order_item.update(data.get('po_id'), data.get('description'), data.get('quantity'),
                                   data.get('unit_price'))
        return jsonify({'message': 'Purchase order item updated successfully'}), 200

    elif request.method == 'DELETE':
        purchase_order_item.delete()
        return jsonify({'message': 'Purchase order item deleted successfully'}), 200


@app.route('/invoice_item', methods=['POST'])
def create_invoice_item():
    data = request.json
    invoice_item = InvoiceItem()
    invoice_item.create(data['invoice_id'], data['description'], data['quantity'], data['unit_price'])
    return jsonify({'message': 'Invoice item created successfully', 'id': invoice_item.id}), 201


@app.route('/invoice_item/<invoice_item_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_invoice_item(invoice_item_id):
    invoice_item = InvoiceItem(invoice_item_id)

    if request.method == 'GET':
        result = invoice_item.read()
        if result is None:
            return jsonify({'message': 'Invoice item not found'}), 404
        else:
            return jsonify(result), 200

    elif request.method == 'PUT':
        data = request.json
        invoice_item.update(data.get('invoice_id'), data.get('description'), data.get('quantity'),
                            data.get('unit_price'))
        return jsonify({'message': 'Invoice item updated successfully'}), 200

    elif request.method == 'DELETE':
        invoice_item.delete()
        return jsonify({'message': 'Invoice item deleted successfully'}), 200


@app.route('/customer', methods=['POST'])
def create_customer():
    data = request.json
    customer = Customer()
    customer.create(data['name'], data['address'], data.get('phone'), data.get('email'))
    return jsonify({'message': 'Customer created successfully', 'id': customer.id}), 201


@app.route('/customer/get-all/<account_id>', methods=['GET'])
def get_all_customers(account_id):
    account = Customer('', account_id)
    if request.method == 'GET':
        result = account.read_all()
        if result is None:
            return jsonify({'message': 'No customers found'}), 404
        else:
            return jsonify(result), 200


@app.route('/customer/<customer_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_customer(customer_id):
    customer = Customer(customer_id)

    if request.method == 'GET':
        result = customer.read()
        if result is None:
            return jsonify({'message': 'Customer not found'}), 404
        else:
            return jsonify(result), 200

    elif request.method == 'PUT':
        data = request.json
        customer.update(data.get('name'), data.get('address'), data.get('phone'), data.get('email'))
        return jsonify({'message': 'Customer updated successfully'}), 200

    elif request.method == 'DELETE':
        customer.delete()
        return jsonify({'message': 'Customer deleted successfully'}), 200


@app.route('/account', methods=['POST'])
def create_account():
    data = request.json
    account = Account()
    account.create(data.get('cognito_group_id'))
    return jsonify({'message': 'Account created successfully', 'id': account.id}), 201


@app.route('/account/<account_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_account(account_id):
    account = Account(account_id)

    if request.method == 'GET':
        result = account.read()
        if result is None:
            return jsonify({'message': 'Account not found'}), 404
        else:
            return jsonify(result), 200

    elif request.method == 'PUT':
        data = request.json
        account.update(data.get('cognito_group_id'))
        return jsonify({'message': 'Account updated successfully'}), 200

    elif request.method == 'DELETE':
        account.delete()
        return jsonify({'message': 'Account deleted successfully'}), 200


@app.route('/approval-hierarchy/get-all/<account_id>', methods=['GET'])
def read_all_approval_heirarchies(account_id):
    approval_hierarchy = ApprovalHierarchy('', account_id)
    if request.method == 'GET':
        result = approval_hierarchy.read_all()
        if result is None:
            return jsonify({'message': 'No approval hierarchy found'}), 404
        else:
            return jsonify(result), 200


@app.route('/approval-hierarchy', methods=['POST'])
def create_approval_hierarchy():
    data = request.json
    approval_hierarchy = ApprovalHierarchy()
    approval_hierarchy.create(data.get('name'), data.get('account_id'))
    return jsonify({'message': 'Approval hierarchy created successfully', 'id': approval_hierarchy.id}), 201


@app.route('/approval-hierarchy/<approval_hierarchy_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_approval_hierarchy(approval_hierarchy_id):
    approval_hierarchy = ApprovalHierarchy(approval_hierarchy_id)

    if request.method == 'GET':
        result = approval_hierarchy.read()
        if result is None:
            return jsonify({'message': 'Approval hierarchy not found'}), 404
        else:
            return jsonify(result), 200

    elif request.method == 'PUT':
        data = request.json
        approval_hierarchy.update(data.get('name'), data.get('account_id'))
        return jsonify({'message': 'Approval hierarchy updated successfully'}), 200

    elif request.method == 'DELETE':
        approval_hierarchy.delete()
        return jsonify({'message': 'Approval hierarchy deleted successfully'}), 200


@app.route('/discrepancy', methods=['POST'])
def create_discrepancy():
    data = request.json
    discrepancy = Discrepancy(None, data['account_id'])
    discrepancy.create(
        data.get('document_type'),
        data.get('document_number'),
        data.get('customer_id'),
        data.get('supplier_id'),
        data.get('discrepancy_type'),
        data.get('document_amount'),
        data.get('expected_amount')
    )
    return jsonify({'message': 'Discrepancy created successfully', 'id': discrepancy.id}), 201


@app.route('/discrepancy/get-all/<account_id>', methods=['GET'])
def get_all_discrepancies(account_id):
    discrepancy = Discrepancy('', account_id)
    if request.method == 'GET':
        result = discrepancy.read_all()
        if result is None:
            return jsonify({'message': 'No discrepancies found'}), 404
        else:
            return jsonify(result), 200


@app.route('/discrepancy/<discrepancy_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_discrepancy(discrepancy_id):
    discrepancy = Discrepancy(discrepancy_id)

    if request.method == 'GET':
        result = discrepancy.read()
        if result is None:
            return jsonify({'message': 'Discrepancy not found'}), 404
        else:
            return jsonify(result), 200

    elif request.method == 'PUT':
        data = request.json
        discrepancy.update(
            data.get('document_type'),
            data.get('document_number'),
            data.get('customer_id'),
            data.get('supplier_id'),
            data.get('discrepancy_type'),
            data.get('document_amount'),
            data.get('expected_amount')
        )
        return jsonify({'message': 'Discrepancy updated successfully'}), 200

    elif request.method == 'DELETE':
        discrepancy.delete()
        return jsonify({'message': 'Discrepancy deleted successfully'}), 200


@app.route('/integration', methods=['POST'])
def create_integration():
    data = request.json
    integration = Integration()
    integration.create(
        data.get('name'),
        data.get('kms_key_arn'),
        data.get('endpoint_url'),
        data.get('status'),
        data.get('account_id')
    )
    return jsonify({'message': 'Integration created successfully', 'id': integration.id}), 201


@app.route('/integration/get-all/<account_id>', methods=['GET'])
def get_all_integrations(account_id):
    integration = Integration('', account_id)
    if request.method == 'GET':
        result = integration.read_all()
        if result is None:
            return jsonify({'message': 'No discrepancies found'}), 404
        else:
            return jsonify(result), 200


@app.route('/integration/<integration_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_integration(integration_id):
    integration = Integration(integration_id)

    if request.method == 'GET':
        result = integration.read()
        if result is None:
            return jsonify({'message': 'Integration not found'}), 404
        else:
            return jsonify(result), 200

    elif request.method == 'PUT':
        data = request.json
        integration.update(
            data.get('name'),
            data.get('kms_key_arn'),
            data.get('endpoint_url'),
            data.get('status'),
            data.get('account_id')
        )
        return jsonify({'message': 'Integration updated successfully'}), 200

    elif request.method == 'DELETE':
        integration.delete()
        return jsonify({'message': 'Integration deleted successfully'}), 200


@app.route('/permission', methods=['POST'])
def create_permission():
    data = request.json
    permission = Permission()
    permission.create(data.get('permission_name'))
    return jsonify({'message': 'Permission created successfully', 'id': permission.id}), 201


@app.route('/permission/<permission_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_permission(permission_id):
    permission = Permission(permission_id)

    if request.method == 'GET':
        result = permission.read()
        if result is None:
            return jsonify({'message': 'Permission not found'}), 404
        else:
            return jsonify(result), 200

    elif request.method == 'PUT':
        data = request.json
        permission.update(data.get('permission_name'))
        return jsonify({'message': 'Permission updated successfully'}), 200

    elif request.method == 'DELETE':
        permission.delete()
        return jsonify({'message': 'Permission deleted successfully'}), 200


@app.route('/role', methods=['POST'])
def create_role():
    data = request.json
    role = Role()
    role.create(data.get('role_name'), data.get('account_id'))
    return jsonify({'message': 'Role created successfully', 'id': role.id}), 201


@app.route('/role/<role_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_role(role_id):
    role = Role(role_id)

    if request.method == 'GET':
        result = role.read()
        if result is None:
            return jsonify({'message': 'Role not found'}), 404
        else:
            return jsonify(result), 200

    elif request.method == 'PUT':
        data = request.json
        role.update(data.get('role_name'), data.get('account_id'))
        return jsonify({'message': 'Role updated successfully'}), 200

    elif request.method == 'DELETE':
        role.delete()
        return jsonify({'message': 'Role deleted successfully'}), 200


@app.route('/role_permission', methods=['POST'])
def create_role_permission():
    data = request.json
    role_permission = RolePermission()
    role_permission.create(data.get('role_id'), data.get('permission_id'))
    return jsonify({'message': 'Role permission created successfully', 'id': role_permission.id}), 201


@app.route('/role_permission/<role_permission_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_role_permission(role_permission_id):
    role_permission = RolePermission(role_permission_id)

    if request.method == 'GET':
        result = role_permission.read()
        if result is None:
            return jsonify({'message': 'Role permission not found'}), 404
        else:
            return jsonify(result), 200

    elif request.method == 'PUT':
        data = request.json
        role_permission.update(data.get('role_id'), data.get('permission_id'))
        return jsonify({'message': 'Role permission updated successfully'}), 200

    elif request.method == 'DELETE':
        role_permission.delete()
        return jsonify({'message': 'Role permission deleted successfully'}), 200


@app.route('/user_roles', methods=['POST'])
def create_user_role():
    data = request.json
    user_id = data.get('user_id')
    role_id = data.get('role_id')
    user_roles = UserRoles(user_id, role_id)
    user_roles.create()
    return jsonify({'message': 'User role created successfully'}), 201


@app.route('/user_roles', methods=['DELETE'])
def delete_user_role():
    data = request.json
    user_id = data.get('user_id')
    role_id = data.get('role_id')
    user_roles = UserRoles(user_id, role_id)
    user_roles.delete()
    return jsonify({'message': 'User role deleted successfully'}), 200


@app.route('/approvers/get-all/<hierarchy_id>', methods=['GET'])
def read_all_approvers(hierarchy_id):
    approver = Approver(hierarchy_id=hierarchy_id)
    result = approver.read_all()
    if not result:
        return jsonify({'message': 'No approvers found for the specified hierarchy'}), 404
    else:
        return jsonify(result), 200


@app.route('/approvers', methods=['POST'])
def create_approver():
    data = request.json
    approver = Approver()
    approver.level = data.get('level')
    approver.approver = data.get('approver')
    approver.hierarchy_id = data.get('hierarchy_id')
    approver.create()
    return jsonify({'message': 'Approver created successfully', 'id': approver.id}), 201


@app.route('/approvers/<approver_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_approver(approver_id):
    approver = Approver(id=approver_id)

    if request.method == 'GET':
        result = approver.read()
        if not result:
            return jsonify({'message': 'Approver not found'}), 404
        else:
            return jsonify(result), 200

    elif request.method == 'PUT':
        data = request.json
        approver.level = data.get('level')
        approver.approver = data.get('approver')
        approver.hierarchy_id = data.get('hierarchy_id')
        approver.update()
        return jsonify({'message': 'Approver updated successfully'}), 200

    elif request.method == 'DELETE':
        approver.delete()
        return jsonify({'message': 'Approver deleted successfully'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0')
