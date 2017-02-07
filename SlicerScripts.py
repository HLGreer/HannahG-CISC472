'''
    Scripts for use in the python terminal of slicer.
    Created for CISC 472, Winter 2017
    Hannah Greer
'''

import numpy

def createTransformPoints(randErr, N):
  Scale = 30.0
  Sigma = randErr # radius of random error

  fromNormCoordinates = numpy.random.rand(N, 3) # An array of random numbers
  noise = numpy.random.normal(0.0, Sigma, N*3)

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
    xx = x+noise[i*3]
    yy = y+noise[i*3+1]
    zz = z+noise[i*3+2]
    numFids = RASFids.AddFiducial(xx, yy, zz)
    numPoints = betaPoints.InsertNextPoint(xx, yy, zz)

  return [alphaPoints, betaPoints, referenceToRas]


# Create landmark transform object that computes registration
def computeRegistration(referenceToRas, alphaPoints, betaPoints):
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
  targetPoint = numpy.array((0,0,0,1))
  transformedTarget = alphaToBetaMatrix.MultiplyFloatPoint(targetPoint)
  TRE = numpy.linalg.norm(transformedTarget - targetPoint)
  print "The Target Registration Error is: "
  print TRE
  return TRE

# homework for Feb 7, 2017
def compareTRE_FRE():
  for i in range(10,40, 5):
    [alphaPoints, betaPoints, referenceToRas] = createTransformPoints(2.0, i)
    alphaToBetaMatrix = computeRegistration(referenceToRas, alphaPoints, betaPoints)
    average = avgDistAfterReg(i, alphaPoints, betaPoints, alphaToBetaMatrix)
    TRE = computeTRE(alphaToBetaMatrix)









