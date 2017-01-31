'''
    Scripts for use in the python terminal of slicer.
    Created for CISC 472, 2017
'''

import numpy

Scale = 30.0
numPerEdge = 3
Sigma = 2.0 # radius of random error
N = 10

fromNormCoordinates = numpy.random.rand(N, 3) # An array of random numbers
noise = numpy.random.normal(0.0, Sigma, N*3)

# Homework for Jan 24:
referenceToRas = slicer.vtkMRMLLinearTransformNode()
slicer.mrmlScene.AddNode(referenceToRas)
referenceToRas.SetName('ReferenceToRas')


referenceFids = slicer.vtkMRMLMarkupsFiducialNode()
referenceFids.SetName('ReferenceFiducials')
slicer.mrmlScene.AddNode(referenceFids)
RASFids = slicer.vtkMRMLMarkupsFiducialNode()
RASFids.SetName('RASFiducials')
slicer.mrmlScene.AddNode(RASFids)

alphaPoints = vtk.vtkPoints()
betaPoints = vtk.vtkPoints()

for i in range(N):
  x = (fromNormCoordinates[i, 0] - 0.5) * Scale
  y = (fromNormCoordinates[i, 1] - 0.5) * Scale
  z = (fromNormCoordinates[i, 2] - 0.5) * Scale
  numFids = referenceFids.AddFiducial(x, y, z)
  numPoints = alphaPoints.InsertNextPoint(x, y, z)
  xx = x+noise[i*3]
  yy = y+noise[i*3+1]
  zz = z+noise[i*3+2]
  numFids = RASFids.AddFiducial(xx, yy, zz)
  numPoints = betaPoints.InsertNextPoint(xx, yy, zz)

# Create landmark transform object that computes registration

landmarkTransform = vtk.vtkLandmarkTransform()
landmarkTransform.SetSourceLandmarks( alphaPoints )
landmarkTransform.SetTargetLandmarks( betaPoints )
landmarkTransform.SetModeToRigidBody()
landmarkTransform.Update()

alphaToBetaMatrix = vtk.vtkMatrix4x4()
landmarkTransform.GetMatrix( alphaToBetaMatrix )

det = alphaToBetaMatrix.Determinant()
if det < 1e-8:
  print 'Unstable registration. Check input for collinear points.'

referenceToRas.SetMatrixTransformToParent(alphaToBetaMatrix)

# Compute average point distance after registration

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


createModelsLogic = slicer.modules.createmodels.logic()

refModelNode = createModelsLogic.CreateCoordinate(20, 2)
refModelNode.SetName('ReferenceModel')
refModelNode.GetDisplayNode().SetColor(1,0,0)

RASModelNode = createModelsLogic.CreateCoordinate(20, 2)
RASModelNode.SetName('RASModel')
RASModelNode.GetDisplayNode().SetColor(0, 0, 1)

RefToRasTransform = referenceToRas.GetTransformToParent()
















'''
z = 0
for x in range(numPerEdge):
    for y in range(numPerEdge):
        cx = (x-float(numPerEdge-1)/2.0)*scale
        cy = (y-float(numPerEdge-1)/2.0)*scale
        cz = (z-float(numPerEdge-1)/2.0)*scale
        referenceFids.AddFiducial(cx, cy, cz)

referenceFids.GetDisplayNode().SetSelectedColor(0,0,1)

RASFids = slicer.vtkMRMLMarkupsFiducialNode()
RASFids.SetName('RASFiducials')
slicer.mrmlScene.AddNode(RASFids)
z = 0
for x in range(numPerEdge):
    for y in range(numPerEdge):
        cx = (x-float(numPerEdge-1)/2.0)*scale + sigma * numpy.random.random()
        cy = (y-float(numPerEdge-1)/2.0)*scale + sigma * numpy.random.random()
        cz = (z-float(numPerEdge-1)/2.0)*scale
        RASFids.AddFiducial(cx, cy, cz)

RASFids.GetDisplayNode().SetSelectedColor(1,0,0)


createModelsLogic = slicer.modules.createmodels.logic()

refModelNode = createModelsLogic.CreateCoordinate(20, 2)
refModelNode.SetName('ReferenceModel')
refModelNode.GetDisplayNode().SetColor(1,0,0)

RASModelNode = createModelsLogic.CreateCoordinate(20, 2)
RASModelNode.SetName('RASModel')
RASModelNode.GetDisplayNode().SetColor(0, 0, 1)

RefToRasTransform = referenceToRas.GetTransformToParent()

# For Jan 31st:

landmarkTransform = vtk.vtkLandmarkTransform()
landmarkTransform.SetSourceLandmarks(referenceFids)
landmarkTransform.SetTargetLandmarks( RASFids )
landmarkTransform.SetModeToRigidBody()
landmarkTransform.Update()

refToRASMatrix = vtk.vtkMatrix4x4()
landmarkTransform.GetMatrix( refToRASMatrix )

det = refToRASMatrix.Determinant()
if det < 1e-8:
  print 'Unstable registration. Check input for collinear points.'

referenceToRas.SetMatrixTransformToParent(refToRASMatrix)

# Compute average point distance after registration

average = 0.0
numbersSoFar = 0

for i in range(N):
  numbersSoFar = numbersSoFar + 1
  a = referenceFids.GetPoint(i)
  pointA_ref = numpy.array(a)
  pointA_ref = numpy.append(pointA_ref, 1)
  pointA_Beta = refToRASMatrix.MultiplyFloatPoint(pointA_ref)
  b = RASFids.GetPoint(i)
  pointB_RAS = numpy.array(b)
  pointB_RAS = numpy.append(pointB_RAS, 1)
  distance = numpy.linalg.norm(pointA_ref - pointB_RAS)
  average = average + (distance - average) / numbersSoFar


print "The average distance is " + average

'''

