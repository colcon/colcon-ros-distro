colcon-ros-distro
=================

An extension for `colcon-core <https://github.com/colcon/colcon-core>`_ to discover packages in a ROS distribution.

This package provides package discovery and augmentation extensions for enumerating packages in a `REP 153 <https://www.ros.org/reps/rep-0153.html>`_ ROS distribution file.
It currently supports only the 'release' stanza of the distribution file, meaning that packages with only a 'source' stanza will not be enumerated.

Unlike some other colcon extension packages, this package does not register any of the extensions it defines for use in colcon-core.
It therefore serves only as a library for other tools in the colcon ecosystem to use by registering these extensions at appropriate extension points.
