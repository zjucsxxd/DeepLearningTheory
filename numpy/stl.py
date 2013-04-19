from pylab import *
from autoencoder import *
from scipy.optimize import fmin_l_bfgs_b
from loadmnist import *

def feedForwardAutoencoder(theta, hiddenSize, visibleSize, data):
  L = hiddenSize * visibleSize
  W1 = reshape(theta[1:L], (hiddenSize, visibleSize), order='F')
  b1 = theta[2*L:2*L + hiddenSize]
  activation = sigmoid(dot(W1, data) + tile(b1, (1, shape(data)[1])))
  return activation

if __name__ == "__main__":
  inputSize = 28 * 28
  numLabels = 5
  hiddenSize = 2
  eta = 3e-3
  beta = 3
  maxIter = 10
  sparsityParam = 0.1
  visibleSize = inputSize

  L = hiddenSize * visibleSize
  mnistData = loadMNISTImages('train-images-idx3-ubyte')
  mnistLabels = loadMNISTLabels('train-labels-idx1-ubyte')

  labeledSet = mnistLabels[logical_and(mnistLabels >= 0, mnistLabels <=4)]
  unlabeledSet = mnistLabels[mnistLabels >= 5]

  numTrain = around(size(labeledSet)/2)
  trainSet = labeledSet[:numTrain]
  testSet = labeledSet[numTrain:]

  unlabeledData = mnistData[:,unlabeledSet]

  trainData = mnistData[:, trainSet]
  trainLabels = transpose(mnistLabels[trainSet])

  testData = mnistData[:, testSet]
  testLabels = transpose(mnistLabels[testSet])

  print '# examples in unlabeled set: %d' % shape(unlabeledData)[1]
  print '# examples in supervised training set: %d' % shape(trainData)[1]
  print '# examples in supervised testing set: %d' % shape(testData)[1]

  #  Randomly initialize the parameters
  theta = initializeParameters(hiddenSize, inputSize)

  print 'About to call lbfgs'
  print 'shape(unlabeledData): ' + str(shape(unlabeledData))
  # Add call to lbfgs...
  optTheta, cost, d = fmin_l_bfgs_b(lambda x: sparseAutoencoderCostVectorized(x,
    visibleSize, hiddenSize, eta, sparsityParam, beta, unlabeledData), theta,
    maxfun = maxIter)

  print 'visualizing weights'
  # Visualize Weights
  W1 = reshape(optTheta[:L], (hiddenSize, inputSize), order='F')
  display_network(transpose(W1))

  print 'extracting features and training softmax'
  # Extract the features
  trainFeatures = feedForwardAutoencoder(opttheta, hiddenSize, inputSize,
      trainData)

  testFeatures = feedForwardAutoencoder(opttheta, hiddenSize, inputSize, testData)

  # Train the softmax classifier
  optTheta = softmaxTrain(hiddenSize, 5, 1e-4, trainFeatures, trainLabels);

  pred = softmaxPredict(softmaxModel, testFeatures);

  ## ----------------------------------------------------

  # Classification Score
  print 'Test Accuracy: %f%%\n' % 100*mean(pred == testLabels)
