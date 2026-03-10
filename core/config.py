class Config:
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'WARNING'


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
