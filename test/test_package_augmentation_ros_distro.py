# Copyright 2024 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

from colcon_core.package_descriptor import PackageDescriptor
from colcon_ros_distro.package_augmentation.ros_distro \
    import RosDistroPackageAugmentation
import pytest


@pytest.mark.usefixtures('use_sim_distro')
def test_augment():
    extension = RosDistroPackageAugmentation()

    sim_pkg_a = PackageDescriptor('sim/sim_pkg_a')
    sim_pkg_a.name = 'sim_pkg_a'
    sim_pkg_a.type = 'ros_distro'

    sim_pkg_b = PackageDescriptor('sim/sim_pkg_b')
    sim_pkg_b.name = 'sim_pkg_b'
    sim_pkg_b.type = 'ros_distro'

    sim_pkg_c = PackageDescriptor('sim/sim_pkg_c')
    sim_pkg_c.name = 'sim_pkg_c'
    sim_pkg_c.type = 'ros_distro'

    other_pkg_type = PackageDescriptor('/dev/null')
    other_pkg_type.name = 'other_pkg'
    other_pkg_type.type = 'something_else'

    pkgs = {sim_pkg_a, sim_pkg_b, sim_pkg_c, other_pkg_type}

    extension.augment_packages(pkgs)

    assert sim_pkg_a.metadata.get('version') == '0.0.0'
    assert sim_pkg_a.metadata.get('maintainers') == [
        'Nobody <nobody@example.com>',
    ]
    assert set(sim_pkg_a.dependencies.keys()) == {'build', 'run', 'test'}
    assert not sim_pkg_a.dependencies['build']
    assert not sim_pkg_a.dependencies['run']
    assert not sim_pkg_a.dependencies['test']

    assert sim_pkg_b.metadata.get('version') == '0.0.0'
    assert sim_pkg_b.metadata.get('maintainers') == [
        'Nobody <nobody@example.com>',
    ]
    assert set(sim_pkg_b.dependencies.keys()) == {'build', 'run', 'test'}
    assert sim_pkg_b.dependencies['build'] == {'sim_pkg_a'}
    assert sim_pkg_b.dependencies['run'] == {'sim_pkg_a'}
    assert not sim_pkg_b.dependencies['test']

    assert sim_pkg_c.metadata.get('version') == '0.0.0'
    assert sim_pkg_c.metadata.get('maintainers') == [
        'Nobody <nobody@example.com>',
    ]
    assert set(sim_pkg_c.dependencies.keys()) == {'build', 'run', 'test'}
    assert sim_pkg_c.dependencies['build'] == {'sim_pkg_b'}
    assert sim_pkg_c.dependencies['run'] == {'sim_pkg_b'}
    assert not sim_pkg_c.dependencies['test']
