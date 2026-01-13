# ============================================
# Apache Superset Configuration
# Personal Finance BI System
# ============================================

import os
from datetime import timedelta
from cachelib.file import FileSystemCache

# ============================================
# GENERAL CONFIG
# ============================================

# Superset specific config
ROW_LIMIT = 5000
SUPERSET_WEBSERVER_PORT = 8088

# Flask App Builder configuration
SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY', 'superset-secret-key-change-me!')

# Feature flags
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "ENABLE_TEMPLATE_REMOVE_FILTERS": True,
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_CROSS_FILTERS": True,
    "DASHBOARD_NATIVE_FILTERS_SET": True,
    "EMBEDDED_SUPERSET": True,
    "ENABLE_JAVASCRIPT_CONTROLS": True,
    "ALERT_REPORTS": True,
    "DASHBOARD_VIRTUALIZATION": True,
}

# ============================================
# DATABASE CONNECTIONS
# ============================================

# Superset's own metadata database
SQLALCHEMY_DATABASE_URI = 'sqlite:////app/superset_home/superset.db'

# ============================================
# CACHE CONFIG
# ============================================

CACHE_CONFIG = {
    'CACHE_TYPE': 'FileSystemCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_DIR': '/app/superset_home/cache',
}

DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'FileSystemCache',
    'CACHE_DEFAULT_TIMEOUT': 600,
    'CACHE_DIR': '/app/superset_home/data_cache',
}

# ============================================
# SECURITY CONFIG
# ============================================

# Allow embedding in iframes
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
ENABLE_CORS = True
CORS_OPTIONS = {
    'supports_credentials': True,
    'allow_headers': ['*'],
    'resources': ['*'],
    'origins': ['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:5173', 'http://127.0.0.1:5173']
}

# Allow iframe embedding (remove X-Frame-Options)
HTTP_HEADERS = {
    'X-Frame-Options': 'ALLOWALL',
}

TALISMAN_ENABLED = False

# Enable public dashboards
PUBLIC_ROLE_LIKE = "Gamma"

# Guest token for embedded analytics
GUEST_ROLE_NAME = "Gamma"
GUEST_TOKEN_JWT_SECRET = os.environ.get('GUEST_TOKEN_SECRET', 'guest-secret-change-me!')
GUEST_TOKEN_JWT_ALGO = "HS256"
GUEST_TOKEN_HEADER_NAME = "X-GuestToken"
GUEST_TOKEN_JWT_EXP_SECONDS = 3600

# Enable Gamma role for public viewing
PUBLIC_ROLE_LIKE_GAMMA = True

# ============================================
# UI CONFIG
# ============================================

# App name displayed in browser tab
APP_NAME = "Finance BI"

# App icon (path relative to superset/static/assets/images/)
APP_ICON = "/static/assets/images/superset-logo-horiz.png"

# Favicon
FAVICONS = [{"href": "/static/assets/images/favicon.png"}]

# Default chart palette - finance theme
EXTRA_CATEGORICAL_COLOR_SCHEMES = [
    {
        "id": "financeTheme",
        "description": "Personal Finance Theme",
        "label": "Finance Theme",
        "isDefault": True,
        "colors": [
            "#10b981",  # Green - Income
            "#ef4444",  # Red - Expense
            "#6366f1",  # Indigo - Primary
            "#8b5cf6",  # Purple
            "#06b6d4",  # Cyan
            "#f59e0b",  # Amber
            "#ec4899",  # Pink
            "#14b8a6",  # Teal
            "#f97316",  # Orange
            "#3b82f6",  # Blue
        ]
    }
]

# ============================================
# LANGUAGE & LOCALIZATION
# ============================================

# Languages available in Superset
LANGUAGES = {
    'en': {'flag': 'us', 'name': 'English'},
    'vi': {'flag': 'vn', 'name': 'Vietnamese'},
}

# Default language
BABEL_DEFAULT_LOCALE = 'en'

# Timezone
DEFAULT_TIMEZONE = 'Asia/Ho_Chi_Minh'

# ============================================
# LOGGING CONFIG
# ============================================

LOG_FORMAT = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
LOG_LEVEL = 'INFO'
ENABLE_TIME_ROTATE = True
TIME_ROTATE_LOG_LEVEL = 'DEBUG'
FILENAME = '/app/superset_home/superset.log'
ROLLOVER = 'midnight'
INTERVAL = 1
BACKUP_COUNT = 30

# ============================================
# EMAIL REPORTING CONFIG
# ============================================

SMTP_HOST = os.environ.get('SMTP_HOST', 'mailhog')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 1025))
SMTP_STARTTLS = False
SMTP_SSL = False
SMTP_USER = ''
SMTP_PASSWORD = ''
SMTP_MAIL_FROM = 'superset@finance.local'

# Alert reports
ALERT_REPORTS_NOTIFICATION_DRY_RUN = False
WEBDRIVER_BASEURL = 'http://superset:8088/'
WEBDRIVER_BASEURL_USER_FRIENDLY = 'http://localhost:8088/'

# ============================================
# ADDITIONAL SETTINGS
# ============================================

# Enable SQL Lab
SQL_MAX_ROW = 100000
DISPLAY_MAX_ROW = 10000

# Async queries (for better performance)
SQLLAB_ASYNC_TIME_LIMIT_SEC = 60 * 60 * 6
SQLLAB_TIMEOUT = 60 * 30

# Jinja templating for SQL
ENABLE_TEMPLATE_PROCESSING = True

# Allowed tags for SQL templating
JINJA_CONTEXT_ADDONS = {
    'current_user_id': lambda: 1,  # Default user for embedded mode
    'current_month': lambda: 'EXTRACT(MONTH FROM CURRENT_DATE)',
    'current_year': lambda: 'EXTRACT(YEAR FROM CURRENT_DATE)',
}

# CSV export config
CSV_EXPORT = {
    'encoding': 'utf-8',
}
