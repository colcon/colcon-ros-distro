# Copyright 2024 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

from catkin_pkg.package import parse_package_string
from colcon_core.package_augmentation import PackageAugmentationExtensionPoint
from colcon_core.plugin_system import satisfies_version
from colcon_ros.package_identification.ros import add_group_dependencies
from colcon_ros.package_identification.ros import augment_package
from rosdistro import get_cached_distribution
from rosdistro import get_index
from rosdistro import get_index_url
from rosdistro import get_package_condition_context


class RosDistroPackageAugmentation(PackageAugmentationExtensionPoint):
    """Augment ROS distro packages with information from the manifests."""

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(
            PackageAugmentationExtensionPoint.EXTENSION_POINT_VERSION,
            '^1.0')

    def augment_packages(  # noqa: D102
        self, descs, *, additional_argument_names=None
    ):
        index_url = get_index_url()
        index = get_index(index_url)

        pkgs = {}

        distros = {}

        for desc in descs:
            if desc.type != 'ros_distro':
                continue

            ros_distro = str(desc.path.parts[0])
            condition_context = get_package_condition_context(
                index, ros_distro)

            distro = distros.get(ros_distro)
            if not distro:
                distro = get_cached_distribution(index, ros_distro)
                distros[ros_distro] = distro

            manifest = distro.get_release_package_xml(desc.name)

            pkg = parse_package_string(manifest)
            pkg.evaluate_conditions(condition_context)
            augment_package(desc, pkg)

            pkgs[pkg] = desc

        add_group_dependencies(pkgs)
