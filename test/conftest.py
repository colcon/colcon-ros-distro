# Copyright 2024 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

import os
from unittest import mock

from git import Repo
import pytest
from rosdistro import get_index
from rosdistro.distribution_cache_generator import generate_distribution_cache
import yaml


def _create_package(path, manifest):
    (path / 'package.xml').write_text(manifest)
    with mock.patch.dict(os.environ, {
        'GIT_AUTHOR_NAME': 'Nobody',
        'GIT_AUTHOR_EMAIL': 'nobody@example.com',
        'GIT_COMMITTER_NAME': 'Nobody',
        'GIT_COMMITTER_EMAIL': 'nobody@example.com',
    }):
        with Repo.init(path) as repo:
            repo.index.commit('Initial commit')
            repo.create_head('main').checkout()
            repo.index.add('package.xml')
            repo.index.commit('Add package manifest')
            repo.create_tag('0.0.0', message='0.0.0')


@pytest.fixture(scope='session')
def sim_pkg_a(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp('sim_pkg_a')
    manifest = '\n'.join((
        '<package format="3">',
        '  <name>sim_pkg_a</name>',
        '  <version>0.0.0</version>',
        '  <description>Simulated package A.</description>',
        '  <maintainer email="nobody@example.com">Nobody</maintainer>',
        '  <license>Apache-2.0</license>',
        '</package>',
        '',
    ))

    _create_package(tmp_path, manifest)

    return tmp_path


@pytest.fixture(scope='session')
def sim_pkg_b(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp('sim_pkg_b')
    manifest = '\n'.join((
        '<package format="3">',
        '  <name>sim_pkg_b</name>',
        '  <version>0.0.0</version>',
        '  <description>Simulated package B.</description>',
        '  <maintainer email="nobody@example.com">Nobody</maintainer>',
        '  <license>Apache-2.0</license>',
        '  <depend>sim_pkg_a</depend>',
        '  <member_of_group>sim_group</member_of_group>',
        '</package>',
        '',
    ))

    _create_package(tmp_path, manifest)

    return tmp_path


@pytest.fixture(scope='session')
def sim_pkg_c(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp('sim_pkg_c')
    manifest = '\n'.join((
        '<package format="3">',
        '  <name>sim_pkg_c</name>',
        '  <version>0.0.0</version>',
        '  <description>Simulated package C.</description>',
        '  <maintainer email="nobody@example.com">Nobody</maintainer>',
        '  <license>Apache-2.0</license>',
        '  <group_depend>sim_group</group_depend>',
        '</package>',
        '',
    ))

    _create_package(tmp_path, manifest)

    return tmp_path


@pytest.fixture(scope='session')
def sim_distro(tmp_path_factory, sim_pkg_a, sim_pkg_b, sim_pkg_c):
    tmp_path = tmp_path_factory.mktemp('sim_distro')
    index_path = tmp_path / 'index.yaml'
    distribution_path = tmp_path / 'distribution.yaml'
    distribution_cache_path = tmp_path / 'distribution-cache.yaml'

    index_path.write_text('\n'.join((
        '%YAML 1.1',
        '# ROS index file',
        '# see REP 153: http://ros.org/reps/rep-0153.html',
        '---',
        'distributions:',
        '  sim:',
        '    distribution: [distribution.yaml]',
        '    distribution_cache: distribution-cache.yaml',
        '    distribution_status: rolling',
        '    distribution_type: ros2',
        '    python_version: 3',
        'type: index',
        'version: 4',
    )))

    distribution_path.write_text('\n'.join((
        '%YAML 1.1',
        '# ROS distribution file',
        '# see REP 143: http://ros.org/reps/rep-0143.html',
        '---',
        'repositories:',
        '  sim_pkg_a:',
        '    release:',
        '      tags:',
        '        release: 0.0.0',
        f'      url: {sim_pkg_a.as_uri()}',
        '      version: 0.0.0',
        '  sim_pkg_b:',
        '    release:',
        '      tags:',
        '        release: 0.0.0',
        f'      url: {sim_pkg_b.as_uri()}',
        '      version: 0.0.0',
        '  sim_pkg_c:',
        '    release:',
        '      tags:',
        '        release: 0.0.0',
        f'      url: {sim_pkg_c.as_uri()}',
        '      version: 0.0.0',
        '  yanked_pkg:',
        '    release:',
        '      tags:',
        '        release: 0.0.0',
        '      url: file:///dev/null',
        'type: distribution',
        'version: 2',
    )))

    index = get_index(index_path.as_uri())
    cache = generate_distribution_cache(index, 'sim', ignore_local=True)
    with distribution_cache_path.open('w') as f:
        yaml.dump(cache.get_data(), f)

    return index_path


@pytest.fixture
def use_sim_distro(sim_distro):
    with mock.patch.dict(
        os.environ,
        {
            'ROSDISTRO_INDEX_URL': sim_distro.as_uri(),
        },
    ):
        yield
