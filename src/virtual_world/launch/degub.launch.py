from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, TextSubstitution, NotSubstitution, AndSubstitution, OrSubstitution
from launch.actions import DeclareLaunchArgument, Shutdown, LogInfo, IncludeLaunchDescription, ExecuteProcess
from launch.conditions import LaunchConfigurationEquals, IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


ARGUMENTS = [

    # launch arguments
    DeclareLaunchArgument('sim',
        default_value=['true'],
        description='use with simulation'
    ),

    DeclareLaunchArgument('capabilities',
        default_value='[clientPublish,services,connectionGraph,assets]',
        description='capabilities for foxglove'
    ),

    DeclareLaunchArgument('rviz2',
        default_value='false',
        choices=['true', 'false'],
        description='use rviz2 for gui.'
    ),

    DeclareLaunchArgument('foxglove',
        default_value='true',
        choices=['true', 'false'],
        description='use foxglove for gui.'
    ),

    DeclareLaunchArgument('joy',
        default_value='true',
        choices=['true', 'false'],
        description='use joystick'
    ),

    DeclareLaunchArgument('log_level',
        default_value=['warn'],
        description='Logging level'
    ),

    DeclareLaunchArgument('vehicle',
        default_value=['b3rb'],
        description='vehicle'
    ),

    DeclareLaunchArgument('topic_whitelist',
        default_value=['["/camera/image_raw/compressed","/camera/camera_info","/cerebri/out/status","/cerebri/in/pixy_vector","/nxp_cup/debug_image","/calibration_camera_feed","/cerebri/out/nav_sat_fix","/global_costmap/costmap","/map","global_costmap/published_footprint","/plan","/robot_description","/tf", "/debug_images/vector_image", "/scan", "/cerebri/in/joy"]'],
        description='topic_whitelist for foxglove'
    ),

    DeclareLaunchArgument('service_whitelist',
        default_value=['[""]'],
        description='service_whitelist for foxglove'
    ),

    DeclareLaunchArgument('param_whitelist',
        default_value=['[""]'],
        description='param_whitelist for foxglove'
    )
]

def generate_launch_description():

    joy = Node(
        package='joy',
        output='log',
        executable='joy_node',
        condition=IfCondition(OrSubstitution(LaunchConfiguration('joy'),LaunchConfiguration('rviz2'))),
        arguments=['--ros-args', '--log-level', LaunchConfiguration('log_level')],
        parameters=[
            {'use_sim_time': LaunchConfiguration('sim')},
            {'coalesce_interval_ms': 50},
            {'autorepeat_rate': 20.0},
            {'deadzone': 0.02},
            ],
        remappings=[
            ("joy", "cerebri/in/joy"),
        ],
        on_exit=Shutdown()
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        condition=IfCondition(LaunchConfiguration('rviz2')),
        arguments=[
            '-d', [PathJoinSubstitution([FindPackageShare('virtual_world'), 'config',
            LaunchConfiguration('vehicle')]), '.rviz'], '--ros-args', '--log-level',
            LaunchConfiguration('log_level')],
        parameters=[{'use_sim_time': LaunchConfiguration('sim')}],
        on_exit=Shutdown(),
    )


    foxglove_websockets = IncludeLaunchDescription(
        XMLLaunchDescriptionSource([PathJoinSubstitution(
            [get_package_share_directory('foxglove_bridge'), 'launch', 'foxglove_bridge_launch.xml'])]),
        condition=IfCondition(AndSubstitution(AndSubstitution(LaunchConfiguration('foxglove'),LaunchConfiguration('sim')),NotSubstitution(LaunchConfiguration('rviz2')))),
        launch_arguments=[('capabilities', LaunchConfiguration('capabilities')),
                        ('topic_whitelist', LaunchConfiguration('topic_whitelist')),
                        ('service_whitelist', LaunchConfiguration('service_whitelist')),
                        ('param_whitelist', LaunchConfiguration('param_whitelist')),
                        ('use_sim_time', LaunchConfiguration('sim'))])

    foxglove_studio = ExecuteProcess(
            cmd = [f"foxglove-studio"],
            name='foxglove-studio',
            condition=IfCondition(AndSubstitution(LaunchConfiguration('foxglove'),NotSubstitution(LaunchConfiguration('rviz2')))),
            output='log',
            sigterm_timeout='1',
            sigkill_timeout='1',
            on_exit=Shutdown()
            )


    return LaunchDescription(ARGUMENTS + [
        joy,
        rviz_node,
        foxglove_websockets,
        foxglove_studio
    ])
