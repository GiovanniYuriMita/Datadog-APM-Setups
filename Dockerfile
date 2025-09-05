FROM php:8.3-apache

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    libzip-dev \
    zip \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install PHP extensions
RUN docker-php-ext-install pdo_mysql mbstring exif pcntl bcmath gd zip

# Install Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Set working directory
WORKDIR /var/www/html

# Copy composer files
COPY composer.json composer.lock* ./

# Install PHP dependencies (skip for now, install at runtime)
RUN echo "Skipping composer install during build"

# Copy application code
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p storage/logs storage/framework/cache storage/framework/sessions storage/framework/views \
    && chown -R www-data:www-data /var/www/html \
    && chmod -R 755 storage bootstrap/cache

# Configure Apache
RUN a2enmod rewrite
RUN echo '<VirtualHost *:80>\n\
    DocumentRoot /var/www/html/public\n\
    <Directory /var/www/html/public>\n\
        AllowOverride All\n\
        Require all granted\n\
    </Directory>\n\
    ErrorLog /proc/self/fd/2\n\
    CustomLog /proc/self/fd/1 combined\n\
    LogLevel warn\n\
</VirtualHost>' > /etc/apache2/sites-available/000-default.conf

# Install Datadog PHP extension
RUN curl -LO https://github.com/DataDog/dd-trace-php/releases/latest/download/datadog-setup.php \
    && php datadog-setup.php --php-bin=php --enable-appsec --enable-profiling

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
    && echo "DD_PROFILING_ENABLED=true" >> .env

# Generate application key (skip for now)
RUN echo "Skipping artisan key:generate"

# Expose port 80
EXPOSE 80

# Start Apache
CMD ["apache2-foreground"]
