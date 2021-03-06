# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from collective.cover.content import ICover
from collective.cover.controlpanel import ICoverSettings
from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.testing import MULTIPLE_GRIDS_INTEGRATION_TESTING
from plone.app.dexterity.behaviors.exclfromnav import IExcludeFromNavigation
from plone.app.lockingbehavior.behaviors import ILocking
from plone.app.referenceablebehavior.referenceable import IReferenceable
from plone.app.stagingbehavior.interfaces import IStagingSupport
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.dexterity.interfaces import IDexterityFTI
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IAttributeUUID
from zope.component import createObject
from zope.component import getUtility
from zope.component import queryUtility

import json
import unittest


class CoverIntegrationTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']
        self.folder.invokeFactory('collective.cover.content', 'c1',
                                  template_layout='Layout A')
        self.c1 = self.folder['c1']

    def test_adding(self):
        self.assertTrue(ICover.providedBy(self.c1))

    def test_fti(self):
        fti = queryUtility(
            IDexterityFTI, name='collective.cover.content')
        self.assertIsNotNone(fti)

    def test_schema(self):
        fti = queryUtility(
            IDexterityFTI, name='collective.cover.content')
        schema = fti.lookupSchema()
        self.assertEqual(ICover, schema)

    def test_factory(self):
        fti = queryUtility(
            IDexterityFTI, name='collective.cover.content')
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(ICover.providedBy(new_object))

    def test_exclude_from_navigation_behavior(self):
        self.assertTrue(IExcludeFromNavigation.providedBy(self.c1))

    def test_locking_behavior(self):
        self.assertTrue(ILocking.providedBy(self.c1))

    def test_is_referenceable(self):
        self.assertTrue(IReferenceable.providedBy(self.c1))
        self.assertTrue(IAttributeUUID.providedBy(self.c1))

    def test_staging_behavior(self):
        self.assertTrue(IStagingSupport.providedBy(self.c1))

    def test_cover_selectable_as_folder_default_view(self):
        self.folder.setDefaultPage('c1')
        self.assertEqual(self.folder.getDefaultPage(), 'c1')

    def test_export_permission(self):
        # layout export is visible for user with administrative rights
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        layout_edit = self.c1.restrictedTraverse('layoutedit')
        self.assertTrue(layout_edit.can_export_layout())
        self.assertIn('<span>Export layout</span>', layout_edit())

        # Accessing layoutedit as simple Member is not allowed.
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.assertRaises(Unauthorized, self.c1.restrictedTraverse,
                          'layoutedit')

        # But we can cheat a bit here by reusing the layout_edit
        # object that has been visited as a Manager above.  The
        # layout export should still not be visible for this user.
        self.assertFalse(layout_edit.can_export_layout())
        self.assertNotIn('<span>Export layout</span>', layout_edit())

    def test_layoutmanager_settings(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        layout_edit = self.c1.restrictedTraverse('layoutedit')
        settings = json.loads(layout_edit.layoutmanager_settings())
        self.assertEqual(settings, {'ncolumns': 16})

    # TODO: add test for plone.app.relationfield.behavior.IRelatedItems


class CoverMultipleGridsIntegrationTestCase(unittest.TestCase):

    layer = MULTIPLE_GRIDS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']
        self.folder.invokeFactory('collective.cover.content', 'c1',
                                  template_layout='Layout A')
        self.c1 = self.folder['c1']

    def test_layoutmanager_settings(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        layout_edit = self.c1.restrictedTraverse('layoutedit')
        settings = json.loads(layout_edit.layoutmanager_settings())
        self.assertEqual(settings, {'ncolumns': 16})

        # Choose different grid.
        registry = getUtility(IRegistry)
        cover_settings = registry.forInterface(ICoverSettings)
        cover_settings.grid_system = 'bootstrap3'

        # The number of columns should be different now.
        settings = json.loads(layout_edit.layoutmanager_settings())
        self.assertEqual(settings, {'ncolumns': 12})
