import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import math
import numpy

#
# HannahG
#

class HannahG(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "HannahG" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    It performs a simple thresholding on the input volume and optionally captures a screenshot.
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# HannahGWidget
#

class HannahGWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  This section defines the left side bar and what happens with the buttons.
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #

    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input volume selector
    #
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Input Volume: ", self.inputSelector)

    #
    # output volume selector
    #
    self.outputSelector = slicer.qMRMLNodeComboBox()
    self.outputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.outputSelector.selectNodeUponCreation = True
    self.outputSelector.addEnabled = True
    self.outputSelector.removeEnabled = True
    self.outputSelector.noneEnabled = True
    self.outputSelector.showHidden = False
    self.outputSelector.showChildNodeTypes = False
    self.outputSelector.setMRMLScene( slicer.mrmlScene )
    self.outputSelector.setToolTip( "Pick the output to the algorithm." )
    parametersFormLayout.addRow("Output Volume: ", self.outputSelector)

    #
    # threshold value
    #
    '''
    self.imageThresholdSliderWidget = ctk.ctkSliderWidget()
    self.imageThresholdSliderWidget.singleStep = 0.1
    self.imageThresholdSliderWidget.minimum = -100
    self.imageThresholdSliderWidget.maximum = 100
    self.imageThresholdSliderWidget.value = 0.5
    self.imageThresholdSliderWidget.setToolTip("Set threshold value for computing the output image. Voxels that have intensities lower than this value will set to zero.")
    parametersFormLayout.addRow("Image threshold", self.imageThresholdSliderWidget)

    #
    # check box to trigger taking screen shots for later use in tutorials
    #
    self.enableScreenshotsFlagCheckBox = qt.QCheckBox()
    self.enableScreenshotsFlagCheckBox.checked = 0
    self.enableScreenshotsFlagCheckBox.setToolTip("If checked, take screen shots for tutorials. Use Save Data to write them to disk.")
    parametersFormLayout.addRow("Enable Screenshots", self.enableScreenshotsFlagCheckBox)
    '''
    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    '''
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    '''
    self.emSelector = slicer.qMRMLNodeComboBox()
    self.emSelector.nodeTypes = ['vtkMRMLLinearTransformNode']
    self.emSelector.setMRMLScene(slicer.mrmlScene)
    parametersFormLayout.addRow("EM tool tip transform: ", self.emSelector)

    self.opticalSelector = slicer.qMRMLNodeComboBox()
    self.opticalSelector.nodeTypes = ['vtkMRMLLinearTransformNode']
    self.opticalSelector.setMRMLScene(slicer.mrmlScene)
    parametersFormLayout.addRow("Optical tool tip transform: ", self.opticalSelector)
    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode()

  def onApplyButton(self):
    emTipTransform = self.emSelector.currentNode()
    if emTipTransform == None:
      return
    opTipTransform = self.opticalSelector.currentNode()
    if opTipTransform == None:
      return

    emTipTransform.AddObserver(slicer.vtkMRMLTransformNode.TransformModifiedEvent, self.onTransformModified) # This should update the value anytime it changes.
    opTipTransform.AddObserver(slicer.vtkMRMLTransformNode.TransformModifiedEvent, self.onTransformModified)

  def onTransformModified(self):
    emTipTransform = self.emSelector.currentNode()
    if emTipTransform == None:
      return
    opTipTransform = self.opticalSelector.currentNode()
    if opTipTransform == None:
      return

    emTip_EmTip = [0, 0, 0, 1] # Origin in the center of each separate coordinate system
    opTip_OpTip = [0, 0, 0, 1]

    emTipToRasMatrix = vtk.vtkMatrix4x4() # Create a 4x4 Identity Matrix
    emTipTransform.GetMatrixTransformToWorld(emTipToRasMatrix) # RAS is sometimes also called RAS in Slicer
    emTip_Ras = numpy.array(emTipToRasMatrix.MultiplyFloatPoint(emTip_EmTip)) # Transformed point

    opTipToRasMatrix = vtk.vtkMatrix4x4()
    opTipTransform.GetMatrixTransformToWorld(opTipToRasMatrix)
    opTip_Ras = numpy.array(opTipToRasMatrix.MultiplyFloatPoint(opTip_OpTip)) # Transformed point


    distance = numpy.linalg.norm(emTip_Ras - opTip_Ras)
    print str(distance)
    return distance


    '''
    logic = HannahGLogic()
    enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    imageThreshold = self.imageThresholdSliderWidget.value
    logic.run(self.inputSelector.currentNode(), self.outputSelector.currentNode(), imageThreshold, enableScreenshotsFlag)
    '''

#
# HannahGLogic
#

class HannahGLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def hasImageData(self,volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() is None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def isValidInputOutputData(self, inputVolumeNode, outputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode:
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    if not outputVolumeNode:
      logging.debug('isValidInputOutputData failed: no output volume node defined')
      return False
    if inputVolumeNode.GetID()==outputVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
      return False
    return True

  def takeScreenshot(self,name,description,type=-1):
    # show the message even if not taking a screen shot
    slicer.util.delayDisplay('Take screenshot: '+description+'.\nResult is available in the Annotations module.', 3000)

    lm = slicer.app.layoutManager()
    # switch on the type to get the requested window
    widget = 0
    if type == slicer.qMRMLScreenShotDialog.FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog.ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog.Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog.Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog.Green:
      # green slice window
      widget = lm.sliceWidget("Green")
    else:
      # default to using the full window
      widget = slicer.util.mainWindow()
      # reset the type so that the node is set correctly
      type = slicer.qMRMLScreenShotDialog.FullLayout

    # grab and convert to vtk image data
    qpixMap = qt.QPixmap().grabWidget(widget)
    qimage = qpixMap.toImage()
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, 1, imageData)

  def run(self, inputVolume, outputVolume, imageThreshold, enableScreenshots=0):
    """
    Run the actual algorithm
    """

    if not self.isValidInputOutputData(inputVolume, outputVolume):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputVolume.GetID(), 'ThresholdValue' : imageThreshold, 'ThresholdType' : 'Above'}
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)

    # Capture screenshot
    if enableScreenshots:
      self.takeScreenshot('HannahGTest-Start','MyScreenshot',-1)

    logging.info('Processing completed')

    return True

  import numpy

  def createTransformPoints(randErr, N):
    Scale = 30.0
    Sigma = randErr  # radius of random error

    fromNormCoordinates = numpy.random.rand(N, 3)  # An array of random numbers
    noise = numpy.random.normal(0.0, Sigma, N * 3)

    # Homework for Jan 24:
    referenceToRas = slicer.vtkMRMLLinearTransformNode()
    slicer.mrmlScene.AddNode(referenceToRas)
    referenceToRas.SetName('ReferenceToRas')

    referenceFids = slicer.vtkMRMLMarkupsFiducialNode()
    referenceFids.SetName('ReferenceFiducials')
    slicer.mrmlScene.AddNode(referenceFids)
    referenceFids.GetDisplayNode().SetSelectedColor(0, 0, 1)
    RASFids = slicer.vtkMRMLMarkupsFiducialNode()
    RASFids.SetName('RASFiducials')
    slicer.mrmlScene.AddNode(RASFids)
    RASFids.GetDisplayNode().SetSelectedColor(1, 1, 0)

    alphaPoints = vtk.vtkPoints()
    betaPoints = vtk.vtkPoints()
    for i in range(N):
      x = (fromNormCoordinates[i, 0] - 0.5) * Scale
      y = (fromNormCoordinates[i, 1] - 0.5) * Scale
      z = (fromNormCoordinates[i, 2] - 0.5) * Scale
      numFids = referenceFids.AddFiducial(x, y, z)
      numPoints = alphaPoints.InsertNextPoint(x, y, z)
      xx = x + noise[i * 3]
      yy = y + noise[i * 3 + 1]
      zz = z + noise[i * 3 + 2]
      numFids = RASFids.AddFiducial(xx, yy, zz)
      numPoints = betaPoints.InsertNextPoint(xx, yy, zz)

    return [alphaPoints, betaPoints, referenceToRas]

  # Create landmark transform object that computes registration
  def computeRegistration(referenceToRas, alphaPoints, betaPoints):
    landmarkTransform = vtk.vtkLandmarkTransform()
    landmarkTransform.SetSourceLandmarks(alphaPoints)
    landmarkTransform.SetTargetLandmarks(betaPoints)
    landmarkTransform.SetModeToRigidBody()
    landmarkTransform.Update()

    alphaToBetaMatrix = vtk.vtkMatrix4x4()
    landmarkTransform.GetMatrix(alphaToBetaMatrix)

    det = alphaToBetaMatrix.Determinant()
    if det < 1e-8:
      print 'Unstable registration. Check input for collinear points.'

    referenceToRas.SetMatrixTransformToParent(alphaToBetaMatrix)
    return alphaToBetaMatrix

  # Compute average point distance after registration

  def avgDistAfterReg(N, alphaPoints, betaPoints, alphaToBetaMatrix):
    average = 0.0
    numbersSoFar = 0
    for i in range(N):
      numbersSoFar = numbersSoFar + 1
      a = alphaPoints.GetPoint(i)
      pointA_Alpha = numpy.array(a)
      pointA_Alpha = numpy.append(pointA_Alpha, 1)
      pointA_Beta = alphaToBetaMatrix.MultiplyFloatPoint(pointA_Alpha)
      b = betaPoints.GetPoint(i)
      pointB_Beta = numpy.array(b)
      pointB_Beta = numpy.append(pointB_Beta, 1)
      distance = numpy.linalg.norm(pointA_Beta - pointB_Beta)
      average = average + (distance - average) / numbersSoFar

    print "Average distance after registration: " + str(average)
    return average


    # For Feb 2nd:

    # Compute Target Registration Error:
    # Target registration error (TRE), which is the distance, after registration,
    # between a pair of corresponding points which are not used in registration.
    # (From http://www.cse.yorku.ca/~burton/publications/A%20theoretical%20comparison%20of%20different%20target%20registration%20error%20estimators.pdf)

    # Transform the point (0,0,0) with the transform and return the distance between the original and the transformed
    # point as the TRE

  def computeTRE(alphaToBetaMatrix):
    targetPoint = numpy.array((0, 0, 0, 1))
    transformedTarget = alphaToBetaMatrix.MultiplyFloatPoint(targetPoint)
    TRE = numpy.linalg.norm(transformedTarget - targetPoint)
    print "The Target Registration Error is: "
    print TRE
    return TRE

  # homework for Feb 7, 2017
  def compareTRE_FRE():
    averages = []
    TREs = []
    numPoints = range(10, 45, 5)
    for i in range(10, 45, 5):
      # This is 7 iterations
      print "Number of points used: " + str(i)
      [alphaPoints, betaPoints, referenceToRas] = createTransformPoints(2.0, i)
      alphaToBetaMatrix = computeRegistration(referenceToRas, alphaPoints, betaPoints)
      average = avgDistAfterReg(i, alphaPoints, betaPoints, alphaToBetaMatrix)
      averages.append(average)
      TRE = computeTRE(alphaToBetaMatrix)
      TREs.append(TRE)
    lns = slicer.mrmlScene.GetNodesByClass('vtkMRMLLayoutNode')
    lns.InitTraversal()
    ln = lns.GetNextItemAsObject()
    ln.SetViewArrangement(24)
    # Get the Chart View Node
    cvns = slicer.mrmlScene.GetNodesByClass('vtkMRMLChartViewNode')
    cvns.InitTraversal()
    cvn = cvns.GetNextItemAsObject()
    # Create an Array Node and add some data
    TRE_dn = slicer.mrmlScene.AddNode(slicer.vtkMRMLDoubleArrayNode())
    arrayNode = TRE_dn.GetArray()
    arrayNode.SetNumberOfTuples(7)
    FRE_dn = slicer.mrmlScene.AddNode(slicer.vtkMRMLDoubleArrayNode())
    arrayNode2 = FRE_dn.GetArray()
    arrayNode2.SetNumberOfTuples(7)
    for i in range(len(numPoints)):
      arrayNode.SetComponent(i, 0, numPoints[i])
      arrayNode.SetComponent(i, 1, TREs[i])
      arrayNode.SetComponent(i, 2, 0)
      arrayNode2.SetComponent(i, 0, numPoints[i])
      arrayNode2.SetComponent(i, 1, averages[i])
      arrayNode2.SetComponent(i, 2, 0)
    # Create a Chart Node.
    cn = slicer.mrmlScene.AddNode(slicer.vtkMRMLChartNode())
    # Add the Array Nodes to the Chart. The first argument is a string used for the legend and to refer to the Array when setting properties.
    cn.AddArray('TRE', TRE_dn.GetID())
    cn.AddArray('FRE', FRE_dn.GetID())
    # Set a few properties on the Chart. The first argument is a string identifying which Array to assign the property.
    # 'default' is used to assign a property to the Chart itself (as opposed to an Array Node).
    cn.SetProperty('default', 'title', 'TRE and FRE as a function of the number of points')
    cn.SetProperty('default', 'xAxisLabel', 'Number of points')
    cn.SetProperty('default', 'yAxisLabel', 'Unit Value')
    # Tell the Chart View which Chart to display
    cvn.SetChartNodeID(cn.GetID())


if __name__ == '__main__':
  class HannahGTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
      """ Do whatever is needed to reset the state - typically a scene clear will be enough.
      """
      slicer.mrmlScene.Clear(0)

    def runTest(self):
      """Run as few or as many tests as needed here.
      """
      self.setUp()
      self.test_HannahG1()

    def test_HannahG1(self):
      #compareTRE_FRE()
      # do I need anything here still?
      # All the work is done in the widget class at the moment.
      # run the module:
      #testDistance = getattr(HannahGWidget, onTransformModified)
      pass



