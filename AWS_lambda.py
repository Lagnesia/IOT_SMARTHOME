import json
from base64 import b64decode
import boto3
import uuid
from datetime import datetime
import smtplib               # SMTP 라이브러리
import copy
from string import Template  # 문자열 템플릿 모듈
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from email.mime.image     import MIMEImage

def lambda_handler(event, context):
    # TODO implement
    bucket="family-face"
    model_arn='model arn'
    b64_r = event['picture']
    
    # aws resources
    client = boto3.client("rekognition")
    s3 = boto3.client("s3")
    
    # Extract JEPG-encoded image from base64-encoded string
    photo = b64decode(b64_r)
    imageId = str(uuid.uuid4())
    imgtempname = "/tmp/{0}.{1}".format(imageId,"jpg")
    with open(imgtempname,"wb") as f:
        f.write(photo)
        f.close()
    
    
    # family face image
    for obj in s3.list_objects(Bucket=bucket)['Contents']:
        print(obj['Key'])
        fileObj = s3.get_object(Bucket=bucket, Key=obj['Key'])
        file_content = fileObj["Body"].read()
        with open(imgtempname,"rb") as image:
            response=client.compare_faces(SimilarityThreshold=80, SourceImage={"Bytes":file_content}, TargetImage={"Bytes":image.read()})
            image.close()
        #print(response)
        for faceMatch in response['FaceMatches']:
            position = faceMatch['Face']['BoundingBox']
            similarity = str(faceMatch['Similarity'])
            print('The face at '+
                  str(position['Left'])+' '+
                  str(position['Top'])+
                  ' matches with '+similarity+'% confidence')
                  
            if float(similarity)>90:
                cl=boto3.client('iot-data')
                resp = cl.publish(topic='cam/door/entry',qos=1,payload=json.dumps({"family":"true"}))
                return {'statusCode':200,'body':json.dumps('Hello from Lambda!')}
    '''
    # sending email using AWS IoT and AWS SNS
    # s3 upload 
    bucket_name='stranger-face'
    now = datetime.now()
    #bucket name where you want to upload image
    file_name="%d%02d%02d_%02d%02d%02d"%(now.year, now.month, now.day, now.hour, now.minute, now.second)
    s3.upload_file(imgtempname,bucket_name, file_name, ExtraArgs={'ACL':'public-read',"ContentType": 'image/jpeg'})
    s3_url = "https://"+bucket_name+".s3.ap-northeast-2.amazonaws.com/"+file_name
    
    # publish stranger
    cl=boto3.client('iot-data')
    resp = cl.publish(topic='cam/door/entry',qos=1,payload=json.dumps({"family":"false","image":s3_url }))
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    '''
    
    email_send = EmailSender()
    
    str_subject = 'Not Registered Person is trying to get in home.'
    template = Template("""<html>
                                <head>
                                    <style>
                                        img {
                                            width: 50px;
                                            height: 100px;
                                        }
                                        p {
                                            font-size: 20px;
                                            font-weight: bold;
                                        }
                                    </style>
                                     <link rel="stylesheet" href="css/style.css">
                                </head>
                                <body>
                                    <h2>Hi ${NAME}.<h2>
                                    <h1>UnRegistered Person in ESP32 CAM</h1>
                                    <br>
                                    <h4>photo</h4>
                                    <img src="cid:unregistered01" width="180" height="200 align="TOP"><br>Time: ${TIME}</p>
                                    <h3>ESP32 CAM found unregistered person.</h3>
                                    <br>
                                    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"></script>
                                    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"></script>
                                    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>
                                </body>
                            </html>""")
    # Sending email using SMTP module
    now = datetime.now()
    #bucket name where you want to upload image
    img_time="%d.%02d.%02d %02d:%02d:%02d"%(now.year, now.month, now.day, now.hour, now.minute, now.second)
    template_params       = {'NAME':'Sung Jae Kim','TIME':img_time} #{ }템플릿
    str_image_file_name   = [imgtempname] #사진[S3 저장된 사진.]
    str_cid_name          = 'unregistered01' #cid 태그.
    emailHTMLImageContent = EmailHTMLImageContent(str_subject, str_image_file_name, str_cid_name, template, template_params)
    
    str_from_email_addr = 'aws_iot@naver.com' # 발신자 [이메일 만듬.]
    # Place User's email here
    str_to_eamil_addrs  = ['userEmailHere@EmailDomainHere.com'] # 수신자리스트 
    email_send.send_message(emailHTMLImageContent, str_from_email_addr, str_to_eamil_addrs)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


class EmailHTMLImageContent:
    """e메일에 담길 이미지가 포함된 컨텐츠"""
    def __init__(self, str_subject, list_image_file_name, str_cid_name, template, template_params):
        """이미지파일(str_image_file_name), 컨텐츠ID(str_cid_name)사용된 string template과 딕셔너리형 template_params받아 MIME 메시지를 만든다"""
        assert isinstance(template, Template)
        assert isinstance(template_params, dict)
        self.msg = MIMEMultipart()
        
        # e메일 제목을 설정한다
        self.msg['Subject'] = str_subject 
        
        # e메일 본문을 설정한다
        str_msg  = template.safe_substitute(**template_params) # ${변수} 템플릿 만듬.
        mime_msg = MIMEText(str_msg, 'html')                   # MIME HTML 문자열 만듬.
        self.msg.attach(mime_msg)
        
        # e메일 본문에 이미지를 임베딩한다
        assert template.template.find("cid:" + str_cid_name) >= 0, 'template must have cid for embedded image.'
        for str_image_file_name in list_image_file_name:   
            with open(str_image_file_name, 'rb') as img_file:
                mime_img = MIMEImage(img_file.read())
                mime_img.add_header('Content-ID', '<' + str_cid_name + '>')
            self.msg.attach(mime_img)
        
    def get_message(self, str_from_email_addr, str_to_eamil_addrs):
        """발신자, 수신자리스트를 이용하여 보낼메시지를 만든다 """
        mm = copy.deepcopy(self.msg)
        mm['From'] = str_from_email_addr          # 발신자 
        mm['To']   = ",".join(str_to_eamil_addrs) # 수신자리스트 
        return mm

class EmailSender:
    """e메일 발송자"""
    def __init__(self, str_host="Smtp.naver.com", num_port=465):
        """호스트와 포트번호로 SMTP로 연결한다 """
        self.str_host = str_host
        self.num_port = num_port
        self.ss = smtplib.SMTP_SSL(host=str_host, port=num_port)
        # SMTP인증이 필요하면 아래 주석을 해제하세요.
        #self.ss.starttls() # TLS(Transport Layer Security) 시작
        #self.ss.login('계정명', '비밀번호') # 메일서버에 연결한 계정과 비밀번호
    
    def send_message(self, emailContent, str_from_email_addr, str_to_eamil_addrs):
        """e메일을 발송한다 """
        cc = emailContent.get_message(str_from_email_addr, str_to_eamil_addrs)
        self.ss.login('aws_iot@naver.com','iloveprofessor')
        self.ss.send_message(cc, from_addr=str_from_email_addr, to_addrs=str_to_eamil_addrs)
        del cc
