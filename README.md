# Hoba


[![PyPI version](https://badge.fury.io/py/hoba.svg?)](https://badge.fury.io/py/hoba)
[![Build Status](https://travis-ci.org/m-kus/hoba.svg?branch=master)](https://travis-ci.org/m-kus/hoba)
[![Made With](https://img.shields.io/badge/made%20with-python-blue.svg?)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Yet another secrets management toolkit based on [passwordstore](https://www.passwordstore.org/)

![hoba](http://memesmix.net/media/download.php?meme=weqlu4)


## Requirements

* git
* gnupg
* pass
* python 3.6+
* pip 19.0.1+

## Installation

```
$ pip install git+https://github.com/m-kus/hoba
```

## Usage

All hoba commands work only if there is a ```hoba.yml``` file inside the current directory. File format will be described below.

### Storing and sharing secrets

Pass is a great alternative to Hashicorp Vault and other enterprise secret storages, cause it's simple, safe, and portable. In my team we came to a pretty convenient scheme without loosing in security.

1. All passwords encryption key, api keys, certificates, etc. are kept in a pass repo, which is gpg-encrypted and stored in git;
2. Pass allows to implement simple access control policy for each tree node with inheritance;
3. Each developer has to generate gpg key and add pubkey to the pass repo (keys are stored in .gpg-keys file);
4. All developers have to import all keys from the repo and set maximum trust level;

You can do this manually, but there is a command which does pretty much the same:

```
$ hoba sync
```

Hoba can also spawn a shell with overrided `PASSWORD_STORE_DIR` environment variable:

```
$ hoba shell
$ pass
```

### Deploying secrets

By default hoba looks for a ```default``` section inside the configuration file.

```
$ hoba gen
```

You can also specify target env:

```
$ hoba gen dev
```

Sample hoba configuration file:

```yaml
password-store:
  repo_url: http://github.com/example.git
  repo_dir: ./.password-store
  
environments:
  dev:
    default:
  prod:
  
targets:
  - type: env_file
    output: ./.secrets/{ENV}.env
    variables:
      - DB_PASSWORD={ENV}/postgresql/password
    except:
      - dev

  - type: dir
    output: ./.secrets
    files:
      - ssl/example.com/cert_key:ssl/cert_key
      - ssl/example.com/dh_params:ssl/dh_params
    only:
      - prod

  - type: keyring
    output: ./.secrets/keyring_pass.cfg
    entries:
      - app@telegram:{ENV}/telegram/bot_api_key
```

Docker compose integration example:

```yaml
version: "3.1"
services:
  nginx:
    environment:
      env_file:
      - ./.secrets/dev.env
    secrets:
      - cert_key
      - dh_params
      - source: keyring
        target: /root/.local/share/python_keyring/keyring_pass.cfg
    
secrets:
  cert_key:
    file: ./.secrets/ssl/cert_key
  dh_params:
    file: ./.secrets/ssl/dh_params
  keyring:
    file: ./.secrets/keyring_pass.cfg
```
