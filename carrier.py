# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import logging
from trytond.config import config
from trytond.model import ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.wizard import Wizard, StateView, StateTransition, Button
from trytond.i18n import gettext
from trytond.exceptions import UserError

PRODUCTION_ENV = config.getboolean('nantic_connection', 'production', default=False)
logger = logging.getLogger(__name__)


class Carrier(metaclass=PoolMeta):
    __name__ = 'carrier'

    format = fields.Many2One('file.format', 'File Format')

    @classmethod
    def generate_carrier_files(cls, shipments, carrier=None):
        shipment_carriers = {}
        for shipment in shipments:
            if shipment.carrier:
                if not shipment_carriers.get(shipment.carrier, False):
                    shipment_carriers[shipment.carrier] = [shipment]
                else:
                    shipment_carriers[shipment.carrier].append(shipment)

        if shipment_carriers:
            for pcarrier in shipment_carriers:
                if carrier and pcarrier == carrier:
                    pcarrier = carrier
                if pcarrier.format:
                    pcarrier.format.export_file(shipment_carriers[pcarrier])


class CarrierFileWizardStart(ModelView):
    'Carrier File Wizard Start'
    __name__ = 'carrier.file.wizard.start'

    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    carrier = fields.Many2One('carrier', 'Carrier')


class CarrierFileWizard(Wizard):
    'Carrier File Wizard'
    __name__ = 'carrier.file.wizard'

    start = StateView('carrier.file.wizard.start',
        'carrier_file.carrier_file_wizard_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Generate Files', 'generate', 'tryton-print', default=True),
            ])
    generate = StateTransition()

    def transition_generate(self):
        pool = Pool()
        Shipment = pool.get('stock.shipment.out')
        Carrier = pool.get('carrier')

        if not PRODUCTION_ENV:
            logger.warning('Production mode is not enabled.')
            return 'end'

        domain = []
        if self.start.start_date:
            domain.append(('effective_date', '>=', self.start.start_date))
        if self.start.end_date:
            domain.append(('effective_date', '<=', self.start.end_date))
        domain.append(('state', '=', 'done'))

        pickings = Shipment.search(domain)

        if not pickings:
            raise UserError(gettext('carrier_file.msg_no_shipments'))
        Carrier.generate_carrier_files(pickings, self.start.carrier)
        return 'end'


class ShipmentOut(metaclass=PoolMeta):
    __name__ = 'stock.shipment.out'

    @classmethod
    def __setup__(cls):
        super(ShipmentOut, cls).__setup__()
        cls._buttons.update({
                'generate_carrier_files': {
                    'invisible': Eval('state') != 'done',
                    },
                })

    @classmethod
    @ModelView.button
    def generate_carrier_files(cls, shipments):
        pool = Pool()
        Carrier = pool.get('carrier')

        if not PRODUCTION_ENV:
            logger.warning('Production mode is not enabled.')
            return

        Carrier.generate_carrier_files(shipments)

    @classmethod
    def do(cls, shipments):
        super(ShipmentOut, cls).do(shipments)
        cls.generate_carrier_files(shipments)
