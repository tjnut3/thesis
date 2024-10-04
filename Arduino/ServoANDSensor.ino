#include <Servo.h>

int irSensorPin = 2;  // ขาเชื่อมต่อ IR sensor
Servo myServo;
int servoPin = 9;  // ขาเชื่อมต่อ Servo
int servoAngle = 0;  // มุมเริ่มต้นของ Servo

void setup() {
  pinMode(irSensorPin, INPUT);
  myServo.attach(servoPin);  // กำหนดขาเชื่อมต่อให้ Servo
  myServo.write(servoAngle);  // ตั้งค่า Servo ให้อยู่ที่มุมเริ่มต้น
  Serial.begin(9600);  // เริ่มต้นการสื่อสารอนุกรม
}

void loop() {
  int sensorValue = digitalRead(irSensorPin);
  if (sensorValue == LOW) {  // ถ้า IR sensor ตรวจจับวัตถุ
    Serial.println("object_detected");  // ส่งข้อความไปยัง Python เพื่อเริ่มถ่ายภาพ
    delay(1000);

    // รอรับข้อมูลจาก Python
    if (Serial.available() > 0) {
      String prediction = Serial.readStringUntil('\n');  // รับค่าการทำนายจาก Python

      if (prediction == "1") {  // ถ้าเมล็ดกาแฟเสีย
        delay(4000);
        myServo.write(50);  // หมุน Servo ไปที่มุม 90 องศา
        delay(1000);  // รอ 1 วินาที
        myServo.write(servoAngle);  // กลับมาที่มุมเริ่มต้น
      }
    }
  }
}