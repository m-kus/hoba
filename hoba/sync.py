import os
import git
import gnupg
import shutil
from loguru import logger


def sync_password_store(repo_url=None, repo_dir='~/.password-store') -> git.Repo:
    try:
        repo = git.Repo(repo_dir)
        logger.info(f'Password store at `{repo_dir}`')
        if repo.git.diff():
            raise ValueError('There are uncommitted changes')

        logger.info(f'Pulling changes from `{repo.remote().url}`')
        repo.git.pull()

    except git.NoSuchPathError:
        logger.info(f'Directory does not exist, creating `{repo_dir}`')
        os.makedirs(repo_dir)
        return sync_password_store(repo_url, repo_dir)

    except git.InvalidGitRepositoryError:
        if not os.path.isdir(repo_dir):
            raise ValueError(f'Not a directory: `{repo_dir}`')
        if os.listdir(repo_dir):
            raise ValueError(f'Directory is not empty: `{repo_dir}`')
        if not repo_url:
            raise ValueError('Repository url is not specified')

        logger.info(f'Directory is not a git repository, cloning from `{repo_url}`')
        repo = git.Repo.clone_from(repo_url, repo_dir)

    return repo


def get_gnupg():
    for cmd in ['gpg2', 'gpg']:
        if shutil.which(cmd) is not None:
            logger.info(f'Using binary `{cmd}`')
            return gnupg.GPG(gpgbinary=cmd)
    raise ValueError('GNUPG is not installed or not in the %PATH%')


def sync_gpg_keys(password_store: git.Repo, filename='.gpg-keys'):
    gpg = get_gnupg()

    secret_keys = gpg.list_keys(secret=True)
    if not secret_keys:
        input_data = gpg.gen_key_input(
            name_real=password_store.git.config('--get', 'user.name'),
            name_email=password_store.git.config('--get', 'user.email'),
            key_length=2048
        )
        logger.info(f'No gpg secret keys found, generating new one:\n{input_data}')
        res = gpg.gen_key(input_data)
        if not res.fingerprint:
            raise ValueError(res.stderr)
        secret_keys = gpg.list_keys(secret=True)

    uid = secret_keys[0]["uids"][0]
    if len(secret_keys) > 1:
        raise ValueError(f'Multiple secret keys found, will use `{uid}`')

    with open(os.path.join(password_store.working_dir, filename), 'a+') as f:
        f.seek(0)
        res = gpg.import_keys(f.read())
        gpg.trust_keys(res.fingerprints, 'TRUST_ULTIMATE')

        if not set(res.fingerprints).intersection(
                set(map(lambda x: x['fingerprint'], secret_keys))):
            logger.info(f'Your fingerprint is absent, exporting pubkey `{uid}`')
            f.write(gpg.export_keys([uid], secret=False))

    password_store.index.add([filename])
    if password_store.git.diff():
        password_store.index.commit(f'Add gpg key: {uid}')
        password_store.git.push()
