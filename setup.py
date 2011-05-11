from setuptools import setup


setup(
    name = "plivohelper",
    py_modules = ['plivohelper'],
    version = "0.1",
    description = "Plivo API client and RESTXML generator",
    author = "Plivo Team",
    author_email = "contact@plivo.org",
    url = "https://github.com/miglu/plivo-python-client",
    keywords = ["plivo","rest"],
    classifiers = [
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Development Status :: 1 - Beta",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Telephony"
        ],
    long_description = """\
        Python Plivo Cient Helper Library
         """ )
