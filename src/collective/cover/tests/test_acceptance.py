import unittest

import robotsuite

from plone.testing import layered

from collective.cover.testing import FUNCTIONAL_TESTING


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite("test_cover.txt"),
                layer=FUNCTIONAL_TESTING),
        layered(robotsuite.RobotTestSuite("test_layout.txt"),
                layer=FUNCTIONAL_TESTING),
        layered(robotsuite.RobotTestSuite("test_collection_tile.txt"),
                layer=FUNCTIONAL_TESTING),
    ])
    return suite