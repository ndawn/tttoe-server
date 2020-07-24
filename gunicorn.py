bind = 'unix:/tmp/toe.sock'

log_level = 'info'

access_log = '/var/www/ndawn.ru/toe/server/log/access.log'
error_log = '/var/www/ndawn.ru/toe/server/log/error.log'

worker_class = 'aiohttp.GunicornWebWorker'

prefork = True

daemon = True
pidfile = '/var/www/ndawn.ru/toe/server/toe.pid'
