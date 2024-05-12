def predict(self, input_arr):
    self.array = input_arr
    self.layer_between_input_and_first_hidden_layer = sigmoid(
        numpy.dot(self.array, self.input_layer_and_first_hidden_layer_weights)
    )
    self.layer_between_first_hidden_layer_and_second_hidden_layer = sigmoid(
        numpy.dot(
            self.layer_between_input_and_first_hidden_layer,
            self.first_hidden_layer_and_second_hidden_layer_weights,
        )
    )
    self.layer_between_second_hidden_layer_and_output = sigmoid(
        numpy.dot(
            self.layer_between_first_hidden_layer_and_second_hidden_layer,
            self.second_hidden_layer_and_output_layer_weights,
        )
    )
    return int((self.layer_between_second_hidden_layer_and_output > 0.6)[0])
