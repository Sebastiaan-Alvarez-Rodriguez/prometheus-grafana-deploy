import argparse
import json
import os

import prometheus_grafana_deploy.internal.defaults.start as start_defaults
from prometheus_grafana_deploy.internal.util.printer import *


def basics():
    '''Basic top-level settings for our dashboard.'''
        # 'annotations': {'list': [{'builtIn': 1, 'datasource': 'skyhook', 'enable': True, 'hide': True, 'iconColor': 'rgba(0, 211, 255, 1)', 'name': 'Annotations & Alerts', 'type': 'dashboard'}]},
    return {
        'description': 'Dashboard showing CPU, RAM, Disk, and Network utilization of SkyhookDM',
        'editable': True,
        'gnetId': None,
        'graphTooltip': 0,
        'id': 1,
        'iteration': 1619523594477,
        'links': [],
        'panels': [],
        "refresh": "30s",
        "schemaVersion": 27,
        "style": "dark",
        "tags": [],
        "templating": {
            "list": [
              {
                "description": "Hostname of the client node",
                "error": None,
                "hide": 2,
                "label": "Client node",
                "name": "client",
                "query": "ms1243.utah.cloudlab.us",
                "skipUrlSync": False,
                "type": "constant"
              }
            ]
        },
        "time": {"from": "now-30m", "to": "now"},
        "timepicker": {"refresh_intervals": ["5s", "10s", "15s", "30s", "1m", "5m", "15m", "30m", "1h", "2h", "1d"]},
        "timezone": "",
        "title": "SkyhookDM-Arrow",
        "uid": "lxKiCIXMk",
        "version": 15
    }


def _dict_append(d0, d1):
    '''Appends dict `d1` to `d0`'''
    d0.update(d1)


def _panel_y_axis_percent(minval=0, maxval=100):
    '''Returns panel y axis information for CPU percentages.'''
    return {
        "yaxes": [
          {"$$hashKey": "object:104", "format": "percent", "label": None, "logBase": 1, "max": maxval, "min": minval, "show": True},
          {"$$hashKey": "object:105", "format": "short", "label": None, "logBase": 1, "max": None, "min": None, "show": True}
        ],
        "yaxis": {"align": False, "alignLevel": None}
    }

def _panel_y_axis_byte_rate():
    return {
        "yaxes": [
          {"$$hashKey": "object:104", "format": "binBps", "label": None, "logBase": 1, "min": 0, "show": True},
          {"$$hashKey": "object:105", "format": "short", "label": None, "logBase": 1, "max": None, "min": None, "show": True}
        ],
        "yaxis": {"align": False, "alignLevel": None}
    }

def _panel_x_axis():
    '''Returns standard panel x axis information for the x-axis.'''
    return {
        "xaxis": {"buckets": None, "mode": "time", "name": None, "show": True, "values": []},
    }

def _panel_legend():
    '''Returns standard panel legend information.'''
    return {"legend": {"avg": False, "current": False, "max": False, "min": False, "show": False, "total": False, "values": False}}

def _panel_lines():
    '''Returns standard panel line configuration.'''
    return {"lines": True, "linewidth": 1, "spaceLength": 10, "steppedLine": False,}

def _panel_misc():
    '''Returns standard panel misc configurations.'''
    return {
        "hiddenSeries": False,
        "nullPointMode": "null",
        "options": {"alertThreshold": True},
        "percentage": False,
        "pluginVersion": "7.5.4",
        "pointradius": 2,
        "points": False,
        "renderer": "flot",
        "seriesOverrides": [],
        "stack": True,
        "thresholds": [],
        "type": "graph"}

def _panel_style():
    '''Returns standard panel style.'''
    return {"aliasColors": {}, "bars": False, "dashLength": 10, "dashes": False, "datasource": None, "fieldConfig": {"defaults": {}, "overrides": []}, "fill": 1, "fillGradient": 0}

def _panel_time():
    '''Returns standard panel time configuration.'''
    return {"timeFrom": None, "timeRegions": [], "timeShift": None,}


def _panel_tooltip():
    '''Returns standard panel tooltip.'''
    return {"tooltip": {"shared": True, "sort": 0, "value_type": "individual"}}


