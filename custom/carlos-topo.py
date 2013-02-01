"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        client = self.addHost( 'h1' )
	client.setIP('1.0.0.1')
        router = self.addHost( 'h2' )
	client.setIP('1.0.1.1',intf='h1-eth0')
	client.setIP('2.0.1.2',intf='h1-eth1')
	server = self.addHost( 'h3' )
	client.setIP('2.0.0.1')

        #leftSwitch = self.addSwitch( 's3' )
        #rightSwitch = self.addSwitch( 's4' )

        # Add links
        #self.addLink( leftHost, leftSwitch )
	#self.addLink( leftHost, rightSwitch)
        #self.addLink( leftSwitch, rightSwitch )
        #self.addLink( rightSwitch, rightHost )
	self.addLink( client, router )
	self.addLink( server, router )


topos = { 'mytopo': ( lambda: MyTopo() ) }
