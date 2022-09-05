#/usr/bin/env python
#-*- coding:utf8 -*-
import threading
import hashlib
import socket
import base64
import signal
import time ,sys
import math
import subprocess
from PIL import Image
import os
import RPi.GPIO as GPIO
from collections import deque

TEXT = 0x1
clients = {}
exit_flag = False
def new_report(test_report):
    lists = os.listdir(test_report)         # 列出目录的下所有文件和文件夹保存到lists
    lists.sort(key=lambda fn: os.path.getmtime(test_report + "/" + fn)) # 按时间排序
    file_new = os.path.join(test_report, lists[-1])      # 获取最新的文件保存到file_new
    return file_new[18:-4]

#客户端处理线程
class websocket_thread(threading.Thread):
  def __init__(self, connection, username):
      super(websocket_thread, self).__init__()
      self.connection = connection
      self.username = username
      self.sendToClientData = deque()


  def run(self):
      print ('new websocket client joined!')
      data = self.connection.recv(1024)
      
      print ('收到小程序的连接信息:%s'%data)
      headers = self.parse_headers(data)
      print ('收到小程序的连接信息头:%s'%headers)
      token = self.generate_token(headers['Sec-WebSocket-Key'])
      self.connection.send(('\
HTTP/1.1 101 WebSocket Protocol Hybi-10\r\n\
Upgrade: WebSocket\r\n\
Connection: Upgrade\r\n\
Sec-WebSocket-Accept: %s\r\n\r\n' % token).encode("utf-8"))
      while True:
          try:
              data = self.connection.recv(1024)
              print ('收到小程序的数据信息:%s'%data)
              
              "print(len(data))"
             
          except socket.error as e:
              print ("unexpected error: ", e)
              clients.pop(self.username)
              break
         
          data = self.parse_data(data)
          print ('len(data)=%d,内容=%s'%(len(data),data))
          if data == "saoma":
              p = subprocess.Popen(["display", '/home/pi/sao_miao_code/tingcheyoudao.png'])
              print("tu pian yi da kai")
              #x.L76X_Gat_GNRMC()
              #print ('Lon = %f  Lat = %f'%(x.Lon,x.Lat))
          if data == "saoma_wancheng":
              p.kill()
              name=new_report('/home/pi/Pictures')
              self.notify(name)
              #print("bbbb")
              continue
          if data == "likai":
              pass
          if len(data) == 0:
              continue
          message = self.username + ": " + data
          #notify(message)
        
  def parse_data(self, msg):
        g_code_length = msg[1] & 127
        if g_code_length == 126:
            g_code_length = struct.unpack('!H', msg[2:4])[0]
            masks = msg[4:8]
            data = msg[8:]
        elif g_code_length == 127:
            g_code_length = struct.unpack('!Q', msg[2:10])[0]
            masks = msg[10:14]
            data = msg[14:]
        else:
            masks = msg[2:6]
            data = msg[6:]
        i= 0
        raw_by = bytearray()
        for d in data:
            raw_by.append(int(d) ^ int(masks[i % 4]))
            i += 1
        print(raw_by)
        print(u"总长度是：%d" % int(g_code_length))
        raw_str = raw_by.decode() 
        # raw_str = str(raw_by)
        return raw_str

 
            
  def parse_headers(self, msg):
      headers = {}
      msg = str(msg, encoding="utf-8")
      header, data = msg.split('\r\n\r\n', 1)
      for line in header.split('\r\n')[1:]:
          key, value = line.split(': ', 1)
          headers[key] = value
      headers['data'] = data
      return headers
    #通知客户端
  def notify(self,message):
      print ('树莓派发送的信息:%s'%message)
      for connection in clients.values():
                self._sendMessage(False, TEXT, message)
                while self.sendToClientData:
                    data = self.sendToClientData.popleft()
                    print(data[1],"9999999999999999999999999999")
                    connection.send(data[1])
  def _sendMessage(self, FIN, opcode, message):
        payload = bytearray()
        b1 = 0
        b2 = 0
        if FIN is False:
            b1 |= 0x80
        b1 |= opcode  # 若opcode=TEXT    b'0x81'
        payload.append(b1)  #
        msg_utf = message.encode('utf-8')
        msg_len = len(msg_utf)
        if msg_len <= 125:
            b2 |= msg_len
            payload.append(b2)
        elif msg_len >= 126 and msg_len <= 65535:
            b2 |= 126
            payload.append(b2)
            payload.extend(struct.pack("!H", msg_len))
        elif msg_len <= (2 ^ 64 - 1):
            b2 |= 127
            payload.append(b2)
            payload.extend(struct.pack("!Q", msg_len))
        else:
            print("传输的数据太长了! ——(_sendMessage)")
        # 拼接上需要发送的数据
        # 格式大概这样：bytearray(b'\x81\x0cHello World!')   '\x0c'是发送的数据长度
        if msg_len > 0:
            payload.extend(msg_utf)
        self.sendToClientData.append((opcode, payload))

  def generate_token(self, msg):
      key = msg.encode("ascii")+ '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'.encode("ascii")
      token = base64.b64encode(hashlib.sha1(key).digest()).decode("ascii")
      #print(a,"111111111111111111111111111111111111111111111111111111111",type(a))
      return token
  

   


class websocket_server(threading.Thread):
  def __init__(self, port):
      super(websocket_server, self).__init__()
      self.port = port

  def run(self):
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      sock.bind(('192.168.1.108', self.port))
      sock.listen(5)
      while True:
          try:
              print ('websocket server started!')
              connection, address = sock.accept()
              username = "ID" + str(address[1])
              thread = websocket_thread(connection, username)
              thread.setDaemon(True)  #设置守护进程
              thread.start()
              clients[username] = connection
          except socket.timeout:
              print ('websocket connection timeout!')
def catch_ctrlc(signo,frame):
    global exit_flag
    print ('捕获到%d 号信号'%signo)
    exit_flag = True
    
 
if __name__ == '__main__':
    signal.signal(signal.SIGINT,catch_ctrlc)
    server = websocket_server(8000)
    server.setDaemon(True)
    server.start()
    print ('main running...')
    while 1:
        if exit_flag:
            break
        #print ('.',)
        sys.stdout.flush()
        time.sleep(1)


