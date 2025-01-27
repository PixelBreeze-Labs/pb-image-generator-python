# utils/__init__.py
import logging
import redis
from functools import wraps
from PIL import Image
from io import BytesIO

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cache_key(template_type, params):
    """Generate unique cache key based on template and parameters"""
    return f"image:{template_type}:{hash(frozenset(params.items()))}"

def cache_image(template_type, params, image):
    """Cache the generated image"""
    try:
        cache_key = get_cache_key(template_type, params)
        img_bytes = BytesIO()
        image.save(img_bytes, format='PNG')
        redis_client.setex(cache_key, 3600, img_bytes.getvalue())
    except Exception as e:
        logger.error(f"Cache error: {str(e)}")

def get_cached_image(template_type, params):
    """Try to get image from cache"""
    try:
        cache_key = get_cache_key(template_type, params)
        cached = redis_client.get(cache_key)
        if cached:
            return Image.open(BytesIO(cached))
    except Exception as e:
        logger.error(f"Cache retrieval error: {str(e)}")
    return None

def handle_errors(f):
    """Error handling decorator"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            # Return fallback image
            return generate_error_image()
    return wrapper