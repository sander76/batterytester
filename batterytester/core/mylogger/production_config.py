LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n'}
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'c:\\temp\\log\\test.log',
            'formatter': 'verbose',
            'maxBytes': 10024,
            'backupCount': 10
        }
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
        'propagate': True
    }

}
