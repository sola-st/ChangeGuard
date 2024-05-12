def roc_curve(y_true, y_score):
    y_true = y_true.ravel()
    classes = np.unique(y_true)
    if classes.shape[0] != 2:
        raise ValueError("ROC is defined for binary classification only")
    y_score = y_score.ravel()
    thresholds = np.sort(np.unique(y_score))[::-1]
    n_pos = float(np.sum(y_true == classes[1]))  
    n_neg = float(np.sum(y_true == classes[0]))  
    thresholds = np.unique(y_score)
    neg_value, pos_value = classes[0], classes[1]
    tpr = np.empty(thresholds.size)  
    fpr = np.empty(thresholds.size)  
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
            tpr[idx] = (sum_pos + dpos) / n_pos
            fpr[idx] = (sum_neg + dneg) / n_neg
            sum_pos += dpos
            sum_neg += dneg
            dpos = 1 if value == pos_value else 0
            dneg = 1 if value == neg_value else 0
            idx += 1
            last_input = each
    else:
        tpr[-1] = (sum_pos + dpos) / n_pos
        fpr[-1] = (sum_neg + dneg) / n_neg
    if fpr.shape[0] == 2:
        fpr = np.array([0.0, fpr[0], fpr[1]])
        tpr = np.array([0.0, tpr[0], tpr[1]])
    elif fpr.shape[0] == 1:
        fpr = np.array([0.0, fpr[0], 1.0])
        tpr = np.array([0.0, tpr[0], 1.0])
    return fpr, tpr, thresholds
