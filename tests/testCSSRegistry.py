#
# CSSRegistryTestCase 
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CSSRegistry.tests import CSSRegistryTestCase

from Products.CSSRegistry.config import TOOLNAME
from Products.CSSRegistry.interfaces import ICSSRegistry
from Interface.Verify import verifyObject

class TestImplementation(CSSRegistryTestCase.CSSRegistryTestCase):

    def afterSetUp(self):
        pass

    def test_interfaces(self):
        tool = getattr(self.portal, TOOLNAME)
        self.failUnless(ICSSRegistry.isImplementedBy(tool))
        self.failUnless(verifyObject(ICSSRegistry, tool))

class TestTool(CSSRegistryTestCase.CSSRegistryTestCase):

    def afterSetUp(self):
        pass

    def testToolExists(self):
        self.failUnless(TOOLNAME in self.portal.objectIds())
        
    def testZMIForm(self):
        tool = getattr(self.portal, TOOLNAME)
        self.setRoles(['Manager'])
        self.failUnless(tool.manage_cssForm())
        

class TestSkin(CSSRegistryTestCase.CSSRegistryTestCase):

    def afterSetUp(self):
        pass

    def testSkins(self):
        skins = self.portal.portal_skins.objectIds()
        self.failUnless('CSSRegistry' in skins) 

    def testSkinExists(self):
        self.failUnless(getattr(self.portal, 'renderAllTheStylesheets' ))


class testZMIMethods(CSSRegistryTestCase.CSSRegistryTestCase):
    
    def afterSetUp(self):
        self.tool = getattr(self.portal, TOOLNAME)
        self.tool.stylesheets = []
                
    def testAdd(self):
        self.tool.manage_addStylesheet(id='joe')
        self.assertEqual(len(self.tool.getStylesheets()),1)
        self.failUnless(self.tool.getStylesheets())
 

class TestStylesheetRegistration(CSSRegistryTestCase.CSSRegistryTestCase):

    def afterSetUp(self):
        self.tool = getattr(self.portal, TOOLNAME)
        self.tool.stylesheets = []

    def testStoringStylesheet(self):
        self.tool.registerStylesheet('foo')
        
        self.assertEqual(len(self.tool.getStylesheets()), 1)
        self.assertEqual(self.tool.getStylesheets()[0].get('id'), 'foo')

    def testDisallowingDuplicateIds(self):
        self.tool.registerStylesheet('foo')
        self.assertRaises(ValueError , self.tool.registerStylesheet , 'foo')
        
    def testPloneCustomStaysOnTop(self):

        self.tool.registerStylesheet('foo')        
        self.tool.registerStylesheet('ploneCustom.css')
        self.assertEqual(len(self.tool.getStylesheets()), 2)
        self.assertEqual(self.tool.getStylesheets()[0].get('id'), 'ploneCustom.css')
        self.assertEqual(self.tool.getStylesheets()[1].get('id'), 'foo')

    def testUnregisterStylesheet(self):
        self.tool.registerStylesheet('foo')        
        self.assertEqual(len(self.tool.getStylesheets()), 1)
        self.assertEqual(self.tool.getStylesheets()[0].get('id'), 'foo')
        self.tool.unregisterStylesheet('foo')
        self.assertEqual(len(self.tool.getStylesheets()), 0)
        
class TestToolSecurity(CSSRegistryTestCase.CSSRegistryTestCase):
    
    def afterSetUp(self):
        self.tool = getattr(self.portal, TOOLNAME)
        self.tool.stylesheets = []

    def testRegistrationSecurity(self):
        from AccessControl import Unauthorized
        self.assertRaises(Unauthorized, self.tool.restrictedTraverse , 'registerStylesheet')        
        self.assertRaises(Unauthorized, self.tool.restrictedTraverse , 'unregisterStylesheet')        
        self.setRoles(['Manager'])
        try:
            self.tool.restrictedTraverse('registerStylesheet')  
            self.tool.restrictedTraverse('unregisterStylesheet')  
        except Unauthorized:
            self.fail()      


