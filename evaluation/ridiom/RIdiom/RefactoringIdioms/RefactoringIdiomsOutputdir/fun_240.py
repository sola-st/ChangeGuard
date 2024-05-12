def main():
    while True:
        print(" Linear Discriminant Analysis ".center(100, "*"))
        print("*" * 100, "\n")
        print("First of all we should specify the number of classes that")
        print("we want to generate as training dataset")
        n_classes = 0
        while True:
            try:
                user_input = int(
                    input("Enter the number of classes (Data Groupings): ").strip()
                )
                if user_input > 0:
                    n_classes = user_input
                    break
                else:
                    print(
                        f"Your entered value is {user_input} , Number of classes "
                        f"should be positive!"
                    )
                    continue
            except ValueError:
                print("Your entered value is not numerical!")
        print("-" * 100)
        std_dev = 1.0  
        while True:
            try:
                user_sd = float(
                    input(
                        "Enter the value of standard deviation"
                        "(Default value is 1.0 for all classes): "
                    ).strip()
                    or "1.0"
                )
                if user_sd >= 0.0:
                    std_dev = user_sd
                    break
                else:
                    print(
                        f"Your entered value is {user_sd}, Standard deviation should "
                        f"not be negative!"
                    )
                    continue
            except ValueError:
                print("Your entered value is not numerical!")
        print("-" * 100)
        counts = []  
        for i in range(n_classes):
            while True:
                try:
                    user_count = int(
                        input(f"Enter The number of instances for class_{i+1}: ")
                    )
                    if user_count > 0:
                        counts.append(user_count)
                        break
                    else:
                        print(
                            f"Your entered value is {user_count}, Number of "
                            f"instances should be positive!"
                        )
                        continue
                except ValueError:
                    print("Your entered value is not numerical!")
        print("-" * 100)
        user_means = []
        for a in range(n_classes):
            while True:
                try:
                    user_mean = float(
                        input(f"Enter the value of mean for class_{a+1}: ")
                    )
                    if isinstance(user_mean, float):
                        user_means.append(user_mean)
                        break
                    print(f"You entered an invalid value: {user_mean}")
                except ValueError:
                    print("Your entered value is not numerical!")
        print("-" * 100)
        print("Standard deviation: ", std_dev)
        for i, count in enumerate(counts, 1):
            print(f"Number of instances in class_{i} is: {count}")
        print("-" * 100)
        for i, user_mean in enumerate(user_means, 1):
            print(f"Mean of class_{i} is: {user_mean}")
        print("-" * 100)
        x = [
            gaussian_distribution(user_means[j], std_dev, counts[j])
            for j in range(n_classes)
        ]
        print("Generated Normal Distribution: \n", x)
        print("-" * 100)
        y = y_generator(n_classes, counts)
        print("Generated Corresponding Ys: \n", y)
        print("-" * 100)
        actual_means = [calculate_mean(counts[k], x[k]) for k in range(n_classes)]
        for i, actual_mean in enumerate(actual_means, 1):
            print(f"Actual(Real) mean of class_{i} is: {actual_mean}")
        print("-" * 100)
        probabilities = [
            calculate_probabilities(counts[i], sum(counts)) for i in range(n_classes)
        ]
        for i, probability in enumerate(probabilities, 1):
            print("Probability of class_{} is: {}".format(i, probability))
        print("-" * 100)
        variance = calculate_variance(x, actual_means, sum(counts))
        print("Variance: ", variance)
        print("-" * 100)
        pre_indexes = predict_y_values(x, actual_means, variance, probabilities)
        print("-" * 100)
        print(f"Accuracy: {accuracy(y, pre_indexes)}")
        print("-" * 100)
        print(" DONE ".center(100, "+"))
        if input("Press any key to restart or 'q' for quit: ").strip().lower() == "q":
            print("\n" + "GoodBye!".center(100, "-") + "\n")
            break
        system("cls" if name == "nt" else "clear")
