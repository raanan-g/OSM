# Data wrangling and visualization
import pandas as pd
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import seaborn as sns

# For machine learning:
# To split the dataset into train and test datasets
from sklearn.model_selection import train_test_split
# Preprocessing
from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder
# For feature selection
from sklearn.decomposition import PCA
# Classifiers
from sklearn.naive_bayes import GaussianNB
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier, export_graphviz

# Classifier evaluation
from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn import metrics
from sklearn.metrics import log_loss


def standardize(df, droplist):
    """
    Deduplicates, standardizes and removes null values from a dataset
    
    Parameters:
    ---------------------
    df : Pandas DataFrame
        Dataframe of numeric values
    droplist : list
        Column names for non-numeric data and target class
        
    Returns:
    df : Pandas DataFrame
        DataFrame of standardized, preprocessed data
    """
    names = df.drop(columns=droplist).columns
    
    # Create the Scaler object and fit data
    scaler = preprocessing.StandardScaler()
    scaled_df = scaler.fit_transform(df.drop(columns=droplist))
    
    scaled_df = pd.DataFrame(scaled_df, columns=names)
    
    df = pd.concat([df[droplist],scaled_df], axis=1)
    
    return df

 
def label_encode(df, columns):
    """
    Encode dataframe columns
    
    Parameters:
    df : DataFrame
        training/test data
    columns : list
        list of column names
    """
    for col in columns:
        le = LabelEncoder()
        col_values_unique = list(df[col].unique())
        le_fitted = le.fit(col_values_unique)
 
        col_values = list(df[col].values)
        #le.classes_
        col_values_transformed = le.transform(col_values)
        df[col] = col_values_transformed

        
