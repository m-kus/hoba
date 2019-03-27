import os
import re
import subprocess
from loguru import logger
from keyrings.alt.file import PlaintextKeyring


def pass_show(path):
    return subprocess.check_output(['pass', 'show', path]).decode()


def pass_show_line(path):
    return pass_show(path).splitlines()[-1]


def ensure_directory(path):
    if not os.path.exists(path):
        logger.info(f'Directory does not exist, creating `{path}`')
        os.makedirs(path)
    elif not os.path.isdir(path):
        raise ValueError(f'Not a directory: `{path}`')


def export_env_file(target: dict, env):
    lines = list()
    for entry in target.get('variables', []):
        variable, path = re.split('=', entry.format(ENV=env))
        value = pass_show_line(path)
        if not value:
            raise ValueError(f'path not found: `{path}`')

        logger.info(f'Exporting env variable `{variable}`')
        lines.append(f'{variable}={value}')
        del value

    with open(target['output'], 'w') as f:
        f.write('\n'.join(lines))
    del lines


def export_dir(target: dict, env):
    for entry in target.get('files', []):
        path, output = re.split(':', entry.format(ENV=env))
        source = pass_show(path)
        if not source:
            raise ValueError(f'Path not found: `{path}`')

        logger.info(f'Exporting file `{output}`')
        with open(os.path.join(target['output'], output), 'w') as f:
            f.write(source)
        del source


def export_keyring(target: dict, env):
    keyring = PlaintextKeyring()
    keyring.file_path = target['output']

    for entry in target.get('entries'):
        username, service, path = re.split('[@:]', entry.format(ENV=env))
        password = pass_show_line(path)
        if not password:
            raise ValueError(f'Path not found: `{path}`')

        logger.info(f'Exporting keyring password for `{username}@{service}`')
        keyring.set_password(service, username, password)
        del password


def generate_files(config: dict, env=None):
    if not isinstance(config.get('environments'), dict):
        raise ValueError('Missing `environments` section')
    if env is None:
        logger.warning('Environment not specified, looking for default')
        env = next(k for k, v in config['environments'].items() if 'default' in v)
    elif env not in config['environments']:
        raise ValueError(f'Unsupported environment `{env}`')

    for target in config.get('targets', []):
        if env not in target.get('only', {env}):
            logger.info(f'Skipping target because `{env}` not in `{target["only"]}`')
            continue

        if env in target.get('except', []):
            logger.info(f'Skipping target because `{env}` is in except list')
            continue

        target['output'] = target['output'].format(ENV=env)
        logger.info(f'Processing {target["type"]} target at `{target["output"]}`')

        if target['type'] == 'env_file':
            ensure_directory(os.path.dirname(target['output']))
            export_env_file(target, env)
        elif target['type'] == 'dir':
            ensure_directory(target['output'])
            export_dir(target, env)
        elif target['type'] == 'keyring':
            ensure_directory(os.path.dirname(target['output']))
            export_keyring(target, env)
        else:
            raise ValueError(f'Unsupported target type `{target["type"]}`')
