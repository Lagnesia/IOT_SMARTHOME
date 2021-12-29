import os, copy
import smtplib               # SMTP 라이브러리
from string import Template  # 문자열 템플릿 모듈
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from email.mime.image     import MIMEImage
#1203 13 Contents
#13 22 분석1
#23 31 네이버 이메일 [SMTP, SSL, IMG, 권한]
#32 

#제목: Not Registered Person is trying to get in home.
#내용: [Image] Do you want to keep monitoring him/her? Keep / Ignore

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
            assert os.path.isfile(str_image_file_name), 'image file does not exist.'        
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
        self.ss.login('emailID','emailPW')
        self.ss.send_message(cc, from_addr=str_from_email_addr, to_addrs=str_to_eamil_addrs)
        del cc

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
                                <img src="cid:unregistered01" width="180" height="200 align="TOP"><br>Gender: ${GENDER}<br>Time: ${TIME}</p>
                                <h3>ESP32 CAM found unregistered person.<br>
                                Do you want to keep monitoring him/her?</h3>
                                <br>
                                <button type="button" class="btn btn-primary">KEEP</button>
                                <button type="button" class="btn btn-secondary">IGONORE</button>
                                <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"></script>
                                <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"></script>
                                <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>
                            </body>
                        </html>""")
template_params       = {'NAME':'AWS_IOT', 'GENDER':'MALE','TIME':'20xx.xx.xx hh:mm:ss'} #{ }템플릿
str_image_file_name   = ['cartoon.jpg','celebrity.jpg'] #사진[S3 저장된 사진.]
str_cid_name          = 'unregistered01' #cid 태그.
emailHTMLImageContent = EmailHTMLImageContent(str_subject, str_image_file_name, str_cid_name, template, template_params)

str_from_email_addr = 'aws_iot@naver.com' # 발신자 [이메일 만듬.]
str_to_eamil_addrs  = [''] # 수신자리스트 
email_send.send_message(emailHTMLImageContent, str_from_email_addr, str_to_eamil_addrs)
