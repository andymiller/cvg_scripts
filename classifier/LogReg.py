from scipy.optimize.optimize import fmin_cg, fmin_bfgs, fmin
import numpy as np
from sklearn import datasets

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

class LogReg():
    """ A simple logistic regression model with L2 regularization (zero-mean
    Gaussian priors on parameters). """

    def __init__(self, alpha=.1, synthetic=False):
        # Set L2 regularization strength
        self.alpha = alpha

    def fit(self, x_train, y_train):
        # Set the data.
        self.x_train = x_train
        self.y_train = y_train
        self.n = y_train.shape[0]

        # Initialize parameters to zero, for lack of a better choice.
        self.betas = np.zeros(self.x_train.shape[1])

        # train the classifier
        self.train()

    def negative_lik(self, betas):
        return -1 * self.lik(betas)

    def lik(self, betas):
        """ Likelihood of the data under the current settings of parameters. """
        # l = sum log sigmoid( Y * beta dot X ) - sum alpha/2 * beta^2
        bDotX = np.sum(betas*self.x_train,1)
        l = np.sum(np.log(sigmoid(self.y_train * bDotX)))
        l -= (self.alpha/2.0) * np.sum(self.betas*self.betas)
        return l

    def train(self):
        """ Define the gradient and hand it off to a scipy gradient-based
        optimizer. """
        
        # Define the derivative of the likelihood with respect to beta_k.
        # Need to multiply by -1 because we will be minimizing.
        dB_k = lambda B, k : (k > 0) * self.alpha * B[k] - np.sum([ \
                                     self.y_train[i] * self.x_train[i, k] * \
                                     sigmoid(-self.y_train[i] *\
                                             np.dot(B, self.x_train[i,:])) \
                                     for i in range(self.n)])
        
        # The full gradient is just an array of componentwise derivatives
        dB = lambda B : np.array([dB_k(B, k) \
                                  for k in range(self.x_train.shape[1])])
        
        # Optimize
        self.betas = fmin_bfgs(self.negative_lik, self.betas, fprime=dB)


    def predict_proba(self, x_test):
        """ computes probabilities given features x_test
        """
        p_y = sigmoid( np.sum(self.betas*x_test, 1) )
        return p_y

    def predict(self, x_test):
        p_y = self.predict_proba(x_test)
        y_test = p_y.argmax(1)
        y_test[y_test==0] = -1
        return y_test

    def plot_training_reconstruction(self):
        plot(np.arange(self.n), .5 + .5 * self.y_train, 'bo')
        plot(np.arange(self.n), self.predict_proba(self.x_train), 'rx')
        ylim([-.1, 1.1])

    def plot_test_predictions(self, x_test, y_test):
        plot(np.arange(self.n), .5 + .5 * y_test, 'yo')
        plot(np.arange(self.n), self.predict_proba(x_test), 'rx')
        ylim([-.1, 1.1])


if __name__ == "__main__":
    from pylab import *

    # Create 20 dimensional data set with 25 points -- this will be
    # susceptible to overfitting.
    X, y = datasets.make_blobs(n_samples=100, centers=2, n_features=20)
    y[y==0] = -1
    X_train = X[0:50]
    y_train = y[0:50]
    X_test = X[50:]
    y_test = y[50:]

    # Run for a variety of regularization strengths
    alphas = [0, .001, .01, .1]
    for j, a in enumerate(alphas):
        print "Training with alpha: ", a

        # Create a new learner, but use the same data for each run
        lr = LogReg(alpha=a)
        lr.fit(X_train, y_train)
        
        # Display execution info
        print "Final betas:"
        print lr.betas
        print "Final lik:"
        print lr.lik(lr.betas)
        
        # Plot the results
        subplot(len(alphas), 2, 2*j + 1)
        lr.plot_training_reconstruction()
        ylabel("Alpha=%s" % a)
        if j == 0:
            title("Training set reconstructions")
        
        subplot(len(alphas), 2, 2*j + 2)
        lr.plot_test_predictions(X_test, y_test)
        if j == 0:
            title("Test set predictions")

    show()
