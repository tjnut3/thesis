import torch
import serial
import cv2
from ultralytics import YOLO
import time

# ตรวจสอบว่าใช้ GPU ได้หรือไม่
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def send_to_arduino(message, serial_port):
    try:
        serial_port.write((message + '\n').encode())  # ส่งข้อมูลไปยัง Arduino
        print(f"Sent '{message}' to Arduino")
    except Exception as e:
        print(f"Failed to send data to Arduino: {e}")

# โหลดโมเดล YOLO
model = YOLO('best.pt')

# ตั้งค่า Serial Communication กับ Arduino
arduino_port = 'COM3'  # เปลี่ยนตามพอร์ตที่ใช้งาน
baud_rate = 9600
try:
    arduino = serial.Serial(arduino_port, baud_rate, timeout=1)
    print(f"Connected to Arduino on {arduino_port}")
except Exception as e:
    print(f"Failed to connect to Arduino: {e}")
    arduino = None

# --------------------------------------------------------------------------  Set up  -------------------------------------------------------------------------------------------------------

cap = cv2.VideoCapture(0)  # เปิดกล้อง
if not cap.isOpened():
    print("Error: Could not open webcam.")
else:
    while True:
        # อ่านเฟรมจากกล้อง
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # ทำการทำนายวัตถุจากเฟรมปัจจุบัน
        results = model.predict(source=frame, conf=0.5, iou=0.75, show=False)

        # แสดง bounding boxes ลงบนเฟรม
        annotated_frame = results[0].plot()

        # แสดงเฟรมพร้อม bounding box
        cv2.imshow("YOLO Detection", annotated_frame)

        # ตรวจสอบการทำงานของ Arduino sensor
        if arduino and arduino.in_waiting > 0:
            line = arduino.readline().decode().strip()  # อ่านค่าจาก Arduino
            if line == "object_detected":
                print("Object detected by sensor, starting prediction cycle...")
                
                # เริ่มจับเวลา
                start_time = time.time()

                # ตรวจจับคลาสที่โมเดลทำนายได้
                predicted_class = None
                for box in results[0].boxes:
                    class_id = int(box.cls[0])  # ดึง ID ของ class
                    class_name = results[0].names[class_id]  # ดึงชื่อของ class
                    predicted_class = class_name
                    print(f"Predicted class: {predicted_class}")

                    # ส่งค่าคลาสไปยัง Arduino ถ้าตรงตามเงื่อนไข
                    if predicted_class in ['Black', 'Elephant Ear', 'Fade', 'Half', 'Borer Damaged', 'Triangle', 'Incomplete']:
                        send_to_arduino('1', arduino)
                    else:
                        send_to_arduino('0', arduino)

                # จับเวลาสิ้นสุด
                end_time = time.time()
                print(f"Time taken for prediction cycle: {end_time - start_time} seconds")

        # ตรวจสอบการกดปุ่ม 'q' เพื่อออกจาก loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# ปิดการเชื่อมต่อกล้องและหน้าต่างแสดงผล
cap.release()
cv2.destroyAllWindows()