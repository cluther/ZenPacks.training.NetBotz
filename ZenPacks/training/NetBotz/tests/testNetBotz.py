# BaseTestCase is a subclass of ZopeTestCase which is ultimately a subclass of
# Python's standard unittest.TestCase. Because of this the following
# documentation on unit testing in Zope and Python are both applicable here.
#
# Python Unit testing framework
# http://docs.python.org/library/unittest.html
#
# Zope Unit Testing
# http://wiki.zope.org/zope2/Testing

# We need zcml to load our ZenPack's configure.zcml. This is not automatically
# done by the runtests framework.

import logging
LOG = logging.getLogger('zen.NetBotz')

from Products.Five import zcml

from Products.ZenTestCase.BaseTestCase import BaseTestCase


class TestNetBotz(BaseTestCase):
    def afterSetUp(self):
        # You can use the afterSetUp method to create a proper environment for
        # your tests to execute in, or to run common code between the tests.

        #Always call the base class's afterSetUp method first, so things like self.dmd will be available.
        super(TestNetBotz, self).afterSetUp()

        import ZenPacks.training.NetBotz
        zcml.load_config('configure.zcml', ZenPacks.training.NetBotz)

        deviceclass = self.dmd.Devices.createOrganizer('/NetBotz')
        deviceclass.setZenProperty('zPythonClass', 'ZenPacks.training.NetBotz.NetBotzDevice')
        self.device = deviceclass.createInstance('testDevice')

    def testImportModelClasses(self):
        """Make sure that all of our custom model classes import."""

        from ZenPacks.training.NetBotz.NetBotzDevice import NetBotzDevice
        from ZenPacks.training.NetBotz.Enclosure import Enclosure
        from ZenPacks.training.NetBotz.TemperatureSensor import TemperatureSensor

    def testEnclosure(self):
        """Test the Enclosure class."""

        from ZenPacks.training.NetBotz.Enclosure import Enclosure
        enclosure1 = Enclosure('enclosure1')
        self.assertEquals(enclosure1.getRRDTemplateName(), 'Enclosure')

    def testTemperatureSensor(self):
        """Test the TemperatureSensor class."""

        from ZenPacks.training.NetBotz.Enclosure import Enclosure
        from ZenPacks.training.NetBotz.TemperatureSensor import TemperatureSensor

        enclosure1 = Enclosure('enclosure1')
        self.device.enclosures._setObject(enclosure1.id, enclosure1)
        enclosure1 = self.device.enclosures._getOb(enclosure1.id)

        sensor1 = TemperatureSensor('sensor1')
        enclosure1.temperature_sensors._setObject(sensor1.id, sensor1)
        sensor1 = enclosure1.temperature_sensors._getOb(sensor1.id)

        self.assertEquals(sensor1.getRRDTemplateName(), 'TemperatureSensor')
        self.assertEquals(sensor1.device().id, 'testDevice')

    def testInfoAdapters(self):
        """Make sure that our Info adapters are wired correctly."""

        from Products.Zuul.interfaces import IInfo
        from ZenPacks.training.NetBotz.Enclosure import Enclosure
        from ZenPacks.training.NetBotz.TemperatureSensor import TemperatureSensor

        device_info = IInfo(self.device)
        self.assertTrue(hasattr(device_info, 'temp_sensor_count'))

        enclosure1 = Enclosure('enclosure1')
        self.device.enclosures._setObject(enclosure1.id, enclosure1)
        enclosure1 = self.device.enclosures._getOb(enclosure1.id)

        enclosure1_info = IInfo(enclosure1)
        self.assertTrue(hasattr(enclosure1_info, 'enclosure_status'))
        self.assertEquals(enclosure1_info.temperature_sensor_count, 0)

        sensor1 = TemperatureSensor('sensor1')
        enclosure1.temperature_sensors._setObject(sensor1.id, sensor1)
        sensor1 = enclosure1.temperature_sensors._getOb(sensor1.id)

        sensor1_info = IInfo(sensor1)
        self.assertTrue(hasattr(sensor1_info, 'port'))
        self.assertEquals(sensor1_info.enclosure.id, 'enclosure1')


    def testModelerPlugin(self):
        import os
        import pickle

        results_filename = os.path.join(os.path.dirname(__file__), 'data', 'netbotz.pickle')
        f = open(results_filename, 'rb')
        results = pickle.load(f)
        f.close()

        from ZenPacks.training.NetBotz.modeler.plugins.training.snmp.NetBotz import NetBotz
        plugin = NetBotz()
        datamaps = plugin.process(self.device, results, LOG)

        self.assertEquals(len(datamaps), 5)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()

    # Add your BaseTestCase subclasses here to have them executed.
    suite.addTest(makeSuite(TestNetBotz))

    return suite
