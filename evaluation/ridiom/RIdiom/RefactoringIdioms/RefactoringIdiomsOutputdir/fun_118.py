def xgboost(
    features, target, test_features
):
    xgb = XGBRegressor(
        verbosity=0, random_state=42, tree_method="exact", base_score=0.5
    )
    xgb.fit(features, target)
    predictions = xgb.predict(test_features)
    predictions = predictions.reshape(len(predictions), 1)
    return predictions
