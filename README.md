# Hoba
Yet another secrets management toolkit

![hoba](http://memesmix.net/media/download.php?meme=weqlu4)


## Configuration

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
