from ultralytics import YOLO

# Load YOLOv8 model (pretrained on COCO)
model = YOLO('yolov8n.pt')

# Run detection
# Replace with your image path
results = model('images/Screenshot-NoPerson.png')

# Get detection data
for result in results:
    result.show()
    for box in result.boxes:
        class_id = int(box.cls[0])
        class_name = model.names[class_id]
        print(box.xyxy, box.conf, box.cls, class_name)
        if class_name == 'person':
            print("\nPerson detected!")
        else:
            print("\nNo person detected.")
