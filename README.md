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

### Storing and sharing secrets

Pass is a great alternative to Hashicorp Vault and other enterprise secret storages, cause it's simple, safe, and portable. In my team we came to a pretty convenient scheme without loosing in security.

1. All passwords encryption key, api keys, certificates, etc. are kept in a pass repo, which is gpg-encrypted and stored in git;
2. Pass allows to implement simple access control policy for each tree node with inheritance;
3. Each developer has to generate gpg key and add pubkey to the pass repo (keys are stored in .gpg-keys file);
4. All developers have to import all keys from the repo and set maximum trust level;

### Deploying secrets

Sample hoba configuration file:

```yaml
password-store:
  repository: http://github.com/example.git
  directory: ./.password-store

dev: &default
  environment:
    env_file: ./.env
    variables:
      - DB_PASSWORD=postgresql/example.com/password
  secrets:
    directory: ./.secrets
    files:
      - cert_key=ssl/example.com/cert_key
      - dh_param=ssl/example.com/dh_params

default: *default
```

Docker-compose sample integration:

```yaml

```
