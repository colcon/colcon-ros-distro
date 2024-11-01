# Copyright 2024 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

from unittest.mock import Mock

from colcon_core.package_descriptor import PackageDescriptor
from colcon_ros_distro.package_discovery.ros_distro \
    import RosDistroPackageDiscovery
import pytest


@pytest.mark.usefixtures('use_sim_distro')
def test_discover():
    extension = RosDistroPackageDiscovery()
    extension.add_arguments(parser=Mock(), with_default=True)

    args = Mock()
    args.ros_distro = 'sim'
    descs = extension.discover(args=args, identification_extensions={})

    sim_pkg_a = PackageDescriptor('sim/sim_pkg_a')
    sim_pkg_a.name = 'sim_pkg_a'
    sim_pkg_a.type = 'ros_distro'

    assert descs and sim_pkg_a in descs


def test_defaults():
    extension = RosDistroPackageDiscovery()
    extension.add_arguments(parser=Mock(), with_default=True)

    assert extension.has_default()

    args = Mock()
    args.ros_distro = 'sim'
    assert extension.has_parameters(args=args)


def test_no_identification_extensions():
    extension = RosDistroPackageDiscovery()
    extension.add_arguments(parser=Mock(), with_default=True)

    args = Mock()
    args.ros_distro = 'sim'
    with pytest.raises(AssertionError):
        extension.discover(args=args, identification_extensions={Mock()})
