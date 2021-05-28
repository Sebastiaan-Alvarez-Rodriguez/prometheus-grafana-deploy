import concurrent.futures
import hashlib
import subprocess
import tempfile

import prometheus_grafana_deploy.internal.defaults.start as defaults
import prometheus_grafana_deploy.internal.defaults.install as install_defaults
from prometheus_grafana_deploy.internal.remoto.modulegenerator import ModuleGenerator
from prometheus_grafana_deploy.internal.remoto.util import get_ssh_connection as _get_ssh_connection
import prometheus_grafana_deploy.internal.util.fs as fs
import prometheus_grafana_deploy.internal.util.importer as importer
import prometheus_grafana_deploy.internal.util.location as loc
from prometheus_grafana_deploy.internal.util.printer import *


def _start_prometheus_node_exporter(connection, module, install_dir, silent=False):
    remote_module = connection.import_module(module)

    if not remote_module.start_prometheus_node_exporter(loc.prometheus_exporterdir(install_dir), silent):
        printe('Could not start prometheus node exporter.')
        return False
    return True


def _start_prometheus_admin(connection, module, install_dir, reservation, port=defaults.prometheus_port(), silent=False):
    remote_module = connection.import_module(module)

    hostlist = ['{}:{}'.format(x.ip_public, port) for x in reservation.nodes]
    if not remote_module.start_prometheus_admin(loc.prometheus_admindir(install_dir), hostlist,  silent):
        printe('Could not start Prometheus admin on some node(s).')
        return False
    return True

def _start_grafana(connection, module, name=defaults.grafana_name(), port=defaults.grafana_port(), image=install_defaults.grafana_image(), silent=False):
    remote_module = connection.import_module(module)
    if not remote_module.start_grafana(name, image, port, silent):
        printe('Could not start Grafana.')
        return False
    return True


def _generate_module_start(silent=False):
    '''Generates Prometheus-start module from available sources.'''
    generation_loc = fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'remoto', 'modules', 'generated', 'all_start.py')
    files = [
        fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'util', 'printer.py'),
        fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'remoto', 'modules', 'util.py'),
        fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'remoto', 'modules', 'printer.py'),
        fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'remoto', 'modules', 'prometheus_start.py'),
        fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'remoto', 'modules', 'grafana_start.py'),
        fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'remoto', 'modules', 'remoto_base.py'),
    ]
    ModuleGenerator().with_modules(fs, importer).with_files(*files).generate(generation_loc, silent)
    return importer.import_full_path(generation_loc)


def _pick_admin(reservation, admin=None):
    '''Picks a Prometheus admin node.
    Args:
        reservation (metareserve.Reservation): Reservation object to pick admin from.
        admin (optional int): If set, picks node with given `node_id`. Picks node with lowest public ip value, otherwise.

    Returns:
        admin, list of non-admins.'''
    if len(reservation) == 1:
        return next(reservation.nodes), []

    if admin:
        return reservation.get_node(node_id=admin), [x for x in reservation.nodes if x.node_id != admin]
    else:
        tmp = sorted(reservation.nodes, key=lambda x: x.ip_public)
        return tmp[0], tmp[1:]


def _merge_kwargs(x, y):
    z = x.copy()
    z.update(y)
    return z


def start(reservation, install_dir=install_defaults.install_dir(), key_path=None, admin_id=None, prometheus_port=defaults.prometheus_port(), grafana_name=defaults.grafana_name(), grafana_port=defaults.grafana_port(), grafana_image=install_defaults.grafana_image(), silent=False):
    '''Start Prometheus on remote cluster.
    Args:
        reservation (metareserve.Reservation): Reservation object with all nodes to start Prometheus on.
        install_dir (optional str): Location on remote host to store Prometheus in.
        key_path (optional str): Path to SSH key, which we use to connect to nodes. If `None`, we do not authenticate using an IdentityFile.
        admin_id (optional int): Node id of the admin. If `None`, the node with lowest public ip value (string comparison) will be picked.
        prometheus_port (optional int): Port to use with Prometheus.
        grafana_name (optional str): Grafana docker run name to use.
        grafana_port (optional int): Port to use with Grafana.
        grafana_image (optional str): Grafana docker image to use.
        silent (optional bool): If set, does not print so much info.

    Returns:
        `True, admin_node_id` on success, `False, None` otherwise.'''
    admin_picked, _ = _pick_admin(reservation, admin=admin_id)
    printc('Picked admin node: {}'.format(admin_picked), Color.CAN)

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(reservation)+2) as executor:
        ssh_kwargs = {'IdentitiesOnly': 'yes', 'StrictHostKeyChecking': 'no'}
        if key_path:
            ssh_kwargs['IdentityFile'] = key_path
        else:
            printw('Connections have no assigned ssh key. Prepare to fill in your password often.')
        futures_connection = {x: executor.submit(_get_ssh_connection, x.ip_public, silent=silent, ssh_params=_merge_kwargs(ssh_kwargs, {'User': x.extra_info['user']})) for x in reservation.nodes}
        connectionwrappers = {k: v.result() for k,v in futures_connection.items()}

        start_module = _generate_module_start()
        futures_start = [executor.submit(_start_prometheus_node_exporter, wrapper.connection, start_module, install_dir, silent=silent) for wrapper in connectionwrappers.values()]
        
        futures_start.append(executor.submit(_start_prometheus_admin, connectionwrappers[admin_picked].connection, start_module, install_dir, reservation, port=prometheus_port, silent=silent))
        
        futures_start.append(executor.submit(_start_grafana, connectionwrappers[admin_picked].connection, start_module, name=grafana_name, port=grafana_port, image=grafana_image, silent=silent))

        if not all(x.result() for x in futures_start):
            return False, None
        prints('Prometheus+Grafana started on all nodes.')
        return True, admin_picked.node_id