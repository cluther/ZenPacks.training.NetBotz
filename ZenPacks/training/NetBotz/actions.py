import logging
LOG = logging.getLogger('zen.NetBotz')

from zope.interface import implements

from Products.ZenModel.actions import IActionBase, _signalToContextDict
from Products.ZenModel.interfaces import IAction
from Products.ZenUtils.guid.guid import GUIDManager
from Products.Zuul.form import schema
from Products.Zuul.infos import InfoBase
from Products.Zuul.infos.actions import ActionFieldProperty
from Products.Zuul.interfaces import IInfo
from Products.Zuul.utils import ZuulMessageFactory as _t


class ISpeakActionContentInfo(IInfo):
    volume = schema.Int(
        title=_t(u'Volume'),
        description=_t(u'How loud Zenoss will speak.'),
        default=11,
        )


class SpeakActionContentInfo(InfoBase):
    implements(ISpeakActionContentInfo)

    volume = ActionFieldProperty(ISpeakActionContentInfo, 'volume')


class SpeakAction(IActionBase):
    implements(IAction)

    id = 'speak'
    name = 'Speak'

    actionContentInfo = ISpeakActionContentInfo

    def setupAction(self, dmd):
        self.guidManager = GUIDManager(dmd)

    def updateContent(self, content=None, data=None):
        content['volume'] = data.get('volume')

    def execute(self, notification, signal):
        evt = _signalToContextDict(signal, '').get('evt')
        if not evt:
            return

        LOG.debug("DEBUG: %r", evt.__dict__)