class TestToolExpression(CSSRegistryTestCase.CSSRegistryTestCase):
    
    def afterSetUp(self):
        self.tool = getattr(self.portal, TOOLNAME)
        self.tool.stylesheets = []

    def testSimplestExpression(self):
        context = self.portal
        self.failUnless(self.tool.evaluateExpression('python:1', context ))
        self.failIf(self.tool.evaluateExpression('python:0', context ))
        self.failUnless(self.tool.evaluateExpression('python:0+1', context ))

    def testNormalExpression(self):
        context = self.portal
        self.failUnless(self.tool.evaluateExpression('object/absolute_url', context ))

    def testExpressionInFolder(self):
        self.folder.invokeFactory('Document', 'eggs')
        context = self.folder
        self.failUnless(self.tool.evaluateExpression('python:"eggs" in object.objectIds()', context ))
        
class TestStylesheetCooking(CSSRegistryTestCase.CSSRegistryTestCase):
    
    def afterSetUp(self):
        self.tool = getattr(self.portal, TOOLNAME)
        self.tool.stylesheets = []
        
    def testStylesheetCooking(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')
                
        self.assertEqual(len(self.tool.getStylesheets()), 3)
        self.assertEqual(len(self.tool.cookedstylesheets), 1)
        self.assertEqual(len(self.tool.concatenatedstylesheets.keys()), 4)

    def testStylesheetCookingValues(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')

        self.assertEqual(self.tool.concatenatedstylesheets[self.tool.cookedstylesheets[0].get('id')], ['eggs', 'spam', 'ham'] )
        
        
    def testGetEvaluatedStylesheetsCollapsing(self ):        
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')
        self.assertEqual(len(self.tool.getEvaluatedStylesheets(self.folder)) , 1 )

    def testMoreComplexStylesheetsCollapsing(self ):        
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam',           media='spam')
        self.tool.registerStylesheet('spam spam',      media='spam')
        self.tool.registerStylesheet('spam spam spam', media='spam')
        self.tool.registerStylesheet('eggs')
        self.assertEqual(len(self.tool.getEvaluatedStylesheets(self.folder)) , 3 )
        ids = [item.get('id') for item in self.tool.getEvaluatedStylesheets(self.folder)]
        self.failUnless('ham' in ids )
        self.failUnless('eggs' in ids )
        self.failIf('spam' in ids )
        self.failIf('spam spam' in ids )
        self.failIf('spam spam spam' in ids )
        
    def testGetEvaluatedStylesheetsWithExpression(self ):        
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam',expression='python:1')
        self.assertEqual(len(self.tool.getEvaluatedStylesheets(self.folder)), 2 )

    def testGetEvaluatedStylesheetsWithFailingExpression(self ):        
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam',expression='python:0')
        self.assertEqual(len(self.tool.getEvaluatedStylesheets(self.folder)), 1 )

    def testGetEvaluatedStylesheetsWithContextualExpression(self ):
        self.folder.invokeFactory('Document', 'eggs')
        self.tool.registerStylesheet('spam',expression='python:"eggs" in object.objectIds()')
        self.assertEqual(len(self.tool.getEvaluatedStylesheets(self.folder)), 1 )

    def testCollapsingStylesheetsLookup(self):        
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam',           media='spam')
        self.tool.registerStylesheet('spam spam',      media='spam')
        evaluated = self.tool.getEvaluatedStylesheets(self.folder)
        self.assertEqual(len(evaluated), 2)
        
    def testRenderingIsInTheRightOrder(self):
        self.tool.registerStylesheet('ham' , media='ham')
        self.tool.registerStylesheet('spam', media='spam')
        evaluated = self.tool.getEvaluatedStylesheets(self.folder)
        evaluatedids = [item['id'] for item in evaluated]
        self.failUnless(evaluatedids[1]=='spam')
        self.failUnless(evaluatedids[0]=='ham')
        
        # can you tell we had good fun writing these tests ? 
        
    def testRenderingStylesheetLinks(self):        
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('ham 2 b merged')
        self.tool.registerStylesheet('spam', media='print')
        self.tool.registerStylesheet('simple.css', inline='1')
        all = getattr(self.portal, 'renderAllTheStylesheets')()
        self.failUnless('background-color' in all)
        self.failUnless('<link' in all)
        self.failUnless('/spam' in all)
        
    def testReenderingConcatenatesInline(self):
        self.tool.registerStylesheet('simple.css', inline='1')
        self.tool.registerStylesheet('simple2.css', inline='1')
        all = getattr(self.portal, 'renderAllTheStylesheets')()
        self.failUnless('background-color' in all)
        self.failUnless('blue' in all)        
        
    def testRenderingWorksInMainTemplate(self):

        renderedpage = getattr(self.portal, 'index_html')()
        self.failIf('background-color' in renderedpage)
        
        self.tool.registerStylesheet('simple.css', inline=1)
        
        renderedpage = getattr(self.portal, 'index_html')()
        self.failUnless('background-color' in renderedpage)


class TestTraversal(CSSRegistryTestCase.CSSRegistryTestCase):

    def afterSetUp(self):
        self.tool = getattr(self.portal, TOOLNAME)
        self.tool.stylesheets = []
        self.tool.registerStylesheet('simple.css')

    def testGetItemTraversal(self):
        self.failUnless(self.tool['simple.css'])
        
    def testGetItemTraversalContent(self):
        self.failUnless('background-color' in str(self.tool['simple.css']))
        
    def testRestrictedTraverseContent(self):
        self.failUnless('background-color' in str(self.portal.restrictedTraverse('portal_css/simple.css')))


    def testRestricedTraverseComposition(self):
        self.tool.registerStylesheet('simple2.css')
        styles = self.tool.getEvaluatedStylesheets(self.portal)
        self.assertEqual(len(styles), 1)
        magicId = styles[0].get('id')
        
        content = str(self.portal.restrictedTraverse('portal_css/%s' % magicId))
        self.failUnless('background-color' in content)
        self.failUnless('blue' in content)

class TestCSSDefaults(CSSRegistryTestCase.CSSRegistryTestCase):

    def afterSetUp(self):
        self.tool = getattr(self.portal, TOOLNAME)
    
    def testDefaultsInstall(self):
        stylesheetids = [item['id'] for item in self.tool.getStylesheets()]
        self.failUnless('plone.css' in stylesheetids)
        self.failUnless('ploneColumns.css' in stylesheetids)
        self.failUnless('ploneCustom.css' in stylesheetids)

    def testTraverseToConcatenatedDefaults(self):
        stylesheets = self.tool.getEvaluatedStylesheets(self.portal)
        for s in stylesheets:
            try:
                magicId = s.get('id')
                self.portal.restrictedTraverse('portal_css/%s' % magicId)
            except KeyError:
                self.fail()

    def testCallingOfConcatenatedStylesheets(self):     
        stylesheets = self.tool.getEvaluatedStylesheets(self.portal)
        for s in stylesheets:
            if 'ploneStyles' in s.get('id'):
                output = self.portal.restrictedTraverse('portal_css/%s' % s.get('id'))
                break
        if not output:
            self.fail()
        o = str(output)[:]
        self.failIf("&lt;dtml-call" in o)            
        self.failIf("&amp;dtml-fontBaseSize;" in o)            
        self.failUnless('** Plone style sheet for CSS2-capable browsers.' in o)            
        
                

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestImplementation))
    suite.addTest(makeSuite(TestTool))
    suite.addTest(makeSuite(TestSkin))
    suite.addTest(makeSuite(testZMIMethods))
    suite.addTest(makeSuite(TestStylesheetRegistration))
    suite.addTest(makeSuite(TestToolSecurity))
    suite.addTest(makeSuite(TestToolExpression))
    suite.addTest(makeSuite(TestStylesheetCooking))
    suite.addTest(makeSuite(TestTraversal))
    suite.addTest(makeSuite(TestCSSDefaults))
    return suite

if __name__ == '__main__':
    framework()
