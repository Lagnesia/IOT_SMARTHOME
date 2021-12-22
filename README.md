AWS_lambda
- Rule Engine에서 trigger 되어 base64로 encoding된 이미지를 디코딩하고 등록된 사용자와의 얼굴과 비교한다. 등록된 사용자면 AWS IoT Core에 true를 publish, 등록된 사용자가 아니라면 Lagnesia가 만든 SMTP 코드를 통해 이메일을 전송한다.

Aws_image_upload.ino
- esp32-cam에서 찍은 이미지를 AWS IoT Core에 publish한다.
- https://github.com/leandrodamascena/aws-detect-a-cat
- 위의 깃에서 arduino/iot-aws-core.ino를 수정하여 만들었다.

Aws_switch_controller
- 강의에서 제공된 코드를 수정하여 만든 light switch controller. 외부에서 사용을 위해 포트포워딩이 필요하다.

b64toImage.py, imagetobase64.py
- 이미지와 base64 형태의 크기 확인 및 lambda test용 base64 데이터 생성 및 AWS IoT에 publish된 base64 데이터 디버깅용 코드

survo.ino
- AWS IoT Core에서 받은 payload로 서보모터를 작동해 스위치를 on/off한다.
