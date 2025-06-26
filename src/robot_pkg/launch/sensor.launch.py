import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, TimerAction
from launch.substitutions import LaunchConfiguration, TextSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_share = get_package_share_directory('robot_pkg')
    urdf_file = os.path.join(pkg_share, 'urdf', 'ugv_rover.urdf')
    world_file = os.path.join(pkg_share, 'worlds', 'world0.world')
    # 添加 config_file 路径（假设为空或自定义 YAML 文件）
    config_file = os.path.join(pkg_share, 'config', 'bridge.yaml')  # 需创建或留空

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

    spawn_model_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'ros_gz_spawn_model.launch.py')
        ]),
        launch_arguments={
            'world': 'demo',
            'file': urdf_file,
            'entity_name': 'ugv_rover',
            'bridge_name': 'ugv_rover_bridge',
            'config_file': config_file,  # 添加 config_file
            'x': '0.0',
            'y': '0.0',
            'z': '0.1'
        }.items()
    )

    delayed_spawn = TimerAction(period=10.0, actions=[spawn_model_launch])

    return LaunchDescription([
        use_gazebo_gui,
        gz_sim_launch,
        delayed_spawn,
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='gz_bridge',

            arguments=[
                '/clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock',  # 时钟话题
                '/camera/image_raw@sensor_msgs/msg/Image@gz.msgs.Image',  # RGB图像
                '/camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo',  # 相机信息
            ],
            output='screen',
            parameters=[{'use_sim_time': True}],
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            arguments=[urdf_file],
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            parameters=[{'use_sim_time': True}],
        ),
    ])