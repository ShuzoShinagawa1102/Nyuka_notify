import sys

from selene.browsers import BrowserName
from selene.api import *
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import traceback
from time import sleep
import ssl
import random
import datetime
import schedule
from smtplib import SMTP, SMTP_SSL
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
from email.mime.base import MIMEBase

#URL
url = "https://www.tokaido.tokyo/products/detail/443"


#Create mail function
def createMailMessageMIME(sender, to, message, subject, filepath=None, filename=""):
    #CreateMIMEText
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    msg.attach(MIMEText(message, 'plain', 'utf-8'))

    #AttachImage
    if filepath:
        path = filepath
        attachment = MIMEBase('image', 'png;name="nyuuka.png"')
        file = open(path,"rb")
        attachment.set_payload(file.read())
        file.close()
        encoders.encode_base64(attachment)
        attachment.add_header("Content-Dispositon","attachment",filename='nippou.png') 
        msg.attach(attachment)
    return msg


#Send mail function
def send_email(msg):
    #Login information
    account = "shuzoall@gmail.com"
    password = "qsuyvfhjptlmqsin"
    host = 'smtp.gmail.com'
    port = 465

    #Specify server
    context = ssl.create_default_context()
    server = SMTP_SSL(host, port, context=context)

    #Login
    server.login(account, password)

    #Send mail
    server.send_message(msg)

    #Close
    server.quit()

#Main function
def main():
    #Setup ChromeDriver
    config.browser_name = BrowserName.CHROME
    chrome_option = webdriver.ChromeOptions()
    chrome_option.add_argument('--headless')
    chrome_option.add_argument('--disable-gpu')
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_option)
    browser.set_driver(driver)

    #Access to Tokaido site
    browser.open_url(url)
    page_width = driver.execute_script('return document.body.scrollWidth')
    page_height = driver.execute_script('return document.body.scrollHeight')
    driver.set_window_size(page_width, page_height)

    #Select grove(red)
    element = driver.find_element(By.ID, "classcategory_id1")
    Select(element).select_by_value("152")
    element.click()
    sleep(2.0)

    #Check size
    element = driver.find_element(By.ID, "classcategory_id2")
    all_options = Select(element).options
    new_elem = all_options[2].text

    #Screenshots
    element = driver.find_element(By.ID, "classcategory_id2")
    Select(element).select_by_value("59")
    sleep(2.0)
    driver.save_screenshot("nyuuka.png")

    #Close
    browser.quit()

    #Output to text file
    try:
        with open("old_elem.txt") as f:
            old_elem = f.read()
    except:
        old_elem = " "

    #If product arrive, notify by mail
    try:
        if new_elem == old_elem:
            print("No change")
        else:
            with open("old_elem.txt", "w") as f:
                f.write(new_elem)
            print("Product Arrived")
            #From
            from_email = "shuzoall@gmail.com"
            #To
            to_email = "koukakarate2009@yahoo.co.jp"
	    #Mail contents
            subject = "商品入荷状況"
            message = "確認してください。"
            mime = createMailMessageMIME(from_email, to_email, message, subject, filepath="nyuuka.png", filename="nyuuka")
            send_email(mime)
            print("Job has done!")
    except:
        pass

schedule.every(1).minutes.do(main)

while True:
    try:
        schedule.run_pending()
        sleep(3)
    except:
        print("error occured")
