from setuptools import setup

setup(
   name='Scraper',
   version='1.0.1',
   description='Review Scraper',
   author='YeongRoYun',
   author_email='appleofyyr@icloud.com',
   packages=['scraper'],  # would be the same as name
   install_requires=['PyMySQL', 'sqlalchemy', 'requests', 'bs4'], #external packages acting as dependencies
)