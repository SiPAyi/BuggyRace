from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, TextSubstitution, NotSubstitution, AndSubstitution
from launch.actions import DeclareLaunchArgument, Shutdown, IncludeLaunchDescription, ExecuteProcess
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory

ARGUMENTS = [

    # Launch arguments
    DeclareLaunchArgument('sim',
        default_value=['true'],
        description='use with simulation'
    ),

    DeclareLaunchArgument('capabilities',
        default_value='[clientPublish,services,connectionGraph,assets]',
        description='capabilities for foxglove'
    ),

    DeclareLaunchArgument('foxglove',
        default_value='true',
        choices=['true', 'false'],
        description='use foxglove for gui.'
    ),

    DeclareLaunchArgument('log_level',
        default_value=['warn'],
        description='Logging level'
    ),

    DeclareLaunchArgument('vehicle',
        default_value=['b3rb'],
        description='vehicle'
    ),

    # Updated topic whitelist argument for Foxglove
    DeclareLaunchArgument('topic_whitelist',
        default_value=['["/camera/image_raw/compressed","/camera/camera_info", "/edge_vectors", "/debug_images/thresh_image", "/debug_images/vector_image","/robot_description"]'],
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

    foxglove_websockets = IncludeLaunchDescription(
        XMLLaunchDescriptionSource([PathJoinSubstitution(
            [get_package_share_directory('foxglove_bridge'), 'launch', 'foxglove_bridge_launch.xml'])]),
        condition=IfCondition(AndSubstitution(LaunchConfiguration('foxglove'), LaunchConfiguration('sim'))),
        launch_arguments=[('capabilities', LaunchConfiguration('capabilities')),
                          ('topic_whitelist', LaunchConfiguration('topic_whitelist')),
                          ('service_whitelist', LaunchConfiguration('service_whitelist')),
                          ('param_whitelist', LaunchConfiguration('param_whitelist')),
                          ('use_sim_time', LaunchConfiguration('sim'))])

    foxglove_studio = ExecuteProcess(
        cmd=["foxglove-studio",  # Command to start Foxglove Studio],
        name='foxglove-studio',
        condition=IfCondition(LaunchConfiguration('foxglove')),
        output='log',
        sigterm_timeout='1',
        sigkill_timeout='1',
        on_exit=Shutdown()
    )

    return LaunchDescription(ARGUMENTS + [
        foxglove_websockets,
        foxglove_studio
    ])

