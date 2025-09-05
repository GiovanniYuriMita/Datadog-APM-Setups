FROM php:8.3-fpm-alpine

# Install essential libraries for Datadog APM compatibility
RUN echo "http://dl-cdn.alpinelinux.org/alpine/v3.18/main" > /etc/apk/repositories && \
    echo "http://dl-cdn.alpinelinux.org/alpine/v3.18/community" >> /etc/apk/repositories && \
    apk update && \
    apk add --no-cache \
    libgcc \
    libstdc++ \
    libc6-compat \
    gcompat \
    nginx \
    supervisor \
    git \
    curl \
    oniguruma-dev \
    libzip-dev \
    libpng-dev

# Install PHP extensions (minimal set)
RUN docker-php-ext-install pdo_mysql mbstring zip

# Install Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Set working directory
WORKDIR /var/www/html

# Copy application code
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p storage/logs storage/framework/cache storage/framework/sessions storage/framework/views \
    && chown -R www-data:www-data /var/www/html \
    && chmod -R 755 storage bootstrap/cache

# Configure Nginx
RUN cat > /etc/nginx/http.d/default.conf << 'EOF'
server {
    listen 80;
    server_name localhost;
    root /var/www/html/public;
    index index.php index.html;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        fastcgi_pass 127.0.0.1:9000;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\.ht {
        deny all;
    }
}
EOF

# Configure supervisor
RUN mkdir -p /etc/supervisor/conf.d && \
    cat > /etc/supervisor/conf.d/supervisord.conf << 'EOF'
[supervisord]
nodaemon=true

[program:nginx]
command=nginx -g "daemon off;"
autostart=true
autorestart=true

[program:php-fpm]
command=php-fpm -F
autostart=true
autorestart=true
EOF

# Install Datadog PHP extension
RUN curl -LO https://github.com/DataDog/dd-trace-php/releases/latest/download/datadog-setup.php \
    && php datadog-setup.php --php-bin=all --enable-appsec --enable-profiling \
    && docker-php-ext-enable ddtrace

# Configure PHP for Laravel
RUN echo "memory_limit = 256M" >> /usr/local/etc/php/conf.d/laravel.ini \
    && echo "upload_max_filesize = 64M" >> /usr/local/etc/php/conf.d/laravel.ini \
    && echo "post_max_size = 64M" >> /usr/local/etc/php/conf.d/laravel.ini \
    && echo "max_execution_time = 300" >> /usr/local/etc/php/conf.d/laravel.ini

# Set up Laravel environment
RUN echo "APP_KEY=base64:$(openssl rand -base64 32)" > .env \
    && echo "APP_ENV=local" >> .env \
    && echo "APP_DEBUG=true" >> .env \
    && echo "LOG_CHANNEL=stack" >> .env \
    && echo "DD_AGENT_HOST=datadog-agent" >> .env \
    && echo "DD_TRACE_AGENT_PORT=8126" >> .env \
    && echo "DD_ENV=local" >> .env \
    && echo "DD_SERVICE=laravel-datadog-apm" >> .env \
    && echo "DD_VERSION=1.0.0" >> .env \
    && echo "DD_TRACE_DEBUG=true" >> .env \
    && echo "DD_TRACE_SAMPLE_RATE=1.0" >> .env \
    && echo "DD_TRACE_ANALYTICS_ENABLED=true" >> .env \
    && echo "DD_TRACE_AUTO_FLUSH_ENABLED=true" >> .env \
    && echo "DD_TRACE_GENERATE_ROOT_SPAN=true" >> .env \
    && echo "DD_TRACE_URL_AS_RESOURCE_NAMES_ENABLED=true" >> .env \
    && echo "DD_TAGS=env:local,service:laravel-datadog-apm" >> .env \
    && echo "DD_LOGS_ENABLED=true" >> .env \
    && echo "DD_LOGS_INJECTION=true" >> .env \
    && echo "DD_PROFILING_ENABLED=true" >> .env \
    && echo "DD_TRACE_CLI_ENABLED=true" >> .env \
    && echo "DD_TRACE_RESOURCE_URI_MAPPING_INCOMING=*" >> .env

EXPOSE 80

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]