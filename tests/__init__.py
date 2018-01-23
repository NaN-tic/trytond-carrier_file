# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
try:
    from trytond.modules.carrier_file.tests.test_carrier_file import suite
except ImportError:
    from .test_carrier_file import suite

__all__ = ['suite']
