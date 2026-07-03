from setuptools import find_packages, setup

package_name = "can_pract"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="hs",
    maintainer_email="hs@todo.todo",
    description="TODO: Package description",
    license="TODO: License declaration",
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            "button_client = can_pract.button_client:main",
            "service_server = can_pract.service_server:main",
            "action_server = can_pract.action_server:main",
            "status_monitor = can_pract.status_monitor:main",
        ],
    },
)
