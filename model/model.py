from sklearn.datasets import load_iris
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn2pmml.pipeline import PMMLPipeline
from sklearn2pmml import sklearn2pmml

import pandas as pd
import numpy as np

data = load_iris()
feature_cols = data['feature_names']
df = pd.DataFrame(data=np.c_[data['data'], data['target']],
                  columns=data['feature_names'] + ['target'])

X, y = df[feature_cols], df["target"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.12, random_state=42)

print(X_test.head())
print(y_test.head())

pipeline = PMMLPipeline([
    ("classifier", GradientBoostingClassifier())
])
pipeline.fit(X_train, y_train)

sklearn2pmml(
    pipeline, "/Users/tcfartunc/Dev/workspaces/python/python_model_server/pmmls/GBIris.pmml", with_repr=True)
