=====================
Carrier File Scenario
=====================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from proteus import config, Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> today = datetime.date.today()
    >>> yesterday = today - relativedelta(days=1)

Activate carrier_file Module::

    >>> config = activate_modules('carrier_file')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']
    >>> cash = accounts['cash']

Create tax::

    >>> tax = create_tax(Decimal('.10'))
    >>> tax.save()

Create payment term::

    >>> payment_term = create_payment_term()
    >>> payment_term.save()

Create customer::

    >>> Party = Model.get('party.party')
    >>> customer = Party(name='Customer')
    >>> customer.save()

Create carrier::

    >>> pcarrier = Party(name='Carrier')
    >>> pcarrier.save()

Create account category::

    >>> Tax = Model.get('account.tax')
    >>> ProductCategory = Model.get('product.category')
    >>> account_category = ProductCategory(name="Account Category")
    >>> account_category.accounting = True
    >>> account_category.account_expense = expense
    >>> account_category.account_revenue = revenue
    >>> account_category.customer_taxes.append(tax)
    >>> account_category.supplier_taxes.append(Tax(tax.id))
    >>> account_category.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> product = Product()
    >>> template = ProductTemplate()
    >>> template.name = 'Product'
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.list_price = Decimal('20')
    >>> template.salable = True
    >>> template.account_category = account_category
    >>> template.save()
    >>> product.template = template
    >>> product.save()

Create Carriers::

    >>> cproduct = Product()
    >>> template = ProductTemplate()
    >>> template.name = 'Product Carrier'
    >>> template.default_uom = unit
    >>> template.type = 'service'
    >>> template.list_price = Decimal('10')
    >>> template.salable = True
    >>> template.account_category = account_category
    >>> template.save()
    >>> cproduct.template = template
    >>> cproduct.save()

    >>> FileFormat = Model.get('file.format')
    >>> Carrier = Model.get('carrier')

    >>> dexpress_fileformat, = FileFormat.find([('name', '=', 'DynamicExpress')], limit=1)
    >>> dexpress_fileformat.path = '/tmp'
    >>> dexpress_fileformat.save()
    >>> dexpress = Carrier()
    >>> dexpress.party = pcarrier
    >>> dexpress.carrier_product = cproduct
    >>> dexpress.carrier_cost_method = 'product'
    >>> dexpress.format = dexpress_fileformat
    >>> dexpress.save()

    >>> dexpresscomplete_fileformat, = FileFormat.find([('name', '=', 'DynamicExpress Complete')], limit=1)
    >>> dexpresscomplete_fileformat.path = '/tmp'
    >>> dexpresscomplete_fileformat.save()
    >>> dexpresscomplete = Carrier()
    >>> dexpresscomplete.party = pcarrier
    >>> dexpresscomplete.carrier_product = cproduct
    >>> dexpresscomplete.carrier_cost_method = 'product'
    >>> dexpresscomplete.format = dexpresscomplete_fileformat
    >>> dexpresscomplete.save()

    >>> mrw_fileformat, = FileFormat.find([('name', '=', 'MRW')], limit=1)
    >>> mrw_fileformat.path = '/tmp'
    >>> mrw_fileformat.save()
    >>> mrw = Carrier()
    >>> mrw.party = pcarrier
    >>> mrw.carrier_product = cproduct
    >>> mrw.carrier_cost_method = 'product'
    >>> mrw.format = mrw_fileformat
    >>> mrw.save()

    >>> seur_fileformat, = FileFormat.find([('name', '=', 'SEUR')], limit=1)
    >>> seur_fileformat.path = '/tmp'
    >>> seur_fileformat.save()
    >>> seur = Carrier()
    >>> seur.party = pcarrier
    >>> seur.carrier_product = cproduct
    >>> seur.carrier_cost_method = 'product'
    >>> seur.format = seur_fileformat
    >>> seur.save()

    >>> tipsa_fileformat, = FileFormat.find([('name', '=', 'TIPSA')], limit=1)
    >>> tipsa_fileformat.path = '/tmp'
    >>> tipsa_fileformat.save()
    >>> tipsa = Carrier()
    >>> tipsa.party = pcarrier
    >>> tipsa.carrier_product = cproduct
    >>> tipsa.carrier_cost_method = 'product'
    >>> tipsa.format = tipsa_fileformat
    >>> tipsa.save()

    >>> ups_fileformat, = FileFormat.find([('name', '=', 'UPS')], limit=1)
    >>> ups_fileformat.path = '/tmp'
    >>> ups_fileformat.save()
    >>> ups = Carrier()
    >>> ups.party = pcarrier
    >>> ups.carrier_product = cproduct
    >>> ups.carrier_cost_method = 'product'
    >>> ups.format = seur_fileformat
    >>> ups.save()

Get stock locations::

    >>> Location = Model.get('stock.location')
    >>> warehouse_loc, = Location.find([('code', '=', 'WH')])
    >>> supplier_loc, = Location.find([('code', '=', 'SUP')])
    >>> customer_loc, = Location.find([('code', '=', 'CUS')])
    >>> output_loc, = Location.find([('code', '=', 'OUT')])
    >>> storage_loc, = Location.find([('code', '=', 'STO')])

