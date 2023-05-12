#project: p7
#submitter: kmconrad3
#partner: none
#hours: 22

import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import make_column_transformer

class UserPredictor:
    def __init__(self):
        self.train_userrr = None
        self.test_userrr = None
        self.model = None
           
        
    def fit(self, train_user, train_log, train_y):
        self.train_userrr = train_user.merge(train_y)

        train_logg = train_log.groupby(['user_id']).sum("seconds")
        self.train_userrr = self.train_userrr.merge(train_logg, on="user_id", how="outer")
        self.train_userrr = self.train_userrr.fillna(0)

        num_visited = train_log.groupby(["user_id"])["url"].count().rename("num_visited")
        self.train_userrr = self.train_userrr.merge(num_visited, on="user_id", how="outer")
        self.train_userrr = self.train_userrr.fillna(0)

        self.model = Pipeline([
            ("both", make_column_transformer(
                (OneHotEncoder(), ["badge"]), 
                (PolynomialFeatures(degree=3), ['past_purchase_amt','age','seconds', "num_visited"]))),
            ("std", StandardScaler()),
            ("lr", LogisticRegression(max_iter=3000))])
        
        return self.model.fit(self.train_userrr[['past_purchase_amt','age','seconds', 'badge', "num_visited"]], self.train_userrr['y'])

        
    def predict(self, test_user, test_log):        
        test_logg = test_log.groupby(['user_id']).sum("seconds")
        self.test_userrr = test_user.merge(test_logg, on="user_id", how="outer")
        self.test_userrr = self.test_userrr.fillna(0)

        num_visited = test_log.groupby(["user_id"])["url"].count().rename("num_visited")
        self.test_userrr = self.test_userrr.merge(num_visited, on="user_id", how="outer")
        self.test_userrr = self.test_userrr.fillna(0)
        
        return self.model.predict(self.test_userrr[['past_purchase_amt','age','seconds', 'badge', "num_visited"]])
    