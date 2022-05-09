from setuptools import setup

setup(
   name='scraper',
   version='0.0.1',
   description='Review Scraper',
   author='YeongRoYun',
   author_email='sample@test.com',
   packages=['scraper'],  # would be the same as name
   install_requires=['PyMySQL', 'sqlalchemy', 'requests', 'bs4'], #external packages acting as dependencies
)