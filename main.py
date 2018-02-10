import asyncio
import inspect
import logging
import sys
from panoramisk import Manager
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

# Pometheus push gateway
PUSHGATEWAY = 'localhost:9091'

registry = CollectorRegistry()
uptime = Gauge('asterisk_uptime', 'Asterisk time since start', registry=registry)
last_reload = Gauge('asterisk_last_reload', 'Asterisk last reload', registry=registry)
#channels = Gauge('asterisk_channels_total', 'Asterisk Active Channels',
#                ['channel', 'calleridname','context','cause','cause_txt','exten'],
#                registry=registry)
channels = Gauge('asterisk_channels_total', 'Asterisk Active Channels',
                ['channel'], registry=registry)

# Asterisk AMI manager client
manager = Manager(loop=asyncio.get_event_loop(),
                  host='localhost',
                  username='odoo',
                  secret='odoo')
#manager.loop.set_debug(True)

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)


def main():
    manager.connect()
    try:
        manager.loop.run_forever()
    except KeyboardInterrupt:
        manager.loop.close()


@manager.register_event('FullyBooted')
def on_asterisk_FullyBooted(manager, message):
    uptime.set(message.Uptime)
    last_reload.set(message.LastReload)
    # Get initial channels
    ShowChannels = yield from manager.send_action({'Action': 'CoreShowChannels'})
    calls = list(filter(lambda x: x.Event == 'CoreShowChannel', ShowChannels))
    sip_calls = len(list(filter(lambda x: x.Channel.startswith('SIP/'), calls)))
    iax2_calls = len(list(filter(lambda x: x.Channel.startswith('IAX2/'), calls)))
    dahdi_calls = len(list(filter(lambda x: x.Channel.startswith('DAHDI/'), calls)))
    channels.labels(channel='sip').set(sip_calls)
    channels.labels(channel='iax2').set(iax2_calls)
    channels.labels(channel='dahdi').set(dahdi_calls)
    push_to_gateway(PUSHGATEWAY, job='asterisk', registry=registry)


@manager.register_event('Newchannel')
def on_asterisk_Newchannel(manager, message):
    m = message
    channels.labels(channel=m.Channel.split('/')[0].lower(),
             #calleridnum=m.CallerIDNum,
             #calleridname=m.CallerIDName,
             #context=m.Context,
             #exten=m.Exten
             ).inc()
    push_to_gateway(PUSHGATEWAY, job='asterisk', registry=registry)


@manager.register_event('Hangup')
def on_asterisk_Hangup(manager, message):
    m = message
    channels.labels(channel=m.Channel.split('/')[0].lower(),
             #calleridnum=m.CallerIDNum,
             #alleridname=m.CallerIDName,
             #context=m.Context,
             #cause=m.Cause,
             #cause_txt=m.get('Cause-txt'),
             #exten=m.Exten
             ).dec()
    push_to_gateway(PUSHGATEWAY, job='asterisk', registry=registry)


def on_asterisk_DialBegin(manager, message):
    print (message)


def on_asterisk_DialEnd(manager, message):
    print (message)


def on_asterisk_Reload(manager, message):
    print (message)



if __name__ == '__main__':
    main()
