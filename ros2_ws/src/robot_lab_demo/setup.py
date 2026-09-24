from glob import glob
from setuptools import find_packages, setup


package_name = "robot_lab_demo"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="LearnCV learner",
    maintainer_email="learner@example.com",
    description="Publishes a deterministic occupancy grid and A-star path.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "astar_publisher = robot_lab_demo.astar_publisher:main",
        ],
    },
)
