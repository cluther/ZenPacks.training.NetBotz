import collections

from Products.DataCollector.plugins.CollectorPlugin import (
    SnmpPlugin, GetTableMap,
    )

from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap


def lookup_OperStatus(value):
    """Return string given a NETBOTZB2-MIB::OperStatus value."""
    return {
        0: 'disconnected',
        1: 'error',
        2: 'normal',
        }.get(value, 'unknown')


def lookup_ErrorStatus(value):
    """Return a string given a NETBOTZV2-MIB::ErrorStatus value."""
    return {
        0: 'normal',
        1: 'info',
        2: 'warning',
        3: 'error',
        4: 'critical',
        5: 'failure',
        }.get(value, 'unknown')


class NetBotz(SnmpPlugin):
    snmpGetTableMaps = (
        GetTableMap(
            'enclosureTable', '1.3.6.1.4.1.5528.100.2.1.1', {
                '.1': 'enclosureId',
                '.2': 'enclosureStatus',
                '.3': 'enclosureErrorStatus',
                '.4': 'enclosureLabel',
                '.5': 'enclosureParentEncId',
                '.6': 'enclosureDockedToEncId',
                }
            ),

        GetTableMap(
            'tempSensorTable', '1.3.6.1.4.1.5528.100.4.1.1.1', {
                '.1': 'tempSensorId',
                '.5': 'tempSensorEncId',
                '.6': 'tempSensorPortId',
                }
            ),
        )

    def process(self, device, results, log):
        enclosures = results[1].get('enclosureTable', {})
        temp_sensors = results[1].get('tempSensorTable', {})

        maps = []

        enclosure_oms = []

        for snmpindex, row in enclosures.items():
            enclosure_id = row.get('enclosureId')
            if not enclosure_id:
                log.warn('Skipping enclosure with no ID.')
                continue

            enclosure_status = lookup_OperStatus(row.get('enclosureStatus'))
            error_status = lookup_ErrorStatus(row.get('enclosureErrorStatus'))

            enclosure_oms.append(ObjectMap(data={
                'id': self.prepId(enclosure_id),
                'title': row.get('enclosureLabel') or enclosure_id,
                'snmpindex': snmpindex.strip('.'),
                'enclosure_status': enclosure_status,
                'error_status': error_status,
                'parent_id': row.get('enclosureParentEncId'),
                'docked_id': row.get('enclosureDockedToEncId'),
                }))

        maps.append(RelationshipMap(
            relname='enclosures',
            modname='ZenPacks.training.NetBotz.Enclosure',
            objmaps=enclosure_oms))

        temperature_sensor_oms = collections.defaultdict(list)

        for snmpindex, row in temp_sensors.items():
            name = row.get('tempSensorId')
            if not name:
                log.warn('Skipping temperature sensor with no name')
                continue

            enclosure_id = row.get('tempSensorEncId')
            if not enclosure_id:
                log.warn('Skipping temperature sensor with no enclosure.')
                continue

            om = ObjectMap(data={
                'id': self.prepId(name),
                'title': name,
                'snmpindex': snmpindex.strip('.'),
                'port': row.get('tempSensorPortId'),
                })

            temperature_sensor_oms[enclosure_id].append(om)

        # Device path.
        # NetBotz/devices/Netbotz01
        #
        # Enclosure path.
        # NetBotz/devices/Netbotz01/enclosures/nbHawk01_ENC_0
        #
        # Sensor path.
        # NetBotz/devices/Netbotz01/enclosures/nbHawk01_ENC_0/temperature_sensors/nbHawk01_ENC_0_TEMP1
        #
        # relname needs to be "enclosures" for an enclosure.
        # relname needs to be "temperature_sensors" for a temperature sensor.
        #
        # compname needs to be "" for an enclosure because nothing separates relname from the device.
        # compname needs to be "enclosures/nbHawk01_ENC_0" for a sensor because that's what separates
        #    its relname from the device.

        for enclosure_id, temperature_sensor_oms in temperature_sensor_oms.items():
            rm = RelationshipMap(
                compname='enclosures/%s' % self.prepId(enclosure_id),
                relname='temperature_sensors',
                modname='ZenPacks.training.NetBotz.TemperatureSensor',
                objmaps=temperature_sensor_oms)

            maps.append(rm)

        return maps

