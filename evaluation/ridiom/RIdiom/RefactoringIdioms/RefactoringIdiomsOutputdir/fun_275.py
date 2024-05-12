def roc_curve(y_true, y_score):
    y_true = y_true.ravel()
    classes = np.unique(y_true)
    if classes.shape[0] != 2:
        raise ValueError("ROC is defined for binary classification only")
    y_score = y_score.ravel()
    thresholds = np.sort(np.unique(y_score))[::-1]
    n_pos , n_neg , thresholds  = float(np.sum(y_true == classes[1])), float(np.sum(y_true == classes[0])), np.unique(y_score)  
    neg_value, pos_value = classes[0], classes[1]
    tpr , fpr  = np.empty(thresholds.size), np.empty(thresholds.size)  
    dpos = dneg = sum_pos = sum_neg = idx = 0
    sorted_signal = sorted(zip(y_score, y_true), reverse=True)
    last_input = sorted_signal[0][0]
    for each, value in sorted_signal:
        if each == last_input:
            if value == pos_value:
                dpos += 1
            else:
                dneg += 1
        else:
            tpr[idx] , fpr[idx]  = (sum_pos + dpos) / n_pos, (sum_neg + dneg) / n_neg
            sum_pos += dpos
            sum_neg += dneg
            dpos , dneg  = 1 if value == pos_value else 0, 1 if value == neg_value else 0
            idx += 1
            last_input = each
    else:
        tpr[-1] , fpr[-1]  = (sum_pos + dpos) / n_pos, (sum_neg + dneg) / n_neg
    if fpr.shape[0] == 2:
        fpr , tpr  = np.array([0.0, fpr[0], fpr[1]]), np.array([0.0, tpr[0], tpr[1]])
    elif fpr.shape[0] == 1:
        fpr , tpr  = np.array([0.0, fpr[0], 1.0]), np.array([0.0, tpr[0], 1.0])
    return fpr, tpr, thresholds
