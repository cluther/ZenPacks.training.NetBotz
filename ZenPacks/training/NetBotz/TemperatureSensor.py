from zope.interface import implements

from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.ZenModel.ZenossSecurity import ZEN_CHANGE_DEVICE
from Products.ZenRelations.RelSchema import ToManyCont, ToOne
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.component import ComponentInfo
from Products.Zuul.interfaces.component import IComponentInfo
from Products.Zuul.utils import ZuulMessageFactory as _t


class TemperatureSensor(DeviceComponent, ManagedEntity):
    meta_type = portal_type = 'NetBotzTemperatureSensor'

    # Fields inherited from DeviceComponent and ManagedEntity
    #   id, title, snmpindex

    enclosure = None
    port = None

    _properties = ManagedEntity._properties + (
        {'id': 'enclosure', 'type': 'string'},
        {'id': 'port', 'type': 'string'},
        )

    _relations = ManagedEntity._relations + (
        ('sensor_device', ToOne(ToManyCont,
            'ZenPacks.training.NetBotz.NetBotzDevice',
            'temperature_sensors',
            )),
        )

    factory_type_information = ({
        'actions': ({
            'id': 'perfConf',
            'name': 'Template',
            'action': 'objTemplates',
            'permissions': (ZEN_CHANGE_DEVICE,),
            },),
        },)

    def device(self):
        return self.sensor_device()

    def getRRDTemplateName(self):
        return 'TemperatureSensor'


class ITemperatureSensorInfo(IComponentInfo):
    enclosure = schema.TextLine(title=_t('Sensor Enclosure ID'))
    port = schema.TextLine(title=_t('Sensor Port ID'))


class TemperatureSensorInfo(ComponentInfo):
    implements(ITemperatureSensorInfo)

    enclosure = ProxyProperty('enclosure')
    port = ProxyProperty('port')

