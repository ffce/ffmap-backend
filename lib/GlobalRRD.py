import os
import subprocess

from lib.RRD import DS, RRA, RRD


class GlobalRRD(RRD):
    ds_list = [
        # Number of nodes available
        DS('nodes', 'GAUGE', 1800, 0, float('NaN')),
        # Number of client available
        DS('clients', 'GAUGE', 1800, 0, float('NaN')),
    ]
    rra_list = [
        # 12 hours of 10 minute samples
        RRA('AVERAGE', 0.5, 1, 72),
        # 31 days  of 2 hour samples
        RRA('AVERAGE', 0.5, 12, 372),
        # ~5 years of 1 day samples
        RRA('AVERAGE', 0.5, 144, 1860),
    ]

    def __init__(self, directory):
        super().__init__(os.path.join(directory, "nodes.rrd"))
        self.ensure_sanity(self.ds_list, self.rra_list, step=600)

    # TODO: fix this, python does not support function overloading
    def update(self, node_count, client_count):
        super().update({'nodes': node_count, 'clients': client_count})

    def graph(self, filename, timeframe):
        args = ["/usr/bin/rrdtool", 'graph', filename,
                '-s', '-' + timeframe,
                '-w', '800',
                '-h' '400',
                'DEF:nodes=' + self.filename + ':nodes:AVERAGE',
                'LINE1:nodes#F00:nodes\\l',
                'DEF:clients=' + self.filename + ':clients:AVERAGE',
                'LINE2:clients#00F:clients']
        subprocess.check_output(args)
