Material Classification Module

Training and testing data comes in flat files.  These flatfiles are created using the executable in boxm2/class.  

1) Train a model on some data
example:
% python train.py -d data/train_small.txt -m isvm_lda -s isvm_lda.pkl

        args: -p (pixels): all, EO, or IR
              -m (modeltype): isvm_lda, isvm_pca, isvm, ilogreg, ilogreg_lda (different classifiers and 
              -s (save): model name - can be anything
              -c (complexity): specify how many dimensions the data should be in (2, 3, 4 -> number of features)

2) Test model for classification statistics
% python test.py -m model.pkl -d data/test_small.txt 

        args: -v (visualize): for two dimensional models, visualize classification in XY plane

3) Visualize classified images
% python classify_image.py model.pkl EOimg.png IRimg.png

        args: model, eo img (or eo img directory) and ir img (or ir img directory)

4) Compare rocs for multiple models
% python rocs.py data/test_small.txt model1.pkl model2.pkl model3.pkl ...

        args: testing data in flat file


