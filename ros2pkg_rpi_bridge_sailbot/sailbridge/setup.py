from setuptools import setup

package_name = 'sailbridge'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='your_email@example.com',
    description='ROS 2 package for controlling a miniature sailboat rudder and sail',
    license='Your license',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'sailbridge_node = sailbridge.sailbridge_node:main',
            'joystick_control_node = sailbridge.joystick_control_node:main',
        ],
    },
)
