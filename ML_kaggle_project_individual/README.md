# ML_kaggle_project_individual

Individual project based on work done with Trevor Mattos, Lauren Thomlinson, and Natalie Zadrozna.

House prediction model on Ames dataset. Only some of the models from the original project are here, with some models, e.g. ensembles, excluded due to performance.

Key components of the methodology involved feature selection for an interpretable linear model. In particular, feature selection was based on a combination of:
  - Lasso coefficients
  - Statistical significance of coefficients
  - Linear dependence between observation vectors
  - AIC/BIC scores
  - R2, RMSE, and MAE metrics
  
When features were appropriately selected, a standard linear regression model was competetive with other models, including those using the full feature set (namely, XGBoost, Random Forest, Lasso). Additionally, it had other benefits in addition to being interpretable:
  - Standard linear regression and lasso models on the selected feature set were much less overfit than other models
  - Feature selection led to a model with drastically smaller CIs around its coefficients, dropping from an average of over 500% relative standard error per feature in the full model compared to 23% in the reduced model
  - The final model is a compromise between similar reduced models based on the reliability of the coefficients and AIC/BIC scores. This model improved the MAE by $40k on test data compared to the null model. 
  - Having reliable coefficients shows the contribution of each feature to the final appraisal. These can be used to evaluate the benefits of various potential improvements or compare investments.
