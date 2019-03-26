import os
import yaml
import fire
import subprocess
from shellingham import detect_shell
from loguru import logger

from hoba.sync import sync_password_store, sync_gpg_keys


def load_config(section, config_path='./hoba.yml'):
    if not os.path.exists(config_path):
        logger.warning('Config file not found in current folder, continue with reduced functional')
        config = dict()
    else:
        with open(config_path) as f:
            config = yaml.load(f.read())

    return config.get(section, dict())


def pass_show(path):
    return subprocess.check_output(['pass', 'show', path]).decode()


def pass_show_line(path):
    return pass_show(path).splitlines()[-1]


def export_env_file(config: dict, default_path='./.env'):
    lines = list()
    for entry in config.get('variables', []):
        variable, path = entry.split('=')
        lines.append(f'{variable}={pass_show_line(path)}')

    with open(config.get('env_file', default_path), 'w') as f:
        f.write('\n'.join(lines))


def export_secrets(config: dict, default_dir='./.secrets'):
    secrets_dir = config.get('directory', default_dir)
    if not os.path.exists(secrets_dir):
        logger.info(f'Secrets directory does not exist, creating `{secrets_dir}`')
        os.makedirs(secrets_dir)

    for entry in config.get('files', []):
        filename, path = entry.split('=')
        with open(os.path.join(secrets_dir, filename), 'w') as f:
            f.write(pass_show(path))


def spawn_shell():
    os.environ['PS1'] = r'\[\033[48;5;54m\]\u@\h:\w\\$\e[0m \[$(tput sgr0)\]'
    os.environ['HOBA_ACTIVE'] = '1'

    _, shell_path = detect_shell(os.getpid())
    subprocess.call([shell_path, '--norc', '--noprofile', '-i'])

    os.environ.pop('HOBA_ACTIVE')


class Hoba:

    def __str__(self):
        return 'Documentation'

    def update(self):
        config = load_config('password-store')
        repo = sync_password_store(
            repo_url=config.get('repository'),
            repo_dir=config.get('directory', '~/.password-store')
        )
        sync_gpg_keys(repo)

    def shell(self):
        config = load_config('password-store')
        if not config.get('directory'):
            logger.info('Password store directory is not specified')
        elif os.environ.get('HOBA_ACTIVE', '0') == '1':
            logger.info('You are already in a hoba shell')
        else:
            os.environ['PASSWORD_STORE_DIR'] = config['directory']
            spawn_shell()

    def export(self, env='default'):
        config = load_config(env)
        if config.get('environment'):
            export_env_file(config['environment'])
        if config.get('secrets'):
            export_secrets(config['secrets'])


def main():
    fire.Fire(Hoba())


if __name__ == '__main__':
    main()
