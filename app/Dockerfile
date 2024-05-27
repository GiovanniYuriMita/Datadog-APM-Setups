# Use the official PHP image
FROM php:8.3.7-apache

# Enable Apache mod_rewrite
RUN a2enmod rewrite

# Copy custom Apache configuration
COPY my-apache2.conf /etc/apache2/sites-available/000-default.conf

# Copy the Datadog setup script
COPY datadog-setup.php /usr/local/bin/datadog-setup.php

# Install Datadog PHP tracing client
RUN php /usr/local/bin/datadog-setup.php --php-bin=all

# Copy the application files
COPY app /var/www/html/

# Set permissions for the web root directory
RUN chown -R www-data:www-data /var/www/html && chmod -R 755 /var/www/html

# Set working directory
WORKDIR /var/www/html

# Expose port 80
EXPOSE 80