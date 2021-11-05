from setuptools import find_packages, setup

setup(
    name='clubbi_utils',
    packages=find_packages(include=['src/']),
    version='0.1.0',
    description='Clubbi commons and helper functions',
    author='Me',
    license='MIT',
    install_requires=[],
    setup_requires=[''],
    tests_require=[''],
    test_suite='tests',
)
