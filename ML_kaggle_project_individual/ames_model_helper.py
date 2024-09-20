import pandas as pd
import numpy as np
import re
from io import StringIO

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score

#statsmodels results to pandas converters

def smOLS_results(ols_model):
    '''Returns the OLS Regression Results (first table) for overall regression
    stats as a pandas DataFrame.
    
    ols_model: a fitted statsmodels ols model
    '''
    ols_results_lines = np.array(ols_model.summary().__dict__['tables'][0].as_csv()\
                                 .strip('OLS Regression Results').split('\n')[1:-1])

    nonF = pd.DataFrame(np.array([*map(
        lambda x: x.split(','), 
        ols_results_lines[['Date' not in line for line in ols_results_lines]]
    )]).reshape(-1,2)).applymap(lambda x: x.strip())

    nonF = nonF[nonF != ''].dropna()

    Fstat = pd.DataFrame(np.array(
        re.search('Prob.+', 
              ols_results_lines[['Date'  in line for line in ols_results_lines]][0])\
               .group(0).split(',')).reshape(-1,2))

    results = pd.concat([nonF,Fstat], axis = 0)\
                .rename(mapper = {0:'Result', 1: 'Value'}, axis = 1)
    
    results.reset_index(drop=True, inplace = True)
    results = results.iloc[list(range(0,6)) + [-1] + list(range(6,13))]
    return results

def smOLS_featurestats(ols_model, transformer = None):
    '''Returns the per-coefficient stats for a statsmodels regression as a pandas DataFrame.
    
    Pass a transformer with a .get_feature_names_out() method whose feature names list matches the variables in the statsmodels OLS model to relabel the variable column with the feature names.
    
    ols_model: a fitted statsmodels ols model
    transformer: a fitted transformer whose feature list matches the variables of the OLS model
    '''
    results = pd.read_csv(
    StringIO(ols_model.summary().__dict__['tables'][1].as_csv()))
    
    results.columns = ['variable'] + [*map(lambda x: x.strip(), results.columns)][1:]
    
    if transformer:
        vardict = {x[0]:x[1] for x  in zip(results['variable'], 
                        ['1'] + list(transformer.get_feature_names_out()))}
        results['variable'] = results['variable'].apply(lambda var: vardict[var])
    
    return results


# Linear dependence related feature selection

def estimate_dependence(df, columns = None):
    '''Tests for linear dependence of each column by fitting a linear regression to predict that column from the other columns. Returns a DataFrame with the R^2 score when that feature is the target variable. If a feature has a high R^2, it can be strongly linearly predicted by the other variables. Optionally pass a list of columns to subset the dataframe. 
    
    df: a dataframe
    columns: optional list of column names
    
    Returns: DataFrame of features and R^2 values.
    '''
    if columns:
        df = df[columns]
    lm = LinearRegression()
    cols = list(df.columns)
    name_list = []
    R2_list = []
    for col in cols:
        other_cols = list(set(cols).difference({col}))
        lm.fit(df[other_cols], df[col])
        R2 = lm.score(df[other_cols], df[col])
        name_list.append(col)
        R2_list.append(R2)
    return pd.DataFrame({'feature': name_list, 'R2': R2_list})\
            .sort_values(by = 'R2', ascending = False)

def recursive_dropping(X, y):
    """
    Recursively remove features which are the most linearly dependent on other features if they improve the CV score of a regular linear model, or keep it the same.
    args:
        X features
        y target
    """
    drop_list = []
    lm = LinearRegression()
    current_score = cross_val_score(lm, X.drop(drop_list, axis = 1), y).mean()
    
    while True:
        dependence = estimate_dependence(X.drop(drop_list, axis = 1))
        sequence = dependence.feature.values.tolist()
        for ind, feature in enumerate(sequence):
            lm = LinearRegression()
            new_score = cross_val_score(lm, X.drop(drop_list+[feature], axis = 1), y).mean()
            if new_score >= current_score:
                drop_list += [feature]
                current_score = new_score
                break
            elif ind == len(sequence) - 1:
                return drop_list
            else:
                continue   