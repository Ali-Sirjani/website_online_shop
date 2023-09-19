
# Website Online Shop

## E-commerce Platform with Multilingual Support

Website Online Shop is an e-commerce platform built using the Django framework. It allows users to browse and purchase products from the site, with the option to access and buy products even without logging in. Users can also like products to save them for later. The site is available in both Persian and English, although the templates are primarily designed for the Persian language. Please note that some areas of the templates may not be fully optimized for the English language.

Additionally, users have the convenience of logging in using their Google accounts for a seamless shopping experience.

## Installation

To set up and run the Website Online Shop project, follow these steps:

1. **Create a .env File:**
   Create a `.env` file in the project's root directory and configure the following environment variables:

   ```plaintext
   DOCKER_COMPOSE_DJANGO_SECRET_KEY=your-secret-key
   DOCKER_COMPOSE_DJANGO_DEBUG=debug-value
   ```

   If you prefer to display emails in the console and not use Gmail for sending emails, you can skip these variables:

   ```plaintext
   DOCKER_COMPOSE_EMAIL_HOST=your-email-host
   DOCKER_COMPOSE_EMAIL_HOST_PASSWORD=your-email-password
   ```

   Remove the following lines from `settings.py`:

   ```python
   EMAIL_USE_TLS
   EMAIL_HOST
   EMAIL_PORT
   EMAIL_HOST_USER
   DEFAULT_FROM_EMAIL
   EMAIL_HOST_PASSWORD
   ```

   Add this line to `settings.py` to use console email backend:

   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
   ```

2. **Run Docker Compose:**
   Start the Docker containers using Docker Compose:

   ```bash
   docker-compose up
   ```

3. **Apply Migrations:**

   ```bash
   docker-compose exec web python manage.py makemigrations
   docker-compose exec web python manage.py migrate
   ```

4. **Run the Server:**
   The project should now be accessible at `http://localhost:8000/`. You can explore the website and begin your online shopping experience.

## Third-Party Apps

Website Online Shop utilizes the following third-party apps:

- `allauth`: Provides authentication and account management functionality.
- `rosetta`: Facilitates translations and multilingual support for the site.

