# -*- coding: utf-8 -*-

# Imports
# -------

from re import sub
from unifi.controller import Controller


# Constants
# ---------

MODELS = {'BZ2': 'UAP / UAP LR / UAP Outdoor',
          'U7P': 'UAP Pro',
          'U7E': 'UAP AC'}


# Unifi collection class
# ----------------------

class Unifi:
    """
    Helper class which collects node information from a Unifi controller instance
    that delivers networks. This polls the complete AP info using get_aps() with
    the Python bindings for the Unifi JSON API, and reformats the output to fit
    in the standard Alfred format.
    """

    # Initialization
    # --------------

    def __init__(self, host, user, pwd, port="8443", ver="v4"):
        """
        Initialize the Unifi API, binding to the controller on the specified
        host/port with the passed password and setting up the appropriate
        internal connection.

        @param host Host to connect to.
        @param user User to connect as, needs to be at least a R/O admin.
        @param pwd Password of the user to connect as.
        @param port Port that the Unifi API is listening on.
        @param ver Version of the Unifi API to use, default to v4.
        """

        # Create controller instance.
        self._controller = Controller(host, user, pwd, port, ver)
        self._owner = user
        self._stats = []

    def nodeinfo(self, gw):
        """
        Collect node information of the nodes connected to the Unifi
        controller, returning the information in a format suitable to
        later processing in a decoded form.

        @param gw Gateway to use for Unifi controller.
        @return nodeinfo structure as returned by Batman.
        """

        # Walk the nodes.
        nodes = []
        for node in self._controller.get_aps():
            # Create nodes.
            nodeid = sub('[^a-fA-F0-9]+', '', node['mac'])
            nodes.append({'hardware': {'model': 'Unifi {0}'.format(MODELS.get(node['model'], 'unknown')),
                                       'nproc': 1},
                          'hostname': 'freifunk-celle-unifi-{0}'.format(nodeid),
                          'location': {'latitude': node['x'], 'longitude': node['y']},
                          'network': {'addresses': [node['ip']],
                                      'mac': node['mac']},
                          'node_id': nodeid,
                          'owner': {'contact': 'info@freifunk-celle.de'},
                          'software': {'autoupdater': {'branch': 'stable', 'enabled': True},
                                       'firmware': {'base': 'Unifi', 'release': node['version']}},
                          'system': {'site_code': 'ffce'}})

            # Create stats.
            self._stats.append({'clients': {'total': -1, 'wifi': -1},
                                'node_id': nodeid,
                                'gateway': gw,
                                'uptime': node['uptime'],
                                'traffic': {'rx': {'bytes': node['stat']['rx_bytes'],
                                                   'packets': node['stat']['rx_packets']},
                                            'tx': {'bytes': node['stat']['tx_bytes'],
                                                   'packets': node['stat']['tx_bytes']}}})

        # Return node list.
        return nodes

    def statistics(self):
        """
        Fetch the precollected statistics that were derived from the
        Unifi API statistics data. This must be called after the node
        info has already been retrieved.

        @return Statistics data.
        """

        # Return stats.
        return self._stats
