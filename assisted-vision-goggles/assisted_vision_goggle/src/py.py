import tensorflow as tf
interpreter = tf.lite.Interpreter(model_path="model\efficientdet_lite2.tflite")
interpreter.allocate_tensors()

# Get input/output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print("Input Details:", input_details)
print("Output Details:", output_details)
