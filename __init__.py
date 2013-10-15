#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.

from trytond.pool import Pool
from carrier import *


def register():
    Pool.register(
        Carrier,
        CarrierFileWizardStart,
        ShipmentOut,
        module='carrier_file', type_='model')
    Pool.register(
        CarrierFileWizard,
        module='carrier_file', type_='wizard')
