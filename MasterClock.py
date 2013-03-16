#!/usr/bin/env python

#
# MasterClock.py
# Copyright (c) 2010-2013 Aaron C Spike
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# 

import os
from datetime import datetime, timedelta
from ConfigParser import RawConfigParser

if os.name == 'nt':
    from twisted.internet import win32eventreactor
    win32eventreactor.install()

from email.mime.text import MIMEText
from twisted.mail.smtp import sendmail
from twisted.internet import reactor, protocol, task, serialport
from lathem import to_lathem_time_string

LOOP_INTERVAL = 60.0

class Config(object):
    def __init__(self):
        self.loop_interval = 60.0
        self.debug = False
        self.debug_toggle = False
        self.smtphost = ''
        self.smtpto = ''
        self.smtpfrom = ''
        
global_config = Config()

def email(subject, msgtxt):
    msg = MIMEText(msgtxt)
    msg['Subject'] = subject
    msg['From'] = global_config.smtpfrom
    msg['To'] = ', '.join(global_config.smtpto)

    sendmail(global_config.smtphost, global_config.smtpfrom, global_config.smtpto, msg.as_string())

class Group(object):
    def __init__(self):
        group = self
        self.protocols = set([])
        class Protocol(protocol.Protocol):
            def connectionMade(self):
                print 'add', self.transport
                group.protocols.add(self)
            def connectionLost(self, reason):
                print 'remove', self.transport
                group.protocols.remove(self)
        self.protocol = Protocol
        class Factory(protocol.ReconnectingClientFactory):
            protocol = Protocol
            #maximum time between reconnection attempts in seconds
            maxDelay = 360
            reconnecting = False
            def clientConnectionFailed(self, connector, reason):
                print "Connection failed - goodbye! (%s,%s)" % (connector.host,connector.port)
                if not self.reconnecting:
                    self.reconnecting = True
                    body = '''[CLOCK] Connection with %s failed at %s''' % (str((connector.host,connector.port)), str(datetime.today()))
                    email(body, body)
                protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)                
            def clientConnectionLost(self, connector, reason):
                print "Connection lost - goodbye! (%s,%s)" % (connector.host,connector.port)
                if not self.reconnecting:
                    self.reconnecting = True
                    body = '''[CLOCK] Connection with %s lost at %s''' % (str((connector.host,connector.port)), str(datetime.today()))
                    email(body, body)
                protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
            def buildProtocol(self, addr):
                self.resetDelay()
                if self.reconnecting:
                    self.reconnecting = False
                    body = '''[CLOCK] Reconnected to %s at %s''' % (str(addr), str(datetime.today()))
                    email(body, body)
                return protocol.ReconnectingClientFactory.buildProtocol(self, addr)
        self.factory = Factory

def init_config(config_file, _reactor, group):
    '''initialize configuration
    configuration file should be in the form:
    [transports]
    ipN=host:port
    serN=COMX
    '''
    
    cp = RawConfigParser()
    cp.read(config_file)
    
    if cp.has_option('global','debug'):
        global_config.loop_interval = 5.0
        global_config.debug = True
    if cp.has_option('global','smtphost'):
        global_config.smtphost = cp.get('global','smtphost')
    if cp.has_option('global','smtpfrom'):
        global_config.smtpfrom = cp.get('global','smtpfrom')
    if cp.has_option('global','smtpto'):
        tos = [x.strip() for x in cp.get('global','smtpto').split(',')]
        global_config.smtpto = tos
        
    section = 'transports'
    for op in cp.options(section):
        value = cp.get(section, op)
        if op.startswith('ip'):
            ip, port = value.split(':')
            _reactor.connectTCP(ip, int(port), group.factory())
        elif op.startswith('ser'):
            serialport.SerialPort(group.protocol(),value,_reactor)

def writeTimeToAll(group):
    now = datetime.today()
    if global_config.debug:
        if global_config.debug_toggle:
            if now.hour >= 12:
                now = now - timedelta(hours=12)
            else:
                now = now + timedelta(hours=12)
        global_config.debug_toggle = not global_config.debug_toggle
    print now
    data = to_lathem_time_string(now)
    for p in list(group.protocols):
        p.transport.write(data)

def seconds_to_next_minute():
    now = datetime.today()
    return 60.0 - (now.second + (now.microsecond/1000000.0))
    
def start_time_loop(group, interval):
    lc = task.LoopingCall(writeTimeToAll, group)
    lc.start(interval)

def main():
    g = Group()

    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),'config.ini')
    init_config(config_file, reactor, g)
    
    # delay the initial call to the loop so that 
    # it happens on the head of each minute
    delay = seconds_to_next_minute()
    reactor.callLater(delay, start_time_loop, g, global_config.loop_interval)
    
    reactor.run()

if __name__ == '__main__':
    main()
