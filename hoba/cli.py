import os
import yaml
import fire
import subprocess
from shellingham import detect_shell
from loguru import logger

from hoba.sync import sync_password_store, sync_gpg_keys
from hoba.gen import generate_files


def load_config(path='./hoba.yml'):
    if not os.path.exists(path):
        logger.warning('Config file not found in current folder, continue with reduced functional')
        config = dict()
    else:
        with open(path) as f:
            config = yaml.load(f.read())
    return config


def set_pass_env(pass_info: dict) -> bool:
    if not pass_info.get('repo_dir'):
        logger.info('Password store directory is not specified')
        return False
    else:
        os.environ['PASSWORD_STORE_DIR'] = pass_info['repo_dir']
        return True


def spawn_shell():
    if os.environ.get('HOBA_ACTIVE', '0') == '1':
        logger.info('You are already in a hoba shell')
    else:
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
        try:
            repo = sync_password_store(
                repo_url=config.get('repo_url'),
                repo_dir=config.get('repo_dir', '~/.password-store')
            )
            sync_gpg_keys(repo)
        except ValueError as e:
            logger.error(e)

    def shell(self):
        if set_pass_env(load_config().get('password-store', {})):
            spawn_shell()

    def gen(self, env=None):
        config = load_config()
        try:
            set_pass_env(config.get('password-store', {}))
            generate_files(load_config(), env)
        except ValueError as e:
            logger.error(e)


def main():
    fire.Fire(Hoba())


if __name__ == '__main__':
    main()
