import pandas as pd
import numpy as np
import re
from scipy.sparse._csr import csr_matrix

def col_splits(dataframe):
    """
    Splits a housing dataframe into different column types. Returns lists of columns as a dictionary.
    """
    
    #Create lists of columns with different preprocessing steps
    cols = list(dataframe.columns)

    #Columns containing these strings contain area in sqft
    areas = [x for x in cols if re.search('Area|SF|Porch',x)] 

    #Frontage is the only length measurement
    frontage = ['LotFrontage']

    #MiscVal is the only dollar value other than the target 'SalePrice'
    miscval = ['MiscVal']

    #Categoricals relating to sale and location conditions
    conditions = [x for x in cols if re.search('Condition', x)]

    #Columns containing 'Overall' refer to a 10pt inspection
    inspect10pt = [x for x in cols if re.search('Overall', x)] 

    #Columns containing 'Cond', 'Qu', or 'QC' are 5pt inspections, 
    #excluding the sqft, conditions, and 10pt inspections
    inspect5pt = [x for x in cols if re.search('Cond|Qu|QC', x) 
                  if x not in areas+conditions+inspect10pt]

    #Create single group for 5pt and 10pt scale quality
    inspections = inspect10pt + inspect5pt

    #Columns relating to years
    dates = [x for x in cols if re.search('Year|Yr|MoSold',x)]

    #Numeric columns excluding those above, the ID, target SalePrice, and categorical MSSubClass 
    #are counts (rooms, or # of cars in garage)
    counts = dataframe[[x for x in cols if x not in 
             areas+frontage+miscval+conditions+inspections+dates
             +['PID', 'SalePrice', 'MSSubClass']]]\
            .select_dtypes(include=np.number).columns.tolist()

    #All remaining columns are categorical, except ID and target
    categoricals = [x for x in cols if x not in 
                areas+frontage+miscval+conditions+inspections+dates+counts+['PID', 'SalePrice']]
    
    return {'areas': areas,
           'frontage': frontage,
           'miscval': miscval,
           'conditions': conditions,
           'inspect10pt': inspect10pt,
           'inspect5pt': inspect5pt,
           'inspections': inspections,
           'dates': dates,
           'counts': counts,
           'categoricals': categoricals}

def restrict_col_list(col_list,dataframe):
    """
    Restricts a list of column names to the columns in the dataframe.
    """
    return [x for x in dataframe.columns if x in col_list]

