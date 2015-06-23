from setuptools import setup, find_packages
import ghost

setup(
    name='ghostrunner',
    version=ghost.__version__,
    url='https://github.com/wearespindle/ghostrunner',
    license='mit',
    author='Jean-Philippe Serafin',
    author_email='serafinjp@gmail.com',
    description='Ghost.py fork that focuses on running fast functional tests in Django.',
    long_description=open('README.rst').read(),
    data_files=[('ghost', ['README.rst', ])],
    include_package_data=True,
    install_requires=[
        'Django>=1.4.13',
    ],
    packages=find_packages(),
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
