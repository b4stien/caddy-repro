# Repro Caddy glitch

TLDR: Disabling retries on GET request seems to disable a retry logic on upstream selection.

## Scenario

- An API with a single endpoint (`/ok-1s`) which responds 200 on a GET request (in 1 second), listening on port 8011.
- A Caddy server operating in reverse proxy mode in front of this single upstream API, limiting concurrent request to this upstream to 1 (using `upstreams.[].max_requests`).
- A client shooting 2 requests "at the same time" to this endpoint.
- We expect both requests to succeed, with a 1s delay on one of the two requests (the one reaching Caddy last).

## Problem

It works perfectly with `caddy-config.json`, but trying to disable retry on GET requests as it's done on `caddy-config.with-glitch.json` makes the whole process unreliable, failing ~80/90% of the tries.

The errors on Caddy logs are:

```
2023/09/26 10:17:46.061	ERROR	http.log.error	no upstreams available	{"request": {"remote_ip": "::1", "remote_port": "59635", "client_ip": "::1", "proto": "HTTP/1.1", "method": "GET", "host": "localhost:8010", "uri": "/ok-1s", "headers": {"Accept": ["*/*"], "Accept-Encoding": ["gzip, deflate"], "Connection": ["keep-alive"], "User-Agent": ["python-httpx/0.23.1"]}}, "duration": 0.000046458, "status": 503, "err_id": "23pbf4z8k", "err_trace": "reverseproxy.(*Handler).proxyLoopIteration (reverseproxy.go:483)"}
```

## Repro

```
# Launch Caddy with or without glitch
caddy run --config caddy-config.with-glitch.json

# Launch the API
python api.py

# Launch the client
python client.py
```

## Details

This has been done with `caddy v2.7.4 h1:J8nisjdOxnYHXlorUKXY75Gr6iBfudfoGhrJ8t7/flI=`. Outputs follows:

### `caddy-config.json`

Client logs

```
↪ python client.py
Success (iteration 0 - 2s)
Success (iteration 1 - 2s)
Success (iteration 2 - 2s)
Success (iteration 3 - 2s)
Success (iteration 4 - 2s)
Success (iteration 5 - 2s)
Success (iteration 6 - 2s)
Success (iteration 7 - 2s)
Success (iteration 8 - 2s)
Success (iteration 9 - 2s)
Success (iteration 10 - 2s)
Success (iteration 11 - 2s)
Success (iteration 12 - 2s)
Success (iteration 13 - 2s)
Success (iteration 14 - 2s)
Success (iteration 15 - 2s)
Success (iteration 16 - 2s)
Success (iteration 17 - 2s)
Success (iteration 18 - 2s)
Success (iteration 19 - 2s)
20 success(es), 0 failure(s)
```

### `caddy-config.with-glitch.json`

Caddy logs

```
...
2023/09/26 10:18:49.297	ERROR	http.log.error	no upstreams available	{"request": {"remote_ip": "::1", "remote_port": "59654", "client_ip": "::1", "proto": "HTTP/1.1", "method": "GET", "host": "localhost:8010", "uri": "/ok-1s", "headers": {"Accept": ["*/*"], "Accept-Encoding": ["gzip, deflate"], "Connection": ["keep-alive"], "User-Agent": ["python-httpx/0.23.1"]}}, "duration": 0.000037708, "status": 503, "err_id": "8ufm9246j", "err_trace": "reverseproxy.(*Handler).proxyLoopIteration (reverseproxy.go:483)"}
...
```

Client logs

```
↪ python client.py
Success (iteration 0 - 2s)
Success (iteration 1 - 2s)
Failure (iteration 2 - 1s)
Failure (iteration 3 - 1s)
Failure (iteration 4 - 1s)
Failure (iteration 5 - 1s)
Success (iteration 6 - 2s)
Failure (iteration 7 - 1s)
Failure (iteration 8 - 1s)
Failure (iteration 9 - 1s)
Failure (iteration 10 - 1s)
Failure (iteration 11 - 1s)
Failure (iteration 12 - 1s)
Failure (iteration 13 - 1s)
Failure (iteration 14 - 1s)
Failure (iteration 15 - 1s)
Failure (iteration 16 - 1s)
Failure (iteration 17 - 1s)
Failure (iteration 18 - 1s)
Failure (iteration 19 - 1s)
3 success(es), 17 failure(s)
```
