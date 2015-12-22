import pandas as pd
import xgboost as xgb

#sample script for doing simple and multiple linear regression with xgboost

def train_and_predict(X_train,Y_train,df_test):
    T_train_xgb = xgb.DMatrix(X_train, Y_train)
    params = {"objective": "reg:linear"}
    gbm = xgb.train(dtrain=T_train_xgb,params=params)
    Y_pred = gbm.predict(xgb.DMatrix(df_test))
    print Y_pred

def simple_linear_regression():
    #single predictor variable and single response variable
    df = pd.DataFrame({'x':[1,2,3]})
    df['y'] = df['x']*10
    df_test = pd.DataFrame({'x':[4,5]})
    X_train = df[['x']]#this is the syntax for getting lables + data whereas df['x'] will simply get you the data sans labels
    Y_train = df['y']
    train_and_predict(X_train,Y_train,df_test)


def multiple_linear_regression():
    #multiple predictor variables and single response variable
    df = pd.DataFrame({'x':[1,2,3,9,10,100]})
    df['x1'] = df['x']
    df['y'] = df['x']+df['x1']
    df_test = pd.DataFrame({'x':[4,5]})
    df_test['x1'] = df['x']
    X_train = df[['x','x1']]
    Y_train = df['y']
    train_and_predict(X_train,Y_train,df_test)

def multivariate_linear_regression():
    #when you have multiple response variables. I don't know how to do it with xgboost
    print "how to do it?"

simple_linear_regression()
multiple_linear_regression()
