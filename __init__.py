# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import carrier


def register():
    Pool.register(
        carrier.Carrier,
        carrier.CarrierFileWizardStart,
        carrier.ShipmentOut,
        module='carrier_file', type_='model')
    Pool.register(
        carrier.CarrierFileWizard,
        module='carrier_file', type_='wizard')
