def local_weight_regression(
    x_train, y_train, tau
):
    y_pred = np.zeros(len(x_train))  
    for i, item in enumerate(x_train):
        y_pred[i] = np.dot(item, local_weight(item, x_train, y_train, tau))
    return y_pred
