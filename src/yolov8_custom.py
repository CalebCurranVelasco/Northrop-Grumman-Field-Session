from ultralytics import YOLO

# load our model
model = YOLO('models/custom_yolo_model.pt')

# Run inference of the osurce
results = model(source='../Assets/VehicleImages/image_41_1_547153ea7e3f4396abce4e14eb600079.jpg', show=True, conf=0.25, save=True)