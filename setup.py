from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='cycling-stats',
    version='0.1.0',
    author='Eva van Weenen',
    author_email='evanweenen@ethz.ch',
    description='Calculate advanced cycling statistics from power and/or heart rate data',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/evavanweenen/cycling-stats',
    license='MIT',
    packages=['cyclingstats'],
    scripts=['bin/run.py'],
    zip_safe=False,
    install_requires=['numpy', 'pandas']
    )