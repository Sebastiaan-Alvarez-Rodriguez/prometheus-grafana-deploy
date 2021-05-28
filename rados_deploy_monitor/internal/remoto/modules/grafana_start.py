import subprocess

def start_grafana(instance_name, image, port, silent):
    output = subprocess.check_output('sudo docker ps -f "name={0}" --format "{{{{.Names}}}}"'.format(instance_name), **get_subprocess_kwargs(True)).decode('utf-8').strip()
    grafana_running = output == instance_name
    if grafana_running:
        prints('Running Grafana instance found.')
        return True
    if subprocess.call('sudo docker run -d --name {0} -p {1}:{1} {2}'.format(instance_name, port, image), **get_subprocess_kwargs(silent)) != 0:
        printe('Could not start Grafana.')
        return False
    return True