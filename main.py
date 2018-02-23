import asyncio
import inspect
import logging
import os
import sys
from panoramisk import Manager
import statsd

# Pometheus push gateway
STATSD_HOST = os.environ.get('STATSD_HOST', 'localhost:9125')
AMI_HOST = os.environ.get('AMI_HOST', 'localhost')
AMI_PORT = os.environ.get('AMI_PORT', '5038')
AMI_USER = os.environ.get('AMI_USER', 'asterisk')
AMI_SECRET = os.environ.get('AMI_SECRET', 'secret')

stats = statsd.StatsClient(*STATSD_HOST.split(':'))

loop = asyncio.get_event_loop()

# Asterisk AMI manager client
manager = Manager(loop=loop,
                  host=AMI_HOST, port=AMI_PORT,
                  username=AMI_USER,
                  secret=AMI_SECRET)
#manager.loop.set_debug(True)

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)

channels_current = {} # Current channels counter


def main():
    logger.info('Connecting to {}:{}.'.format(AMI_HOST, AMI_PORT))
    manager.connect()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()


@manager.register_event('FullyBooted')
def on_asterisk_FullyBooted(manager, message):
    if message.Uptime:
        stats.gauge('asterisk_uptime', int(message.Uptime))
    if message.LastReload:
        stats.gauge('asterisk_last_reload', int(message.LastReload))
    # Get initial channels
    ShowChannels = yield from manager.send_action({'Action': 'CoreShowChannels'})
    channels = list(filter(lambda x: x.Event == 'CoreShowChannel', ShowChannels))
    sip_channels = len(list(filter(lambda x: x.Channel.startswith('SIP/'), channels)))
    iax2_channels = len(list(filter(lambda x: x.Channel.startswith('IAX2/'), channels)))
    dahdi_channels = len(list(filter(lambda x: x.Channel.startswith('DAHDI/'), channels)))
    local_channels = len(list(filter(lambda x: x.Channel.startswith('Local/'), channels)))
    channels_current['sip'] = sip_channels
    channels_current['iax2'] = iax2_channels
    channels_current['dahdi'] = dahdi_channels
    channels_current['local'] = local_channels
    sip_channels and stats.gauge('asterisk_channels_current', sip_channels, tags={'channel':'sip'})
    iax2_channels and stats.gauge('asterisk_channels_current', iax2_channels, tags={'channel':'iax2'})
    sip_channels and stats.gauge('asterisk_channels_current', sip_channels, tags={'channel':'sip'})


@manager.register_event('Newchannel')
def on_asterisk_Newchannel(manager, message):
    m = message
    channel=m.Channel.split('/')[0].lower()
    stats.incr('asterisk_channels_total', tags={'channel': channel})
    if channels_current.get(channel):
        channels_current[channel] += 1
    else:
        channels_current[channel] = 0
    logger.debug('New channel {}, current: {}'.format(channel, channels_current[channel]))
    stats.gauge('asterisk_channels_current', channels_current[channel],
                tags={'channel':channel})


@manager.register_event('Hangup')
def on_asterisk_Hangup(manager, message):
    m = message
    channel=m.Channel.split('/')[0].lower()
    if channels_current.get(channel):
        channels_current[channel] -= 1
    else:
        channels_current[channel] = 0
    logger.debug('Channel {} hangup, current: {}'.format(channel, channels_current[channel]))
    stats.gauge('asterisk_channels_current', channels_current[channel],
                tags={'channel':channel})


def on_asterisk_DialBegin(manager, message):
    print (message)


def on_asterisk_DialEnd(manager, message):
    print (message)


def on_asterisk_Reload(manager, message):
    print (message)



if __name__ == '__main__':
    main()
