from django.apps import AppConfig

from . import monkey_patch
class LifterConfig(AppConfig):
    name = 'lifter'

    def ready(self):
        monkey_patch.setup()
