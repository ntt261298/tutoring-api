from configs.base import _BaseConfig


class _LocalConfig(_BaseConfig):
    DEBUG = True


config = _LocalConfig
