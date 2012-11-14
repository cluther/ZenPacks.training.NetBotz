from zope.interface import implements

from Products.ZenModel.Device import Device
from Products.ZenRelations.RelSchema import ToManyCont, ToOne
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.device import DeviceInfo
from Products.Zuul.interfaces.device import IDeviceInfo
from Products.Zuul.utils import ZuulMessageFactory as _t


## Model Class

class NetBotzDevice(Device):
    temp_sensor_count = None

    _properties = Device._properties + (
        {'id': 'temp_sensor_count', 'type': 'int'},
        )

    _relations = Device._relations + (
        ('temperature_sensors', ToManyCont(ToOne,
            'ZenPacks.training.NetBotz.TemperatureSensor',
            'sensor_device',
            )),
        )


## API: Info Interface

class INetBotzDeviceInfo(IDeviceInfo):
    temp_sensor_count = schema.Int(title=_t('Number of Temperature Sensors'))


## API: Info Adapter

class NetBotzDeviceInfo(DeviceInfo):
    implements(INetBotzDeviceInfo)

    temp_sensor_count = ProxyProperty('temp_sensor_count')

