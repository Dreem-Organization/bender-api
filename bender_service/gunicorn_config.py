"""
Gunicorn configuration file (all arguments can be overriden by passing CLI
arguments with similar names (maybe underscores become dashes but that's all)
"""
# Source IPs to accept
bind = ["0.0.0.0:8000"]
forwarded_allow_ips = "*"

# Backend timeout
timeout = 30

# Graceful termination timeout (should simply be higher than the maximum
# request processing time, here, log uploads of say... five minutes)
graceful_timeout = 35

# Number of worker processes
workers = 3
worker_class = 'gevent'

# Maximum number of pending connection
backlog = 2048

# Maximum number of requests a worker will process before restarting
max_requests = 8192

# Randomize restarts by +/- a certain amount to prevent workers from restarting
# at the same time
max_requests_jitter = 512

# Preload the application code before worker processes are forked (decreases
# RAM consumption a bit)
preload = True
