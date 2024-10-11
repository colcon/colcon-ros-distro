# Copyright 2024 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

import logging
import os

from colcon_core.argument_default import is_default_value
from colcon_core.argument_default import wrap_default_value
from colcon_core.environment_variable import EnvironmentVariable
from colcon_core.logging import colcon_logger
from colcon_core.logging import get_effective_console_level
from colcon_core.package_descriptor import PackageDescriptor
from colcon_core.package_discovery import PackageDiscoveryExtensionPoint
from colcon_core.plugin_system import satisfies_version
from rosdistro import get_distribution_file
from rosdistro import get_index
from rosdistro import get_index_url

logger = colcon_logger.getChild(__name__)

ROS_DISTRO_ENVIRONMENT_VARIABLE = EnvironmentVariable(
    'ROS_DISTRO',
    'Set the default ROS distribution name, used if the corresponding command '
    'line argument is not specified')

ROSDISTRO_INDEX_URL_ENVIRONMENT_VARIABLE = EnvironmentVariable(
    'ROSDISTRO_INDEX_URL',
    'Set the URL of the rosdistro index containing packages to be discovered')


class RosDistroPackageDiscovery(PackageDiscoveryExtensionPoint):
    """Discover packages in a ROS distribution."""

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(
            PackageDiscoveryExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

        rosdistro_logger = logging.getLogger('rosdistro')
        log_level = get_effective_console_level(colcon_logger)
        rosdistro_logger.setLevel(log_level)

    def has_default(self):  # noqa: D102
        return True

    def add_arguments(  # noqa: D102
        self, *, parser, with_default, single_path=False
    ):
        parser.add_argument(
            '--ros-distro',
            default=(wrap_default_value(
                os.environ.get(
                    ROS_DISTRO_ENVIRONMENT_VARIABLE.name, 'rolling'))
                if with_default else None))

    def has_parameters(self, *, args):  # noqa: D102
        return all(
            (not is_default_value(value)) and bool(value)
            for value in (
                args.ros_distro,
            ))

    def discover(self, *, args, identification_extensions):  # noqa: D102
        assert not identification_extensions, \
            'colcon-ros-distro does not support explicit ' \
            'package identification extensions'
        return set(_discover(args.ros_distro))


def _discover(ros_distro):
    index_url = get_index_url()
    index = get_index(index_url)
    distro_file = get_distribution_file(index, ros_distro)

    for repo_name, repo in distro_file.repositories.items():
        if not repo.release_repository or not repo.release_repository.version:
            continue

        for pkg_name in repo.release_repository.package_names:
            desc = PackageDescriptor(f'{ros_distro}/{repo_name}')
            desc.name = pkg_name
            desc.type = 'ros_distro'
            yield desc
