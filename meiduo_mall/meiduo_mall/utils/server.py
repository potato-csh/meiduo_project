import socket

def main():
    s = socket.socket()
    # host = socket.gethostname()
    # print(host)

    host = socket.gethostbyname("DESKTOP-8GRF2T1")  # 获取自己的主机ip
    print(host)

    host = '192.168.2.71'
    port =12345
    s.connect((host,port))
    # s.bind((host,port))

    msg = input("你要发送的信息")
    s.send(msg.encode("utf-8"))
    print(s.recv(1024).decode("utf-8"))

    s.close()



main()