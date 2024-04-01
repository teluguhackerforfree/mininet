from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node, Controller, RemoteController
from mininet.log import setLogLevel, info
import logging
import os
from mininet.cli import CLI
from mininet.link import Intf

import json
from  time import sleep
from api import ApiService

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger( __name__ )

def iperfTest(myh1, myh2):
    logger.debug("Start")

 
    myh1.cmdPrint('1 > 1')
    myh1.cmdPrint('1 > 2')
    myh1.cmdPrint('1 > 3')

 
    t = 25
    
    sleep(t)
    myh1.cmdPrint('killallf')

 
    
def pingTest(net):
    logger.debug("Test all network")
    net.pingAll()

def qosSetup(test):
    baseUrl = 'http://0.0.0.0:8080'
    datapath = '0000000000000001'
    api = ApiService(baseUrl)

    
    ovsdbEndpoint = '/v1.0/conf/switches/' + datapath + '/ovsdb_addr'
    ovsdbData = "tcp:127.0.0.1:6632"
    api.put(ovsdbEndpoint, ovsdbData)
    sleep(2)


    
    if test == 1:
        queueEndpoint = '/qos/queue/' + datapath
        queueData = {
            "port_name": "s1-etmyh1",
            "type": "linux-htb",
            "mr": "1000000",
            "queues": [{"mr": "100000"},
                    {"mr": "200000"},
                    {"mr": "300000"},
                    {"min_rate": "800000"}]
        }

        api.post(queueEndpoint, queueData)
    else:
        queueEndpoint = '/qos/queue/' + datapath
        queueData = {
            "port_name": "s1-etmyh1",
            "type": "linux-htb",
            "mr": "1000000",
            "queues": [{"mr": "200000"},
                    {"mr": "300000"},
                    {"mr": "100000"},
                    {"min_rate": "800000"}]
        }
        api.post(queueEndpoint, queueData)


    ruleEndpoint = '/qos/rules/' + datapath
    
    ruleData1 = {"match": {"nw_dst": "10.0.0.1", "nw_proto": "UDP", "tp_dst": "5001"}, "actions":{"queue": "0"}}
    ruleData2 = {"match": {"nw_dst": "10.0.0.1", "nw_proto": "UDP", "tp_dst": "5002"}, "actions":{"queue": "1"}}
    ruleData3 = {"match": {"nw_dst": "10.0.0.1", "nw_proto": "UDP", "tp_dst": "5003"}, "actions":{"queue": "2"}}
    
    api.post(ruleEndpoint, ruleData1)
    api.post(ruleEndpoint, ruleData2)
    api.post(ruleEndpoint, ruleData3)



class MyTopo( Topo ):
    

    def build( self, **opts ):

        # add switches
        s1 = self.addSwitch( 's1' )
        s2 = self.addSwitch( 's2' )

        # add hosts
        myh1 = self.addHost( 'myh1' )
        myh2 = self.addHost( 'myh2' )
        
        self.addLink( myh1, s1 )
        self.addLink( myh2, s2 )
        self.addLink( s1, s2 )


def run():
    topo = MyTopo()
    net = Mininet( topo=topo, controller=RemoteController, autoSetMacs=True )
    net.start()

    # Get nodes
    s1 = net.get( 's1' )
    s2 = net.get( 's2' )
    myh1 = net.get('myh1')
    myh2 = net.get('myh2')

    
    
    
    sleep(3)

    # Configurar protocolo y manager
    
    s1.cmd( 'protocols' )
    
    s2.cmd( 'protocols=13' )
    
    s1.cmd( 'ptcp:6632' )
    s2.cmd( 'ptcp:6632' )

    
    info( 'QoS...' )
    try:
        qosSetup(1) 
        sleep(2)
    except ValueError:
        print('Error....')
    

    myh1.cmdPrint('Network')
    sleep(5)
    

    iperfTest(myh1, myh2)
    qosSetup(2)
    iperfTest(myh1, myh2)
    qosSetup(1)
    iperfTest(myh1, myh2)


    CLI( net )
    net.stop()
    
    s1.cmdPrint('all destroy QoS')
    s1.cmdPrint('all destroy queue')
    sleep(2)
    
if __name__ == '__main__':
    setLogLevel( 'info' )
    run()
