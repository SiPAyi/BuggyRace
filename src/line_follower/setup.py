from setuptools import find_packages, setup

package_name = 'line_follower'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sai',
    maintainer_email='saikr2005@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'detect = line_follower.line_detector:main',
            'follower = line_follower.line_follower:main',
            'good_detect = line_follower.good_line_detector:main',
            'good_follower = line_follower.good_line_follower:main'
        ],
    },
)
