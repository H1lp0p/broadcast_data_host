# Host for [mobile_file_sender](https://github.com/H1lp0p/mobile_file_sender)

- runs udp server on port `8888`
- runs REST API on port `8000`

# how to run
- install [docker](https://www.docker.com/)
- open cmd in repository dir
- run
```bash
docker-compose up
```

#important to know

```yml
    volumes:
      - ./uploads:/app/uploads # ./uploads - folder to store data
```
[main.py](./main.py)

SECRET_KEY is sha encoded message to compare with message from client. Need to be changed along with client-side message (see [mobile_file_sender](https://github.com/H1lp0p/mobile_file_sender) readme file)

```python
SECRET_KEY = "b3405fbdf36b61f06f3a91054c62d68cd963e45b658f0834e44d0b76e7659c4d"
```

> Actualy, it's is just an example of server-side. If your server answers the same way (on udp message and REST API endpoints), it will also work with client

# todo's for future maintenance
- [ ] change simple sha encoded message to more secure verification pipeline
- [ ] add ssl certificates or solve security issues on client side other way
- [ ] add upload optimization to sync which files to upload