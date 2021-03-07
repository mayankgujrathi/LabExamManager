from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self) -> None:
        super().ready()
        import users.signals