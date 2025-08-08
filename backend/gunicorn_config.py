# gunicorn_config.py
bind = 'unix:/var/run/gunicorn/llm_st_fly.sock'
workers = 3
worker_class = 'sync'
timeout = 120
access_logfile = '/var/log//gunicorn/gunicorn_access.log'
error_logfile = '/var/log//gunicorn/gunicorn_error.log'
