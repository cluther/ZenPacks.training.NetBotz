#!/usr/bin/env python
import json
import sys

from optparse import OptionParser

from twisted.internet import reactor
from twisted.python.failure import Failure
from pynetsnmp.twistedsnmp import AgentProxy


class EventSeverity:
    """Zenoss event severities."""
    Clear = 0
    Debug = 1
    Info = 2
    Warning = 3
    Error = 4
    Critical = 5


class NetBotzV2MIB:
    """NETBOTZV2-MIB"""

    tempSensorEntry = '1.3.6.1.4.1.5528.100.4.1.1.1'

    tempSensorId = '1.3.6.1.4.1.5528.100.4.1.1.1.1'
    tempSensorValueStr = '1.3.6.1.4.1.5528.100.4.1.1.1.7'


def get_cli_options():
    """Get command line options. Return them in a usable form."""

    parser = OptionParser()

    parser.add_option(
        '-H', '--host',
        dest='host',
        help='IP address of NetBotz device')

    parser.add_option(
        '-V', '--version',
        dest='version', default='v1',
        help='SNMP version to be used')

    parser.add_option(
        '-c', '--community',
        dest='community', default='public',
        help='SNMP community string')

    options, args = parser.parse_args()

    return options


def get_snmp_proxy(host, version, community):
    """Return an SNMP proxy given host, version and community."""
    snmp_proxy = AgentProxy(
        ip=host,
        community=community,
        snmpVersion=version)

    snmp_proxy.open()

    return snmp_proxy


def get_temperatures(snmp_proxy):
    def process_response(result):
        values = {}

        temp_sensor_id_map = {}
        for oid, temp_sensor_id in result.get(NetBotzV2MIB.tempSensorId, {}).items():
            temp_sensor_id_map[oid.split('.')[-1]] = temp_sensor_id

        for oid, temp_sensor_value in result.get(NetBotzV2MIB.tempSensorValueStr, {}).items():
            snmpindex = oid.split('.')[-1]
            name = temp_sensor_id_map.get(snmpindex)
            if not name:
                continue

            values[name] = {'temperature': temp_sensor_value}

        return values

    d = snmp_proxy.getTable((
        NetBotzV2MIB.tempSensorId,
        NetBotzV2MIB.tempSensorValueStr,
        ), maxRepetitions=1, limit=sys.maxint)

    d.addCallback(process_response)

    return d


def main():
    options = get_cli_options()

    if not options.host:
        print json.dumps({
            'events': [{
                'summary': 'no host specified for filesystem check',
                'eventKey': 'filesystem check',
                'eventClassKey': 'cmd_failure_netapp',
                'severity': EventSeverity.Error,
                }],
            })

        return

    snmp_proxy = get_snmp_proxy(
        options.host, options.version, options.community)


    def success(result):
        print json.dumps({
            'events': [{
                'summary': 'temperature check successful',
                'eventKey': 'temperature check',
                'eventClassKey': 'cmd_failure_netbotz',
                'severity': EventSeverity.Clear,
                }],

            'values': result,
            })

    def failure(result):
        msg = None
        if isinstance(result, Failure):
            msg = result.getErrorMessage()
        else:
            msg = str(result)

        print json.dumps({
            'events': [{
                'summary': 'netbotz check error: %s' % msg,
                'eventKey': 'netbotz check',
                'eventClassKey': 'cmd_failure_netbotz',
                'severity': EventSeverity.Error,
                'exception': str(result),
                }],
            })

    def cleanup(result):
        """Called after success or failure."""
        snmp_proxy.close()
        reactor.stop()

    d = get_temperatures(snmp_proxy)
    d.addCallback(success)
    d.addErrback(failure)
    d.addBoth(cleanup)

    reactor.run()


# If we're being called as a stand-alone script. Not imported.
if __name__ == "__main__":
    main()

