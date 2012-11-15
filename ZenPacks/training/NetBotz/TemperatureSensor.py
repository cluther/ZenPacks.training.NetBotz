from zope.interface import implements

from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.ZenModel.ZenossSecurity import ZEN_CHANGE_DEVICE
from Products.ZenRelations.RelSchema import ToManyCont, ToOne
from Products.Zuul.decorators import info
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.component import ComponentInfo
from Products.Zuul.interfaces.component import IComponentInfo
from Products.Zuul.utils import ZuulMessageFactory as _t


class TemperatureSensor(DeviceComponent, ManagedEntity):
    meta_type = portal_type = 'NetBotzTemperatureSensor'

    # Fields inherited from DeviceComponent and ManagedEntity
    #   id, title, snmpindex

    port = None

    _properties = ManagedEntity._properties + (
        {'id': 'port', 'type': 'string'},
        )

    _relations = ManagedEntity._relations + (
        ('enclosure', ToOne(ToManyCont,
            'ZenPacks.training.NetBotz.Enclosure',
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
        return self.enclosure().device()

    def getRRDTemplateName(self):
        return 'TemperatureSensor'


class ITemperatureSensorInfo(IComponentInfo):

    # enclosure is schema.Entity because it will return an object. Not text.
    enclosure = schema.Entity(title=_t('Sensor Enclosure ID'))

    port = schema.TextLine(title=_t('Sensor Port ID'))


class TemperatureSensorInfo(ComponentInfo):
    implements(ITemperatureSensorInfo)

    port = ProxyProperty('port')

    @property
    @info
    def enclosure(self):
        """Return the Enclosure object because ITemperatureInfo defines this
        property as an Entity."""

        return self._object.enclosure()

