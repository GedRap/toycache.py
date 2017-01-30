# Twisted application configuration file for ToyCache
# To learn more about application configuration files, read
# http://twisted.readthedocs.io/en/twisted-16.3.0/core/howto/application.html

from twisted.application import service
from toycache.network_interface import CacheService

application = service.Application("ToyCache.py server")

# attach the service to its parent application
service = CacheService()
service.setServiceParent(application)