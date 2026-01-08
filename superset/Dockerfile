# ============================================
# Apache Superset Custom Docker Image
# Personal Finance BI System
# ============================================

FROM apache/superset:3.1.0

# Switch to root for installation
USER root

# Install additional database drivers and gevent worker
RUN pip install --no-cache-dir \
    psycopg2-binary \
    sqlalchemy \
    requests \
    gevent

# Copy custom configuration
COPY superset_config.py /app/pythonpath/superset_config.py

# Set environment variables
ENV SUPERSET_CONFIG_PATH=/app/pythonpath/superset_config.py
ENV FLASK_ENV=production

# Create directories for cache
RUN mkdir -p /app/superset_home/cache /app/superset_home/data_cache && \
    chown -R superset:superset /app/superset_home

# Switch back to superset user
USER superset

# Expose port
EXPOSE 8088

# Default command
CMD ["gunicorn", "--bind", "0.0.0.0:8088", "--workers", "4", "--worker-class", "gevent", "--timeout", "120", "superset.app:create_app()"]
