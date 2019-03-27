import os
import yaml
import fire
import subprocess
from shellingham import detect_shell
from loguru import logger

from hoba.sync import sync_password_store, sync_gpg_keys
from hoba.gen import generate_files


def load_config(filename='hoba.yml'):
    config_path = os.path.join(os.getcwd(), filename)
    if not os.path.exists(config_path):
        logger.warning('Config file not found in current folder, continue with reduced functional')
        config = dict()
    else:
        with open(config_path) as f:
            config = yaml.load(f.read())

    return config


def spawn_shell():
    os.environ['PS1'] = r'\[\033[48;5;54m\]\u@\h:\w\\$\e[0m \[$(tput sgr0)\]'
    os.environ['HOBA_ACTIVE'] = '1'

    _, shell_path = detect_shell(os.getpid())
    subprocess.call([shell_path, '--norc', '--noprofile', '-i'])

    os.environ.pop('HOBA_ACTIVE')


class Hoba:

    def __str__(self):
        return 'Documentation'

    def sync(self):
        config = load_config().get('password-store', {})
        repo = sync_password_store(
            repo_url=config.get('repo_url'),
            repo_dir=config.get('repo_dir', '~/.password-store')
        )
        sync_gpg_keys(repo)

    def shell(self):
        config = load_config().get('password-store', {})
        if not config.get('repo_dir'):
            logger.info('Password store directory is not specified')
        elif os.environ.get('HOBA_ACTIVE', '0') == '1':
            logger.info('You are already in a hoba shell')
        else:
            os.environ['PASSWORD_STORE_DIR'] = config['repo_dir']
            spawn_shell()

    def gen(self, env=None):
        generate_files(load_config(), env)


def main():
    fire.Fire(Hoba())


if __name__ == '__main__':
    main()