def generate_panel_client_cpu(config, client_nodes, prometheus_port):
    '''Generates a panel displaying Client CPU utilization.'''
    panel_config = {'id': 2, 'gridPos': {'h': 8, 'w': 12, 'x': 0, 'y': 0}}
    axes_config = _panel_x_axis()
    _dict_append(axes_config, _panel_y_axis_percent(maxval=100*len(client_nodes)))

    _dict_append(panel_config, axes_config)
    _dict_append(panel_config, _panel_legend())
    _dict_append(panel_config, _panel_lines())
    _dict_append(panel_config, _panel_misc())
    _dict_append(panel_config, _panel_style())
    _dict_append(panel_config, _panel_time())
    _dict_append(panel_config, _panel_tooltip())
    _dict_append(panel_config, {
        "targets": [
          {
            "exemplar": True,
            "expr": "100 - (avg by (instance) (rate(node_cpu_seconds_total{job=\"client\",mode=\"idle\"}[1m])) * 100)",
            "interval": "",
            "legendFormat": "",
            "refId": "CPUAverageClient"
          }
        ],
        "title": "Client CPU Usage (%)"
    })
    config['panels'].append(panel_config)



def generate_panel_ceph_cpu(config, ceph_nodes, prometheus_port):
    '''Generates a panel displaying CPU utilization in Ceph.'''
    panel_config = {'id': 3, "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}}

    axes_config = _panel_x_axis()
    _dict_append(axes_config, _panel_y_axis_percent(maxval=100*len(ceph_nodes)))

    _dict_append(panel_config, axes_config)
    _dict_append(panel_config, _panel_legend())
    _dict_append(panel_config, _panel_lines())
    _dict_append(panel_config, _panel_misc())
    _dict_append(panel_config, _panel_style())
    _dict_append(panel_config, _panel_time())
    _dict_append(panel_config, _panel_tooltip())
    _dict_append(panel_config, {
        "targets": [
          {
            "exemplar": True,
            "expr": "100 - (avg by (instance) (rate(node_cpu_seconds_total{job=\"storage\",mode=\"idle\"}[1m])) * 100)",
            "interval": "",
            "legendFormat": "",
            "refId": "CPUAverageStorage"
          }
        ],
        "title": "Ceph CPU Usage (%)"
    })
    config['panels'].append(panel_config)


def generate_panel_client_ram(config, client_nodes, prometheus_port):
    panel_config = {'id': 4, "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}}

    axes_config = _panel_x_axis()
    _dict_append(axes_config, _panel_y_axis_percent(maxval=100*len(client_nodes)))

    _dict_append(panel_config, axes_config)
    _dict_append(panel_config, _panel_legend())
    _dict_append(panel_config, _panel_lines())
    _dict_append(panel_config, _panel_misc())
    _dict_append(panel_config, _panel_style())
    _dict_append(panel_config, _panel_time())
    _dict_append(panel_config, _panel_tooltip())
    _dict_append(panel_config, {
        "targets": [
          {
            "exemplar": True,
            "expr": "(1 - (node_memory_MemAvailable_bytes/node_memory_MemTotal_bytes{job=\"client\"}))*100",
            "interval": "",
            "legendFormat": "",
            "refId": "CPUAverageClient"
          }
        ],
        "title": "Client RAM Usage (%)"
    })
    config['panels'].append(panel_config)


def generate_panel_ceph_ram(config, ceph_nodes, prometheus_port):
    panel_config = {'id': 5, "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}}

    axes_config = _panel_x_axis()
    _dict_append(axes_config, _panel_y_axis_percent(maxval=100*len(ceph_nodes)))

    _dict_append(panel_config, axes_config)
    _dict_append(panel_config, _panel_legend())
    _dict_append(panel_config, _panel_lines())
    _dict_append(panel_config, _panel_misc())
    _dict_append(panel_config, _panel_style())
    _dict_append(panel_config, _panel_time())
    _dict_append(panel_config, _panel_tooltip())
    _dict_append(panel_config, {
        "targets": [
          {
            "exemplar": True,
            "expr": "(1 - (node_memory_MemAvailable_bytes/node_memory_MemTotal_bytes{job=\"storage\"}))*100",
            "interval": "",
            "legendFormat": "",
            "refId": "CPUAverageStorage"
          }
        ],
        "title": "Ceph RAM Usage (%)"
    })
    config['panels'].append(panel_config)


def generate_panel_client_network(config, client_nodes, prometheus_port):
    '''Generates a panel displaying Client network I/O utilization.'''
    panel_config = {'id': 6, 'gridPos': {'h': 8, 'w': 12, 'x': 0, 'y': 16}}
    axes_config = _panel_x_axis()
    _dict_append(axes_config, _panel_y_axis_byte_rate())

    _dict_append(panel_config, axes_config)
    _dict_append(panel_config, _panel_legend())
    _dict_append(panel_config, _panel_lines())
    _dict_append(panel_config, _panel_misc())
    _dict_append(panel_config, _panel_style())
    _dict_append(panel_config, _panel_time())
    _dict_append(panel_config, _panel_tooltip())
    _dict_append(panel_config, {
        "targets": [
          {
            "exemplar": True,
            "expr": "rate(node_network_receive_bytes_total{device=\"eno1d1\",job=\"client\"}[5m])",
            "interval": "",
            "legendFormat": "",
            "refId": "NetworkClient"
          }
        ],
        "title": "Client Network I/O"
    })
    config['panels'].append(panel_config)


def generate_panel_ceph_storage(config, ceph_nodes, prometheus_port):
    '''Generates a panel displaying Ceph Storage I/O utilization.'''
    panel_config = {'id': 7, "gridPos": {"h": 8, "w": 12, "x": 12, "y": 16}}
    axes_config = _panel_x_axis()
    _dict_append(axes_config, _panel_y_axis_byte_rate())

    _dict_append(panel_config, axes_config)
    _dict_append(panel_config, _panel_legend())
    _dict_append(panel_config, _panel_lines())
    _dict_append(panel_config, _panel_misc())
    _dict_append(panel_config, _panel_style())
    _dict_append(panel_config, _panel_time())
    _dict_append(panel_config, _panel_tooltip())
    _dict_append(panel_config, {
        "targets": [
          {
            "exemplar": True,
            "expr": "rate(node_disk_read_bytes_total{device=\"nvme0n1\", job=\"storage\"}[5m])",
            "interval": "",
            "legendFormat": "",
            "refId": "StorageIOStorage"
          }
        ],
        "title": "Ceph Disk I/O"
    })
    config['panels'].append(panel_config)


def parse(args):
    parser = argparse.ArgumentParser(prog='...')
    # We have no extra arguments to add here.
    parser.add_argument('--prometheus-port', metavar='number', dest='prometheus_port', type=int, default=start_defaults.prometheus_port(), help='Port to use for Prometheus.')
    args = parser.parse_args(args)
    return True, [], {'prometheus_port': args.prometheus_port}




def generate(reservation, outputloc, *args, **kwargs):
    prometheus_port = kwargs.get('prometheus_port') or start_defaults.prometheus_port()

    config = basics()

    client_nodes = [x for x in reservation.nodes if ('job' in x.extra_info and x.extra_info['job']=='client') or ((not 'designations' in x.extra_info) and not 'job' in x.extra_info)]
    ceph_nodes = [x for x in reservation.nodes if ('designations' in x.extra_info) or ('job' in x.extra_info and x.extra_info['job']=='storage')]

    print('Found {} client nodes and {} ceph nodes'.format(len(client_nodes), len(ceph_nodes)))

    generate_panel_client_cpu(config, client_nodes, prometheus_port)
    generate_panel_ceph_cpu(config, ceph_nodes, prometheus_port)
    generate_panel_client_ram(config, client_nodes, prometheus_port)
    generate_panel_ceph_ram(config, ceph_nodes, prometheus_port)
    generate_panel_client_network(config, client_nodes, prometheus_port)
    generate_panel_ceph_storage(config, ceph_nodes, prometheus_port)

    if os.path.isdir(outputloc):
        outputloc = os.path.join(outputloc, 'spark_rados.json')

    if os.path.isfile(outputloc):
        printw('File already exists, overriding: {}'.format(outputloc))

    with open(outputloc, 'w') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    return True