Make 100 unit of the product available::

    >>> StockMove = Model.get('stock.move')
    >>> incoming_move = StockMove()
    >>> incoming_move.product = product
    >>> incoming_move.uom = unit
    >>> incoming_move.quantity = 100
    >>> incoming_move.from_location = supplier_loc
    >>> incoming_move.to_location = storage_loc
    >>> incoming_move.planned_date = today
    >>> incoming_move.effective_date = today
    >>> incoming_move.company = company
    >>> incoming_move.unit_price = Decimal('1')
    >>> incoming_move.currency = company.currency
    >>> incoming_move.click('do')

Create Sales::

    >>> Sale = Model.get('sale.sale')
    >>> SaleLine = Model.get('sale.line')

    >>> for scarrier in [dexpress, dexpresscomplete, mrw, seur, tipsa, ups]:
    ...     sale = Sale()
    ...     sale.party = customer
    ...     sale.payment_term = payment_term
    ...     sale.shipment_method = 'order'
    ...     sale.carrier = scarrier
    ...     sale_line = SaleLine()
    ...     sale.lines.append(sale_line)
    ...     sale_line.product = product
    ...     sale_line.quantity = 1.0
    ...     sale.save()

Confirm Sales::

    >>> sale1, sale2, sale3, sale4, sale5, sale6 = Sale.find([])

    >>> sale1.click('quote')
    >>> sale1.click('confirm')
    >>> sale1.click('process')
    >>> sale1.reload()
    >>> shipment, = sale1.shipments
    >>> shipment.click('wait')
    >>> shipment.click('assign_try')
    >>> shipment.click('pick')
    >>> shipment.click('pack')
    >>> shipment.click('done')
    >>> shipment.state
    'done'
    >>> file_name = shipment.carrier.format.path+'/'+shipment.carrier.format.file_name
    >>> file = open(file_name, 'r')
    >>> fcontent = file.read()
    >>> file.close()
    >>> 'Customer' in fcontent
    True

    >>> sale2.click('quote')
    >>> sale2.click('confirm')
    >>> sale2.click('process')
    >>> sale2.reload()
    >>> shipment, = sale2.shipments
    >>> shipment.click('wait')
    >>> shipment.click('assign_try')
    >>> shipment.click('pick')
    >>> shipment.click('pack')
    >>> shipment.click('done')
    >>> shipment.state
    'done'
    >>> file_name = shipment.carrier.format.path+'/'+shipment.carrier.format.file_name
    >>> file = open(file_name, 'r')
    >>> fcontent = file.read()
    >>> file.close()
    >>> 'Customer' in fcontent
    True

    >>> sale3.click('quote')
    >>> sale3.click('confirm')
    >>> sale3.click('process')
    >>> sale3.reload()
    >>> shipment, = sale3.shipments
    >>> shipment.click('wait')
    >>> shipment.click('assign_try')
    >>> shipment.click('pick')
    >>> shipment.click('pack')
    >>> shipment.click('done')
    >>> shipment.state
    'done'
    >>> file_name = shipment.carrier.format.path+'/'+shipment.carrier.format.file_name
    >>> file = open(file_name, 'r')
    >>> fcontent = file.read()
    >>> file.close()
    >>> 'Customer' in fcontent
    True

    >>> sale4.click('quote')
    >>> sale4.click('confirm')
    >>> sale4.click('process')
    >>> sale4.reload()
    >>> shipment, = sale4.shipments
    >>> shipment.click('wait')
    >>> shipment.click('assign_try')
    >>> shipment.click('pick')
    >>> shipment.click('pack')
    >>> shipment.click('done')
    >>> shipment.state
    'done'
    >>> file_name = shipment.carrier.format.path+'/'+shipment.carrier.format.file_name
    >>> file = open(file_name, 'r')
    >>> fcontent = file.read()
    >>> file.close()
    >>> 'Customer' in fcontent
    True

    >>> sale5.click('quote')
    >>> sale5.click('confirm')
    >>> sale5.click('process')
    >>> sale5.reload()
    >>> shipment, = sale5.shipments
    >>> shipment.click('wait')
    >>> shipment.click('assign_try')
    >>> shipment.click('pick')
    >>> shipment.click('pack')
    >>> shipment.click('done')
    >>> shipment.state
    'done'
    >>> file_name = shipment.carrier.format.path+'/'+shipment.carrier.format.file_name
    >>> file = open(file_name, 'r')
    >>> fcontent = file.read()
    >>> file.close()
    >>> 'Customer' in fcontent
    True

    >>> sale6.click('quote')
    >>> sale6.click('confirm')
    >>> sale6.click('process')
    >>> sale6.reload()
    >>> shipment, = sale6.shipments
    >>> shipment.click('wait')
    >>> shipment.click('assign_try')
    >>> shipment.click('pick')
    >>> shipment.click('pack')
    >>> shipment.click('done')
    >>> shipment.state
    'done'
    >>> file_name = shipment.carrier.format.path+'/'+shipment.carrier.format.file_name
    >>> file = open(file_name, 'r')
    >>> fcontent = file.read()
    >>> file.close()
    >>> 'Customer' in fcontent
    True
