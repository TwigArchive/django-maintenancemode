from setuptools import setup, find_packages


setup(
    name = "django-maintenancemode",
    version = "4.7",
    packages = find_packages(),
    include_package_data = True,
    author = "Twig",
    author_email = "web@twig-world.com",
    description = "A Djangoation that allows you to use" \
            " WYMEditor in your forms and admin.",
    license = "MIT License",
    keywords = "django widget WYMEditor",
    platforms = ['any'],
    url = "https://github.com/TwigWorld/django-maintenancemode",
)
