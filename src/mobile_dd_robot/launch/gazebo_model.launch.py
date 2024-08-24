import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription  # 수정된 임포트
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
import xacro

def generate_launch_description():
    # 로봇 이름과 패키지 이름 설정
    robotXacroName = 'differential_drive_robot'
    namePackage = 'mobile_dd_robot'
    modelFileRelativePath = 'model/robot.xacro'
    worldFileRelativePath = 'model/empty_world.world'

    # 모델 및 월드 파일의 절대 경로 생성
    pathModelFile = os.path.join(get_package_share_directory(namePackage), modelFileRelativePath)
    pathWorldFile = os.path.join(get_package_share_directory(namePackage), worldFileRelativePath)

    # Xacro 파일로부터 로봇 설명(XML) 생성
    robotDescription = xacro.process_file(pathModelFile).toxml()
    
    gazebo_rosPackageLaunch = PythonLaunchDescriptionSource(
        os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py'))

    gazeboLaunch = IncludeLaunchDescription(
        gazebo_rosPackageLaunch, launch_arguments={'world': pathWorldFile}.items())

    # Gazebo에 로봇 엔티티를 스폰하기 위한 노드 생성
    spawnNode = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', robotXacroName], output='screen')

    # 로봇 상태 퍼블리셔 노드 생성
    nodeRobotStatePublisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robotDescription},
            {'use_sim_time': True}
        ]
    )

    launchDescriptionObject = LaunchDescription()

    launchDescriptionObject.add_action(gazeboLaunch)
    launchDescriptionObject.add_action(spawnNode)
    launchDescriptionObject.add_action(nodeRobotStatePublisher)

    return launchDescriptionObject

