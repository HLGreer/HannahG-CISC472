'''
    Scripts for use in the python terminal of slicer.
    Created for CISC 472, 2017
'''

import numpy

# Homework for Jan 24:
referenceToRas = slicer.vtkMRMLLinearTransformNode()
slicer.mrmlScene.AddNode(referenceToRas)
referenceToRas.SetName('ReferenceToRas')

# Homework for Jan 26:

# Scale defines how large cube will be created
# numPerEdge defines how many fiducials to put on each edge of the cube

scale = 30.0
numPerEdge = 3
sigma = 2.0 # radius of random error
N = numPerEdge*numPerEdge

referenceFids = slicer.vtkMRMLMarkupsFiducialNode()
referenceFids.SetName('ReferenceFiducials')
slicer.mrmlScene.AddNode(referenceFids)
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



