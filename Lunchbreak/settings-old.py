from configurations import Configuration
from Lunchbreak import config


class Base(config.Base, Configuration):
    pass


class Development(config.Development, Configuration):
    pass


class Travis(config.Travis, Configuration):
    pass


class Staging(config.Staging, Configuration):
    pass


class Beta(config.Beta, Configuration):
    pass
