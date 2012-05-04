import numpy as np
import pylab as pl
from LogReg import LogReg
from sklearn import datasets

class MultiLogReg():
    """ Multi class logistic regression that trains independent, binary 
        classifiers for each class 
    """
    def __init__(self):
        pass

    def fit(self, x_train, y_train):
        """ Assumes classes are encoded starting at 0 """
        # Set the data.
        self.n = y_train.shape[0]
        self.classes = set(y_train)

        #train each classifier
        self.classifiers = []
        for c in self.classes:
          #create two class training set
          y_c = np.copy(y_train)
          y_c[y_c!=c] = -1
          y_c[y_c==c] = 1
          #train model
          model = LogReg()
          model.fit(x_train, y_c)
          self.classifiers.append(model)

    def predict_proba(self, x_test):
        """ computes probabilities given features x_test
        """
        nTest = x_test.shape[0]
        p_y = np.zeros( (nTest, len(self.classes)+1) )
        for idx in range(len(self.classes)):
          model = self.classifiers[idx]
          positiveProb = np.array(model.predict_proba(x_test))
          p_y[:,idx] = positiveProb[:]
        
        #be sure to calculate the null category
        p_y[:,-1] = np.mean(1.0-p_y[:,0:-1],1)
        return p_y

    def predict(self, x_test):
        probas = self.predict_proba(x_test)
        return probas.argmax(1)


# Test on synthetic data
if __name__ == "__main__":
    from pylab import *

    # Create 20 dimensional data set with 25 points -- this will be
    # susceptible to overfitting.
    X, y = datasets.make_blobs()

    #train svm
    clf = MultiLogReg()
    clf.fit(X,y)
    
    # Plot the decision boundary. For that, we will asign a color to each
    # point in the mesh [x_min, m_max]x[y_min, y_max].
    h = .05
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])

    # Put the result into a color plot
    Z = Z.reshape(xx.shape)
    pl.set_cmap(pl.cm.Paired)
    pl.pcolormesh(xx, yy, Z)

    # Plot also the training points
    pl.scatter(X[:, 0], X[:, 1], c=y)
    pl.title('Multi Logistic Regression')
    pl.axis('tight')
    pl.show()
