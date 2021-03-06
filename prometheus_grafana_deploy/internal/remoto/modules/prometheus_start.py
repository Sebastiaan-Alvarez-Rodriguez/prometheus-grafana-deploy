import subprocess

def start_prometheus_node_exporter(location, silent):
    if not isfile('/etc/systemd/system/node_exporter.service'):
        return False # We have no node daemon installed.
    if subprocess.call('sudo systemctl restart node_exporter', **get_subprocess_kwargs(silent)) != 0:
        return False
    return subprocess.call('sudo systemctl enable node_exporter', **get_subprocess_kwargs(silent)) == 0

def start_prometheus_admin(location, config, silent):
    if not isfile('/etc/systemd/system/prometheus.service'):
        return False # We have no node daemon installed.
    location = os.path.expanduser(location)
    if not isdir(location):
        mkdir(location, exist_ok=True)

    configfile = join(location, 'config.yml')
    with open(configfile, 'w') as f:
        f.write(config)
    if subprocess.call('sudo systemctl restart prometheus', **get_subprocess_kwargs(silent)) != 0:
        return False
    return subprocess.call('sudo systemctl enable prometheus', **get_subprocess_kwargs(silent)) == 0