def get_clean_ames(data):
    """
    Create cleaned dataframe with appropriate encodings of data and NaNs filled where possible.
    Returns dictionary of cleaned dataframe and column lists.
    
    args:
        data: ames dataframe
    """
    #Import dataset
    housing = data.copy().drop_duplicates().reset_index(drop=True)

    #Separate columns for preprocessing
    col_groups = col_splits(housing)
    areas = col_groups['areas']
    frontage = col_groups['frontage']
    miscval = col_groups['miscval']
    conditions = col_groups['conditions']
    inspect10pt = col_groups['inspect10pt']
    inspect5pt = col_groups['inspect5pt']
    inspections = col_groups['inspections']
    dates = col_groups['dates']
    counts = col_groups['counts']
    categoricals = col_groups['categoricals']

    #Prep & check NaNs
    #Assume NaN in area/length column implies doesn't have this feature, hence would be 0 sqft of that feature
    housing[areas] = housing[areas].fillna(0.)
    housing[frontage] = housing[frontage].fillna(0.)

    #Convert rating Poor = 0, Fair = 1, Average = 2, Good = 3, Excellent = 4, keeping NaNs
    housing[inspect5pt] = housing[inspect5pt].applymap(lambda x: 
                                                       {'Po':0, 'Fa':1, 'TA':2, 'Gd':3, 'Ex':4, np.nan:np.nan}[x])
    
    
    #Few sales of type VWD, change to Oth
    housing['SaleType'] = housing['SaleType'].apply(lambda x: 'Oth' if x == 'VWD' else x)
    
    #All places where miscval is missing should correspond to places where there is no associated Misc Feature
    assert housing[housing[miscval].isna()].loc[:,'MiscFeature'].notnull().sum() == 0
    #In which case, fill miscval with $0
    housing[miscval] = housing[miscval].fillna(0.)

    #Basement baths only missing where there is no basement
    assert housing[housing['BsmtFullBath'].isna()].loc[:,'TotalBsmtSF'].sum() == 0
    assert housing[housing['BsmtHalfBath'].isna()].loc[:,'TotalBsmtSF'].sum() == 0
    #Fill these with 0
    housing['BsmtFullBath'] = housing['BsmtFullBath'].fillna(0)
    housing['BsmtHalfBath'] = housing['BsmtHalfBath'].fillna(0)

    #Number of cars garage can hold only missing when there is no garage
    assert housing[housing['GarageCars'].isna()].GarageArea.sum() == 0
    #Fill these with 0
    housing['GarageCars'] = housing['GarageCars'].fillna(0)

    #Check missing categoricals
    assert housing[housing.MiscFeature.isna()].loc[:,'MiscVal'].sum() == 0 # missing MiscFeature --> 0 for MiscVal
    assert housing[housing.GarageFinish.isna()].loc[:,'GarageArea'].sum() == 0 # missing GarageFinish --> no garage
    assert housing[housing.GarageType.isna()].loc[:,'GarageArea'].sum() == 0 # missing GarageType --> no garage
    assert housing[housing.BsmtFinType1.isna()].loc[:,'TotalBsmtSF'].sum() == 0 # missing BsmtFinType1 --> no basement
    assert housing[housing.BsmtFinType2.isna()].loc[:,'TotalBsmtSF'].sum() == 0 # missing BsmtFinType2 --> no basement
    assert housing[housing.BsmtExposure.isna()].loc[:,'TotalBsmtSF'].sum() == 0 # missing BsmtExposure --> no basement
    assert housing[housing.MasVnrType.isna()].loc[:,'MasVnrArea'].sum() == 0 # missing MasVnrType --> no masonry veneer

    #Fill categorical NaNs with 'none'
    housing[categoricals] = housing[categoricals].fillna('none')
    housing['MasVnrType'] = housing['MasVnrType'].apply(lambda x: 'none' if x=='None' else x)
    
    #Check missing numerics
    
    #BsmtQual and BsmtCond only missing where there is no basement
    assert (housing['BsmtQual'].isna() == housing['BsmtCond'].isna()).all() #missing for same listings
    assert housing[housing['BsmtQual'].isna()].loc[:,'TotalBsmtSF'].sum() == 0 #BsmtQual/Cond should only be missing where there is no basement

    #Fireplace Quality only missing where no fireplaces
    assert housing[housing['FireplaceQu'].isna()].loc[:,'Fireplaces'].sum() == 0

    #Garage Year Built only missing where no garage
    assert (housing['GarageYrBlt'].isna() == (housing['GarageArea'] == 0)).all()

    #Pool Quality only missing where no pool
    assert housing[housing['PoolQC'].isna()].loc[:,'PoolArea'].sum() == 0

    #Garage quality only missing where no garage (except for where dropped)
    assert (housing.GarageCond.isna() == (housing.GarageArea == 0)).all()
    
    #Remove totals
    housing.drop('TotRmsAbvGrd', axis = 1, inplace = True)
    
    #TotalBsmtSF is the sum of basement SFs, can be removed
    assert (housing.filter(regex = 'Bsmt.+SF').sum(axis = 1) == housing['TotalBsmtSF']).all()
    housing.drop('TotalBsmtSF', axis = 1, inplace = True)
    
    #GrLivArea is just sum of 1stFlrSF, 2ndFlrSF, and LowQualFinSF, so can be removed
    assert (housing['1stFlrSF'] + housing['2ndFlrSF'] + housing['LowQualFinSF'] == housing['GrLivArea']).all()
    housing.drop('GrLivArea', axis = 1, inplace=True)
    
    #These don't seem to have strong linear correlation with sale price
    housing.drop(['BsmtCond', 'FireplaceQu', 'GarageQual', 'GarageCond', 'PoolQC'], axis = 1, inplace = True)
    
    #Replace BsmtQual (missing values) with new feature which captures related information
    housing['TotBsmtSF*Qual'] = housing['BsmtQual'].fillna(0) * housing.filter(regex='Bsmt.+SF').sum(axis = 1)
    housing.drop('BsmtQual', axis = 1, inplace = True)
    
    #drop column; somewhat predicted by linear combos of other features
    housing.drop('GarageYrBlt', axis = 1, inplace = True)
    
    f = lambda x: restrict_col_list(x, housing)
    
    return {'areas': f(areas),
           'frontage': f(frontage),
           'miscval': f(miscval),
           'conditions': f(conditions),
           'inspect10pt': f(inspect10pt),
           'inspect5pt': f(inspect5pt),
           'inspections': f(inspections),
           'dates': f(dates),
           'counts': f(counts),
           'categoricals': f(categoricals),
           'housing': housing}

