import smtplib

# Gmail 示例
server = smtplib.SMTP('smtp.qq.com', 587, timeout=10)
server.ehlo()
server.starttls()
server.login('490095023@qq.com', 'pslvkdsectqwcadf')
server.quit()