#!/usr/bin/env python

# Edit this script to add your team's code. Some functions are *required*, but you can edit most parts of the required functions,
# change or remove non-required functions, and add your own functions.

################################################################################
#
# Optional libraries and functions. You can change or remove them.
#
################################################################################

"""
from helper_code import *
import numpy as np, os, sys
import pandas as pd
import mne
from sklearn.impute import SimpleImputer                  
from sklearn.ensemble import RandomForestClassifier
import joblib

################################################################################
#
# Required functions. Edit these functions to add your code, but do not change the arguments of the functions.
#
################################################################################

# Train your model.
def train_challenge_model(data_folder, model_folder, verbose):
    # Find the Challenge data.
    if verbose >= 1:
        print('Extracting features and labels from the Challenge data...')
        
    patient_ids, data, label, features = load_challenge_data(data_folder)
    num_patients = len(patient_ids)

    if num_patients==0:
        raise FileNotFoundError('No data is provided.')
        
    # Create a folder for the model if it does not already exist.
    os.makedirs(model_folder, exist_ok=True)
    
    
    # Train the models.
    if verbose >= 1:
        print('Training the Challenge models on the Challenge data...')
    
    data = pd.get_dummies(data)
        
    # Define parameters for random forest classifier and regressor.
    n_estimators   = 123  # Number of trees in the forest.
    max_leaf_nodes = 456  # Maximum number of leaf nodes in each tree.
    random_state   = 789  # Random state; set for reproducibility.

    # Impute any missing features; use the mean value by default.
    imputer = SimpleImputer().fit(data)

    # Train the models.
    data_imputed = imputer.transform(data)
    prediction_model = RandomForestClassifier(
        n_estimators=n_estimators, max_leaf_nodes=max_leaf_nodes, random_state=random_state).fit(data_imputed, label.ravel())


    # Save the models.
    save_challenge_model(model_folder, imputer, prediction_model)

    if verbose >= 1:
        print('Done!')
        
# Load your trained models. This function is *required*. You should edit this function to add your code, but do *not* change the
# arguments of this function.
def load_challenge_model(model_folder, verbose):
    print('Loading the model...')
    filename = os.path.join(model_folder, 'model.sav')
    return joblib.load(filename)

def run_challenge_model(model, data_folder, verbose):
    imputer = model['imputer']
    prediction_model = model['prediction_model']

    # Load data.
    patient_ids, data, label, features = load_challenge_data(data_folder)
    
    data = pd.get_dummies(data)
    
    # Impute missing data.
    data_imputed = imputer.transform(data)

    # Apply model to data.
    prediction_binary = prediction_model.predict(data_imputed)[:]
    prediction_probability = prediction_model.predict_proba(data_imputed)[:, 1]

    return patient_ids, prediction_binary, prediction_probability


################################################################################
#
# Optional functions. You can change or remove these functions and/or add new functions.
#
################################################################################

# Save your trained model.
def save_challenge_model(model_folder, imputer, prediction_model):
    d = {'imputer': imputer, 'prediction_model': prediction_model}
    filename = os.path.join(model_folder, 'model.sav')
    joblib.dump(d, filename, protocol=0)
"""
import xgboost as xgb

# Train your model.
def train_challenge_model(data_folder, model_folder, verbose):
    # Find the Challenge data.
    if verbose >= 1:
        print('Extracting features and labels from the Challenge data...')
        
    patient_ids, data, label, features = load_challenge_data(data_folder)
    num_patients = len(patient_ids)

    if num_patients == 0:
        raise FileNotFoundError('No data is provided.')
        
    # Create a folder for the model if it does not already exist.
    os.makedirs(model_folder, exist_ok=True)
    
    # Train the models.
    if verbose >= 1:
        print('Training the Challenge models on the Challenge data...')
    
    data = pd.get_dummies(data)
        
    # Define parameters for XGBoost classifier.
    params = {
        'objective': 'binary:logistic',
        'eval_metric': 'auc',
        'tree_method': 'hist',  # faster tree construction method
        'grow_policy': 'lossguide',  # split at nodes that yield the largest decrease in loss
        'max_depth': 6,
        'eta': 0.1,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'seed': 42,
    }

    # Split the data into training and validation sets.
    train_data, train_label, val_data, val_label = split_data(data, label)

    # Convert data to XGBoost DMatrix format.
    dtrain = xgb.DMatrix(train_data, label=train_label)
    dval = xgb.DMatrix(val_data, label=val_label)

    # Train the model.
    bst = xgb.train(params, dtrain, num_boost_round=1000, evals=[(dtrain, 'train'), (dval, 'val')], verbose_eval=50,
                    early_stopping_rounds=50)

    # Save the model.
    save_challenge_model(model_folder, bst)

    if verbose >= 1:
        print('Done!')

# Load your trained model. This function is *required*. You should edit this function to add your code, but do *not* change the
# arguments of this function.
def load_challenge_model(model_folder, verbose):
    print('Loading the model...')
    filename = os.path.join(model_folder, 'model.bin')
    return xgb.Booster({'nthread': 4})  # initialize empty Booster
    bst.load_model(filename)  # load model from file

def run_challenge_model(model, data_folder, verbose):
    bst = model

    # Load data.
    patient_ids, data, label, features = load_challenge_data(data_folder)
    
    data = pd.get_dummies(data)
    
    # Apply model to data.
    dtest = xgb.DMatrix(data)
    prediction_probability = bst.predict(dtest)

    # Convert probabilities to binary predictions using a threshold of 0.5.
    prediction_binary = (prediction_probability >= 0.5).astype(int)

    return patient_ids, prediction_binary, prediction_probability
