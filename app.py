import os
import shutil
import requests
import traceback
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from io import BytesIO
import logging
from PIL import Image
from functools import wraps
import redis

# Import template functions
from templates import *
from scraper import is_local_path, scrape_artical
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize Redis for caching
redis_client = redis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_DB,
    decode_responses=True
)

def cache_key(session_id, template_type, **params):
    """Generate a unique cache key"""
    param_str = "-".join(f"{k}:{v}" for k, v in sorted(params.items()))
    return f"image:{session_id}:{template_type}:{param_str}"

def cache_image(key, image_data, expiry=3600):
    """Cache image data with expiry"""
    try:
        redis_client.setex(key, expiry, image_data)
        logger.info(f"Cached image with key: {key}")
    except Exception as e:
        logger.error(f"Cache error: {str(e)}")

def get_cached_image(key):
    """Retrieve cached image data"""
    try:
        return redis_client.get(key)
    except Exception as e:
        logger.error(f"Cache retrieval error: {str(e)}")
    return None

def error_handler(f):
    """Decorator for consistent error handling"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                "error": str(e),
                "status": "error"
            }), 500
    return wrapper

def generate_unique_output_path(user_id, extension="png"):
    """Generate unique output path with proper directory structure"""
    user_dir = os.path.join(Config.BASE_OUTPUT_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}.{extension}"
    return os.path.join(user_dir, filename)

def cleanup_old_files(directory, max_age_hours=24):
    """Cleanup files older than max_age_hours"""
    try:
        current_time = datetime.now()
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_age = datetime.fromtimestamp(os.path.getctime(file_path))
                if (current_time - file_age).total_seconds() > max_age_hours * 3600:
                    os.remove(file_path)
                    logger.info(f"Cleaned up old file: {file_path}")
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")

@app.route("/generate", methods=["POST"])
@error_handler
def generate_image():
    """Main endpoint for image generation"""
    # Validate required parameters
    session_id = request.form.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    template_type = request.form.get("template_type", "sample")

    # Get cache key and check cache
    cache_params = request.form.to_dict()
    cache_params.pop('session_id', None)
    key = cache_key(session_id, template_type, **cache_params)
    cached_data = get_cached_image(key)

    if cached_data:
        logger.info(f"Cache hit for key: {key}")
        return jsonify({
            "output_file_path": cached_data,
            "status": "success",
            "cached": True
        })

    # Generate output path
    output_img_path = generate_unique_output_path(session_id)

    try:
        # Process article URL if provided
        artical_url = request.form.get("artical_url")
        title = text = None
        input_img_path_url = None

        if artical_url:
            title, img_url = scrape_artical(artical_url)
            if not title or not img_url:
                return jsonify({"error": "Cannot scrape given URL"}), 500

            if is_local_path(img_url):
                with open(img_url, "rb") as img_file:
                    img_data = img_file.read()
                input_img_path_url = BytesIO(img_data)
                os.remove(img_url)
            else:
                response = requests.get(img_url)
                input_img_path_url = BytesIO(response.content)

        # Get input parameters
        text = request.form.get("text", title)
        input_img_path = request.form.get("input_img_path", input_img_path_url)
        if input_img_path == '':
            input_img_path = input_img_path_url

        # Process image based on template type
        if template_type in TEMPLATE_MAP:
            template_func = TEMPLATE_MAP[template_type]
            template_params = {
                'text': text,
                'input_img_path': input_img_path,
                'output_img_path': output_img_path,
                'crop_mode': request.form.get("crop_mode", "square"),
                'arrow': request.form.get("arrow"),
                'sub_text': request.form.get("sub_text", "").upper(),
            }
            template_func(**template_params)
        else:
            return jsonify({"error": f"Invalid template type: {template_type}"}), 400

        # Cache the result
        cache_image(key, output_img_path)

        # Cleanup old files periodically
        cleanup_old_files(Config.BASE_OUTPUT_DIR)

        return jsonify({
            "output_file_path": output_img_path,
            "status": "success",
            "cached": False
        })

    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        logger.error(traceback.format_exc())
        if os.path.exists(output_img_path):
            os.remove(output_img_path)
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

# Template mapping
TEMPLATE_MAP = {
    "quotes_writings_art": quotes_writings_art,
    "quotes_writings_morning": quotes_writings_morning,
    "quotes_writings_thonjeza": quotes_writings_thonjeza,
    "quotes_writings_citim": quotes_writings_citim,
    "reforma_quotes_writings": reforma_quotes_writings,
    "reforma_new_quote": reforma_new_quote,
    "reforma_feed_swipe": reforma_feed_swipe,
    "feed_basic": feed_basic,
    "feed_swipe": feed_swipe,
    "highlight": highlight_template,
    "logo_only": logo_only,
    "web_news": web_news,
    "citim": citim,
    "citim_version_2": citim_version_2,
    "iconic_location": iconic_location,
    "feed_location": feed_location,
    "web_news_story": web_news_story,
    "feed_headline": feed_headline,
    "web_news_story_2": web_news_story_2,
    "reforma_web_news_story_2": reforma_web_news_story_2,
    "reforma_news_feed": reforma_news_feed,
    "reforma_web_news_story1": reforma_web_news_story1,
    "reforma_web_news_story2": reforma_web_news_story2,
    "reforma_logo_only": reforma_logo_only,
    "story_2": story_2
}

if __name__ == "__main__":
    app.run(debug=Config.DEBUG)