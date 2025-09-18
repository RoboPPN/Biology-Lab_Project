import os
from setuptools import setup, find_packages

# 获取 setup.py 所在目录
here = os.path.abspath(os.path.dirname(__file__))

setup(
    name='gripper_sdk',
    version='0.0.1',
    setup_requires=['setuptools>=40.0'],
    
    license='MIT License',
    packages=find_packages(include=['gripper_sdk', 'gripper_sdk.*']),
    include_package_data=True,
    package_data={
        '': ['LICENSE', '*.sh', '*.MD'],
        # 'gripper_sdk/asserts': ['*'],
    },
    install_requires=[
        'python-can>=3.3.4',
    ],
    entry_points={},
    author='Agilex Robotice Co., Ltd.',
    author_email='',
    description='A sdk to control Agilex motor driver',
    platforms=['Linux'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',

)
