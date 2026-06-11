#include <Arduino.h>
#include <Servo.h>

const int SERVO_PIN = 0;
const int BUTTON_UP = 2;
const int BUTTON_DOWM = 3;
const int BUTTON_ENABLE_MANUAL = 4;

const int BUTTON_FLYWHEEL = 5;

const int MOTOR1_PWM = 6;
const int MOTOR2_PWM = 10;

const float g = 9.81;
const float launchVelocity = 6.44;
const float launchHeight = 0.0734;

const float gearRatio = 4.0;

float targetDistance = 1.0;

Servo launcherServo;

bool flywheelOn = false;
bool lastButtonState = HIGH;

float launcherAngle = 0;
float servoAngle = 0;

int flywheelPWM = 255;

String serialBuffer = " ";

float calculateLaunchAngle(float range) {
    float numerator = (range * range * g) - (launchHeight - launchVelocity*launcherAngle);
    float denominator = (launchVelocity * launchVelocity) * sqrt((range * range) + (launchHeight * launchHeight));
    float term1 = asin(numerator / denominator);
    float term2  = atan(launchHeight / range);
    float theta = 0.5 * (term1 - term2);
    return degrees(theta);
}

void moveToDistance(float distance) {
    launcherAngle = calculateLaunchAngle(distance);

    servoAngle = launcherAngle * gearRatio;

    servoAngle = constrain(servoAngle, 0, 180);

    launcherServo.write(servoAngle);

    Serial.print("Distance = ");
    Serial.print(distance);

    Serial.print(" m   Launcher Angle = ");
    Serial.print(launcherAngle);

    Serial.print(" deg   Servo Angle = ");
    Serial.println(servoAngle);

}

void startFlyWheel() {
    analogWrite(MOTOR1_PWM, flywheelPWM);

    analogWrite(MOTOR2_PWM, flywheelPWM);

    flywheelOn = true;

    Serial.println("Starting flywheel");
}

void stopFlyWheel() {
    analogWrite(MOTOR1_PWM, 0);

    analogWrite(MOTOR2_PWM, 0);

    flywheelOn = false;

    Serial.println("Stopping flywheel");
}

void readDistanceFromSerial() {
    while (Serial.available() > 0) {
        char c = Serial.read();

        if (c == '\n') {
            float distanceCm = serialBuffer.toFloat();
            serialBuffer = "";

            if (distanceCm > 0) {
                float newTargetDistance = distanceCm / 100.0; // cm -> m

                if (abs(newTargetDistance - targetDistance) >= 0.01) {
                    targetDistance = newTargetDistance;
                    moveToDistance(targetDistance);
                }
            }
        } else if (c != '\r') {
            serialBuffer += c;
        }
    }
}

void setup() {
    Serial.begin(9600);

    pinMode(BUTTON_UP, INPUT_PULLUP);
    pinMode(BUTTON_DOWM, INPUT_PULLUP);
    pinMode(BUTTON_ENABLE_MANUAL, INPUT_PULLUP);

    pinMode(BUTTON_FLYWHEEL, INPUT_PULLUP);

    pinMode(MOTOR1_PWM, OUTPUT);
    pinMode(MOTOR2_PWM, OUTPUT);

    launcherServo.attach(SERVO_PIN);

    launcherAngle = 0;
    servoAngle = 0;

    launcherServo.write(0);
    delay(1000);

    moveToDistance(targetDistance);
}

void loop() {
    readDistanceFromSerial();

    bool currentButton = digitalRead(BUTTON_FLYWHEEL);

    if (lastButtonState == HIGH && currentButton == LOW) {
        if (flywheelOn) {
            stopFlyWheel();
        }
        else {
            startFlyWheel();
        }
        delay(250);
    }

    lastButtonState = currentButton;

    if (digitalRead(BUTTON_ENABLE_MANUAL) == LOW) {
        if (digitalRead(BUTTON_UP) == LOW) {
            servoAngle++;

            servoAngle = constrain(servoAngle, 0, 180);

            launcherServo.write(servoAngle);

            delay(15);
        }

        if (digitalRead(BUTTON_DOWM) == LOW) {
            servoAngle--;

            servoAngle = constrain(servoAngle, 0, 180);

            launcherServo.write(servoAngle);

            delay(15);
        }
    }
}