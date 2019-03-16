# sync
A distributed synchronization service.

## Starting

```bash
python3.6 app.py
```

After server started listening:
```bash
nc 127.0.0.1 10000
acquire 1
acquire 2
release 1
release 2
```
