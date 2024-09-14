# Copyright (c) 2023 CogniPilot Foundation
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node

# Launch Arguments
ARGUMENTS = [
    DeclareLaunchArgument('x', default_value=['11'], #2.90
        description='x position'),
    DeclareLaunchArgument('y', default_value=['2.5'], #0.0
        description='y position'),
    DeclareLaunchArgument('z', default_value=['0.10'],
        description='z position'),
    DeclareLaunchArgument('yaw', default_value=['1.5'], #1.02
        description='yaw position'),
    DeclareLaunchArgument('sync', default_value='false',
                          choices=['true', 'false'],
                          description='Run async or sync SLAM'),
    DeclareLaunchArgument('localization', default_value='slam',
                          choices=['off', 'localization', 'slam'],
                          description='Whether to run localization or SLAM'),
    DeclareLaunchArgument('nav2', default_value='true',
                          choices=['true', 'false'],
                          description='Run nav2'),
    DeclareLaunchArgument('corti', default_value='true',
                          choices=['true', 'false'],
                          description='Run corti'),
    DeclareLaunchArgument('cerebri', default_value='true',
                          choices=['true', 'false'],
                          description='Run cerebri'),
    DeclareLaunchArgument('bridge', default_value='true',
                          choices=['true', 'false'],
                          description='Run bridges'),
    DeclareLaunchArgument('synapse_ros', default_value='true',
                          choices=['true', 'false'],
                          description='Run synapse_ros'),
    DeclareLaunchArgument('synapse_gz', default_value='true',
                          choices=['true', 'false'],
                          description='Run synapse_gz'),
    DeclareLaunchArgument('description', default_value='true',
                          choices=['true', 'false'],
                          description='Run description'),
    DeclareLaunchArgument('world', default_value='virtual_world',
                          description='GZ World'),
    DeclareLaunchArgument('track_vision', default_value='true',
                          choices=['true', 'false'],
                          description='Track vision node'),
    DeclareLaunchArgument('debug_track_vision', default_value='true',
                          choices=['true', 'false'],
                          description='Debug Track vision node'),
    DeclareLaunchArgument(
        'map_yaml',
        default_value=[LaunchConfiguration('world'), '.yaml'],
        description='Map yaml'),
    DeclareLaunchArgument('cerebri_gdb', default_value='false',
                          choices=['true', 'false'],
                          description='Run cerebri with gdb debugger.'),
    DeclareLaunchArgument('spawn_model', default_value='true',
                          choices=['true', 'false'],
                          description='Spawn B3RB Model'),
    DeclareLaunchArgument('use_sim_time', default_value='true',
                          choices=['true', 'false'],
                          description='Use sim time'),
    DeclareLaunchArgument('log_level', default_value='error',
                          choices=['info', 'warn', 'error'],
                          description='log level'),
    
    # Updated topic whitelist argument for Foxglove
    DeclareLaunchArgument('topic_whitelist',
        default_value=['["/camera/image_raw/compressed","/camera/camera_info", "/edge_vectors", "/debug_images/thresh_image", "/debug_images/vector_image","/robot_description"]'],
        description='topic_whitelist for foxglove'
    ),
]

def generate_launch_description():
    pkg_virtual_world = Path(get_package_share_directory('virtual_world'))
    urdf_file = pkg_virtual_world / 'urdf'/ 'buggy.urdf'
    with open(urdf_file, 'r') as f:
        robot_desc = f.read()
        
    line_follower_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='line_follower_state_publisher',
        output='screen',
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
            {'robot_description': robot_desc},
        ],
        arguments=['--ros-args', '--log-level', LaunchConfiguration('log_level')],
        remappings=[
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static')
        ]
    )
    
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([PathJoinSubstitution(
            [get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])]),
        launch_arguments=[('gz_args', [
            LaunchConfiguration('world'), '.sdf', ' -v 0', ' -r'
            ])]
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        arguments=[
            '-world', 'default',
            '-name', 'robot_car',
            '-x', LaunchConfiguration('x'),
            '-y', LaunchConfiguration('y'),
            '-z', LaunchConfiguration('z'),
            '-Y', LaunchConfiguration('yaw'),
            '-file', PathJoinSubstitution([get_package_share_directory(
                'virtual_world'),
                'sdf/buggy/model.sdf'])
        ],
        output='screen',
        condition=IfCondition(LaunchConfiguration("spawn_model")))

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='bridge_gz_ros_clock',
        output='screen',
        condition=IfCondition(LaunchConfiguration('bridge')),
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time')
            }],
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
    )

    camera_info_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='bridge_gz_ros_camera_info',
        output='screen',
        condition=IfCondition(LaunchConfiguration('bridge')),
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time')
        }],
        arguments=[
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo'
        ])

    camera_bridge = Node(
        package='ros_gz_image',
        executable='image_bridge',
        name='bridge_gz_ros_camera',
        output='screen',
        condition=IfCondition(LaunchConfiguration('bridge')),
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time')
        }],
        arguments=['/camera/image_raw'])

    cmd_vel_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='bridge_gz_ros_cmd_vel',
        output='screen',
        condition=IfCondition(LaunchConfiguration('bridge')),
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time')
        }],
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist'
        ])
        
    return LaunchDescription(ARGUMENTS + [
        line_follower_state_publisher,
        gz_sim, 
        spawn_robot,
        clock_bridge,
        camera_info_bridge,
        camera_bridge,
        cmd_vel_bridge,
    ])

