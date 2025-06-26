import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, TextSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('slam_nav')
    world_file = os.path.join(pkg_share, 'worlds', 'school.world')
    urdf_file = os.path.join(pkg_share, 'urdf', 'ugv_rover.urdf')
    
    use_gazebo_gui = DeclareLaunchArgument(
        'use_gazebo_gui',
        default_value='true',
        description='Whether to launch Gazebo GUI'
    )

    gz_sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ]),
        launch_arguments={
            'gz_args': [world_file if LaunchConfiguration('use_gazebo_gui').__eq__(TextSubstitution(text='true')) else f'-s {world_file}']
        }.items()
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': open(urdf_file).read()}]
    )

    return LaunchDescription([
        use_gazebo_gui,
        gz_sim_launch,
        robot_state_publisher_node,
    ])