def classify(predictors, response, classifier = 'svm', kern='rbf', neighbors=3, kfolds=0, report=False, rscores=True):
    """
    Model training, testing, cross-validation and evaluation
    
    Parameters:
    ------------------------
    predictors : DataFrame
        Pandas dataframe of features
    response : Series / list
        Pandas Series or list of target class
    classifier : String
        Classifier type (Naive Bayes, Support Vector Machine, K-Nearest Neighbors, Random Forest, Decision Tree
    kern : Strin
        Specifies type of kernel for SVM models
    neighbors: int
        Specifies number of neighbors for KNN or decision trees for Random Forest
    kfolds : int
        Specifies value of k for k-fold cross-validation
    report : Bool
        Indicates whether to print classification report, confusion matrix, feature importances, etc.
        
    Returns:
    -----------------------
    cl : Model
        Trained ML model
    """
    
    # split X and y into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(predictors, response, test_size=0.20, random_state=1)

    
    if classifier == 'nb':
        cl = GaussianNB() # instantiate model
        msg = 'Naive Bayes'
    elif classifier == 'svm':
        cl = svm.SVC(kernel=kern) # instantiate model
        msg = 'SVM with ' + kern + ' kernel'
    elif classifier == 'knn':
        cl = KNeighborsClassifier(n_neighbors=neighbors)
        msg = 'KNN with k=' + str(neighbors)
    elif classifier == 'rf':
        # Instantiate model with  decision trees
        # Note that the number of decision trees is denoted
        # using the neighbors parameter, which is set to 3 by default
        cl = RandomForestClassifier(n_estimators = 1000, random_state = 42)
        msg = 'Random Forest with ' + str(neighbors) + ' decision trees'
        
    elif classifier == 'dtree':
        cl = DecisionTreeClassifier(min_samples_split=20, random_state=99)
        msg = 'Decision tree'
        
    model = cl.fit(X_train, y_train)
    y_pred_class = model.predict(X_test)
    #y_pred_class = np.array(y_pred_class, dtype=np.int)
    y_probs = model.predict_proba(X_test)  # removed .round() from y_pred_class
    print(msg + ' model accuracy score: ', metrics.accuracy_score(y_test, y_pred_class))
    
    if kfolds > 0:
        # Perform k-fold cross validation
        scores = cross_val_score(model, predictors, response, cv=kfolds, scoring='accuracy')
        cv_score = scores.mean()
        print('Cross-validated score:', cv_score)
        print("Logarithmic Loss:", log_loss(y_test, y_probs, eps=1e-15))
        # Plot ROC Curve and report AUC Statistic
        auc = metrics.roc_auc_score(y_test, y_pred_class)
        print("AUC score: ", auc)
        fpr, tpr, thresholds = metrics.roc_curve(y_test, y_pred_class)
        roc_auc = metrics.auc(fpr, tpr)
        
        # Compute ROC curve and ROC area for each class
        #fpr = dict()
        #tpr = dict()
        #roc_auc = dict()
        #for i in range(n_classes):
        #    fpr[i], tpr[i], _ = roc_curve(y_test[:, i], y_score[:, i])
        #    roc_auc[i] = auc(fpr[i], tpr[i])
        
        plt.figure()
        plt.plot(fpr, tpr, color='darkorange', lw=1, label='ROC curve (area = %0.2f)' % roc_auc)
        plt.plot([0, 1], [0, 1], color='navy', lw=1, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic')
        plt.legend(loc="lower right")
        plt.show()
        
    if report == True:
        try:
            print('Confusion matrix')
            print(metrics.confusion_matrix(y_test, y_pred_class)) # confusion matrix
            print('Classification report')
            print(metrics.classification_report(y_test, y_pred_class))
            
        except:
            print("Metric Error")
        if classifier == 'rf':
            feature_imp = pd.Series(cl.feature_importances_,index=list(predictors)).sort_values(ascending=False)
            # Creating a bar plot
            sns.barplot(x=feature_imp, y=feature_imp.index)
            # Add labels to your graph
            plt.xlabel('Feature Importance Score')
            plt.ylabel('Features')
            plt.title("OSM Geographic Feature Importance")
            plt.figure(figsize=(18,12))
            plt.show()
    
    print('______________________________')
    
    if rscores == True:
        return cl, cv_score, auc
    else:
        return cl


def diagnose(model, X, y):
    """
    Create a detailed dataframe to analyze predictive accuracy of a classification model
    
    Parameters:
    ---------------------------
    model : sklearn classification model
        Trained model (i.e., Random Forest, SVM)
    X : DataFrame
        Pandas DataFrame of features
    y : DataFrame / Series
        Pandas DataFrame of target class labels
        
    Returns:
    ---------------------------
    diagnostic : DataFrame
        Pandas DataFrame with predictions, predicted probabilities for each target class
    """
    preds = model.predict(X)

    probs = model.predict_proba(X)
    prob0 = []
    prob1 = []
    for i in range(0,len(probs)):
        p = probs[i]
        prob0.append(p[0])
        prob1.append(p[1])
        
    diagnostic = pd.DataFrame({'Shipping':y,'Prediction':preds,'p(0)':prob0,'p(1)':prob1})

    # Generate correct/incorrect column
    cr = []
    for i in diagnostic.index:
        if diagnostic['Shipping'][i] == diagnostic['Prediction'][i]:
            cr.append("Correct")
        else:
            cr.append("Incorrect")
    diagnostic['Classification Result'] = cr
    
    
    return diagnostic
    

def implement(model, df, droplist):
    """
    Use a trained model to generate predictions for a dataset of features
    
    Parameters:
    ---------------------------
    model : sklearn classification model
        Trained model (i.e., Random Forest, SVM)
    df : DataFrame
        Pandas DataFrame of features
    droplist : list
        Names of columns that are not features for the model
        
    Returns:
    ---------------------------
    df : DataFrame
        Pandas DataFrame with predictions, predicted probabilities for each target class
    
    """
    # Implement best model (example: random forest)
    X_i = df.drop(columns=droplist)

    preds = model.predict(X_i)
    probs = model.predict_proba(X_i)
    prob0 = []
    prob1 = []
    for i in range(0,len(probs)):
        p = probs[i]
        prob0.append(p[0])
        prob1.append(p[1])
        
    df['Prediction'] = preds # create column with predictions
    df['p(0)'] = prob0    # create column with probability of 'shipping'
    df['p(1)'] = prob1    # create column with probability of 'no shipping'

    return df

    
