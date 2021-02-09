from configs.base import _BaseConfig


class _ProductionConfig(_BaseConfig):
    DEBUG = False


config = _ProductionConfig
