# Hoba
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
$ hoba update
```

Hoba can also spawn a shell with overrided `PASSWORD_STORE_DIR` environment variable:

```
$ hoba shell
$ pass
```

### Deploying secrets

By default hoba looks for a ```default``` section inside the configuration file.

```
$ hoba export
```

You can also specify target env:

```
$ hoba export dev
```

Sample hoba configuration file:

```yaml
password-store:
  repository: http://github.com/example.git
  directory: ./.password-store

dev: &default
  environment:
    env_file: ./.secrets/dev.env
    variables:
      - DB_PASSWORD=postgresql/example.com/password
  secrets:
    directory: ./.secrets
    files:
      - cert_key=ssl/example.com/cert_key
      - dh_param=ssl/example.com/dh_params

default: *default
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
    
secrets:
  cert_key:
    file: ./.secrets/cert_key
  dh_params:
    file: ./.secrets/dh_params
```
