class Config:
    # Redis settings
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DB = 0

    # File settings
    BASE_OUTPUT_DIR = "/var/www/html/api.pixelbreeze.xyz/temp"

    # App settings
    DEBUG = False

    # Cache settings
    CACHE_EXPIRY = 3600  # 1 hour

    # Cleanup settings
    FILE_MAX_AGE_HOURS = 24