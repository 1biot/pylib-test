from setuptools import find_packages, setup
setup(
    name='mqtt_topic_callback',
    packages=find_packages(include=['mqtt_topic_callback']),
    version='1.0.0',
    description='Callback handler for incoming mqtt messages',
    author='1biot',
    license='MIT',
)