def exterior_type(x):
    if x in ['MetalSd', 'Wd Sdng', 'Wd Shng', 'Wd Shing', 'Stucco', 'WdShing']:
        return 'sd_shng'
    elif x in ['CBlock', 'AsphShn', 'Stone']:
        return 'rock'
    elif x in ['HdBoard', 'Plywood']:
        return 'board'
    elif x in ['ImStucc', 'PreCast']:
        return 'fabricated'
    elif x in ['Brk Cmn', 'BrkFace', 'BrkComm']:
        return 'brick'
    elif x == 'AsbShng':
        return 'asb'
    elif x in ['CemntBd', 'CmentBd']:
        return 'cement'
    elif x == 'VinylSd':
        return 'vinyl'
    
    #List above should be exhaustive
    else:
        return x
    
def basement_type(x):
    if x in ['LwQ', 'BLQ', 'Rec', 'Unf']:
        return 'unfinished'
    if x in ['ALQ', 'GLQ']:
        return 'finished'
    if x in ['none']:
        return 'none'
    
    #should be exhaustive
    else:
        x
    
def get_compressed_ames(data):
    """
    Create cleaned dataframe with appropriate encodings of data and NaNs filled where possible.
    Then, groups categorical values based on the EDA
    Returns dictionary of cleaned dataframe and column lists.
    
    args:
        data: ames dataframe
    """
    data_dict = get_clean_ames(data)
    housing = data_dict['housing']
    areas = data_dict['areas']
    frontage = data_dict['frontage']
    miscval = data_dict['miscval']
    conditions = data_dict['conditions']
    inspect10pt = data_dict['inspect10pt']
    inspect5pt = data_dict['inspect5pt']
    inspections = data_dict['inspections']
    dates = data_dict['dates']
    counts = data_dict['counts']
    other_cats = data_dict['categoricals']
    categoricals = other_cats+conditions+inspections
    
    #Group MSZoning
    housing['zoningGroups'] = housing.MSZoning.apply(lambda x:
                                                'neg_zone' if x in ['I (all)', 'C (all)', 'A (agr)'] else(
                                                'low_R' if x in ['RM', 'RH'] else (
                                                'norm_R' if x in ['RL'] else (
                                                'pos_zone' if x in ['FV'] else
                                                x))))
    housing.drop('MSZoning', axis = 1, inplace = True)
    other_cats.append('zoningGroups')
    
    #Group LotShape
    housing['LotShapeGroups'] = housing.LotShape.apply(lambda x: 'IR' if re.search('IR', x) else x)
    housing.drop('LotShape', axis = 1, inplace = True)
    other_cats.append('LotShapeGroups')
    
    
    #Group HouseStyle
    housing['styleGroups'] = housing.HouseStyle.apply(lambda x:
                                                 'neg_styles' if x in ['1.5Unf', '1.5Fin', 'SFoyer'] else(
                                                 'norm_styles' if x in ['SLvl', '1Story'] else (
                                                 'pos_styles' if x in ['2.5Unf', '2Story','2.5Fin'] else
                                                 x)))
    housing.drop('HouseStyle', axis = 1, inplace = True)
    other_cats.append('styleGroups')
    
    #Group Exterior 1 and 2
    housing['ext1groups'] = housing.Exterior1st.apply(exterior_type)
    housing['ext2groups'] = housing.Exterior2nd.apply(exterior_type)
    housing.drop(['Exterior1st', 'Exterior2nd'], axis = 1, inplace = True)
    other_cats += ['ext1groups', 'ext2groups']
    
    #Testing trevor's grouping
    # housing['exterior2_compressed'] = housing.Exterior2nd.apply(lambda x:
    #                                                            1 if x in ['AsphShn', 'CBlock', 'AsbShng'] else (
    #                                                            2 if x in ['Brk Cmn', 'BrkComm', 'Stucco', 'PreCast'] else (
    #                                                            3 if x in ['Other', 'Wd Shng', 'Wd Sdng', 'MetalSd', 
    #                                                                      'WdShing', 'HdBoard'] else (
    #                                                            4 if x == 'Plywood' else (
    #                                                            5 if x in ['BrkFace', 'VinylSd', 'CmentBd', 'Stone', 'ImStucc'] 
    #                                                            else x)))))
    # other_cats.append('exterior2_compressed')
    
    #Group foundation
    housing['foundationGroups'] = housing.Foundation.apply(lambda x: 'neg_foundation' if x in ['Slab', 'BrkTil', 'CBlock']
                                                                  else ('avg_foundation' if x in ['Stone', 'Wood']
                                                                        else ('pos_foundation' if x in ['PConc']
                                                                              else x)))
    housing.drop('Foundation', axis = 1, inplace = True)
    other_cats.append('foundationGroups')
    
    #Group basement exposure type
    housing['BsmtExpGroups'] = housing.BsmtExposure.apply(lambda x: 'norm' if x in ['No', 'Mn', 'Av'] else x)
    housing.drop('BsmtExposure', axis = 1, inplace = True)
    other_cats.append('BsmtExpGroups')
    
    #Group basement finish types
    housing['Bsmt1typeGroups'] = housing.BsmtFinType1.apply(basement_type)
    housing['Bsmt2typeGroups'] = housing.BsmtFinType2.apply(basement_type)
    housing.drop(['BsmtFinType1', 'BsmtFinType2'], axis = 1, inplace = True)
    other_cats += ['Bsmt1typeGroups', 'Bsmt2typeGroups']
    
    #Group heating types
    housing['HeatingGroups'] = housing.Heating.apply(lambda x:
                                                'gas' if x in ['GasW', 'GasA'] else (
                                                'other' if x in ['Floor', 'Wall', 'Grav', 'OthW'] else
                                                x))
    housing.drop('Heating', axis = 1, inplace = True)
    other_cats.append('HeatingGroups')
    
    #Group electrical types
    housing['electricalGroups'] = housing.Electrical.apply(lambda x:
                                                      'fuse' if re.search('Fuse', x) else (
                                                      'breaker' if x in ['SBrkr'] else
                                                      x))
    housing.drop('Electrical', axis = 1, inplace = True)
    other_cats.append('electricalGroups')
    
    #Functionality groups
    housing['functionalGroups'] = housing.Functional.apply(lambda x: 'mid' if x in ['Min1', 'Maj1', 'Min2', 'Mod'] else x)
    housing.drop('Functional', axis = 1, inplace = True)
    other_cats.append('functionalGroups')
    
    #Group garage types
    housing['GarageTypeGroups'] = housing.GarageType.apply(lambda x:
                                                      'pos_type' if x in ['Attchd', 'BuiltIn'] else (
                                                      'mid_type' if x in ['Detchd', '2Types', 'Basment'] else (
                                                      'low_type' if x in ['CarPort'] else (
                                                      'none' if x == 'none' else x))))
    housing.drop('GarageType', axis = 1, inplace = True)
    other_cats.append('GarageTypeGroups')
    
    #Group fence types
    housing['fenceGroups'] = housing.Fence.apply(lambda x: 
                                             'neg_fence' if x in ['MnWw', 'GdWo', 'MnPrv'] else (
                                             'pos_fence' if x in ['GdPrv'] else (
                                             'none' if x == 'none' else x)))
    housing.drop('Fence', axis = 1, inplace = True)
    other_cats.append('fenceGroups')
    
    #Group sale conditions
    housing['SaleCondGroups'] = housing.SaleCondition.apply(lambda x:
                                                       'neg_cond' if x in ['AdjLand', 'Family', 'Alloca']
                                                       else x)
    housing.drop('SaleCondition', axis = 1, inplace = True)
    conditions.append('SaleCondGroups')
    
    
    #Testing trevor's grouping
    # housing['sale_condition_compressed'] = housing.SaleCondition.apply(lambda x:
    #                                                                   'Normal' if x == 'Normal' else (
    #                                                                   'Other' if x in ['Abnorml', 'Alloca', 'Family'] else (
    #                                                                   'Partial' if x == 'Partial' else x)))
    # conditions.append('sale_condition_compressed')


    
    #Group location conditions
    housing['cond1groups'] = housing.Condition1.apply(lambda x: 'neg_cond' if x in ['Artery', 'RRAe', 'Feedr', 'RRNe'] else (
            'normal' if x in ['RRAn', 'Norm', 'RRNn'] else (
            'pos_cond' if x in ['PosN', 'PosA']
            else x)))

    housing['cond2groups'] = housing.Condition2.apply(lambda x: 'neg_cond' if x in ['Artery', 'RRAe', 'Feedr', 'RRNe'] else (
            'normal' if x in ['RRAn', 'Norm', 'RRNn'] else (
            'pos_cond' if x in ['PosN', 'PosA']
            else x)))
    
    #Testing trevor's grouping
    # housing['condition1_compressed'] = housing.Condition1.apply(lambda x:
    #                                                            0 if x in ['Artery', 'RRNe', 'RRAe',
    #                                                                      'Feedr', 'RRAn', 'RRNn'] else (
    #                                                            1 if x == 'Norm' else (
    #                                                            2 if x in ['PosN', 'PosA'] else x)))
    
    # conditions.append('condition1_compressed')
    

    housing.drop(['Condition1', 'Condition2'], axis = 1, inplace = True)
    conditions += ['cond1groups', 'cond2groups']
    
    #Group heating quality
    housing['HeatingQCGroups'] = housing.HeatingQC.apply(lambda x:
                                                    'neg_QC' if x in range(4) else(
                                                    'pos_QC' if x in range(4,5) else x))
    housing.drop('HeatingQC', axis = 1, inplace = True)
    inspect5pt.append('HeatingQCGroups')
    
    inspections = inspect10pt + inspect5pt
    
    f = lambda x: restrict_col_list(x, housing)
    
    return {'areas': f(areas),
           'frontage': f(frontage),
           'miscval': f(miscval),
           'conditions': f(conditions),
           'inspect10pt': f(inspect10pt),
           'inspect5pt': f(inspect5pt),
           'inspections': f(inspections),
           'dates': f(dates),
           'counts': f(counts),
           'categoricals': f(other_cats),
           'housing': housing}


def transformed_df(skltransformer, df):
    """
    Applies sklearn transformer to dataframe, then returns transformed version as dataframe, naming the columns based on the original feature names.
    
    args:
        skltransformer: an sklearn transformer with a .get_feature_names_out method
        df: a dataframe
    """
    transformed = skltransformer.fit_transform(df)
    if isinstance(transformed, csr_matrix):
        transformed = transformed.todense()
        
    cols = [*map(lambda x: x.split('__')[-1], skltransformer.get_feature_names_out())]
    
    return pd.DataFrame(transformed, columns = cols)
    
    

