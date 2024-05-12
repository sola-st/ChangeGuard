def main():
    california = fetch_california_housing()
    data, target = data_handling(california)
    x_train, x_test, y_train, y_test = train_test_split(
        data, target, test_size=0.25, random_state=1
    )
    predictions = xgboost(x_train, y_train, x_test)
    print(f"Mean Absolute Error: {mean_absolute_error(y_test, predictions)}")
    print(f"Mean Square Error: {mean_squared_error(y_test, predictions)}")
