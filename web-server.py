import socket
import threading
import sys
import framework


class HttpWebServer(object):
    # init魔法方法在类中最先被调用
    def __init__(self, port):
        # 创建tcp socket
        tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        tcp_server_socket.bind(('', port))
        tcp_server_socket.listen(128)

        # 为了使这个变量在其他方法中能被调用，需要初始化一个实例属性
        self.tcp_server_socket = tcp_server_socket

    def start(self):
        while True:
            new_socket, ip_port = self.tcp_server_socket.accept()
            sub_thread = threading.Thread(target=self.handle_client, args=(new_socket,))
            sub_thread.setDaemon(True)
            sub_thread.start()

    # 由于这个方法不需要用到类的其他方法和值，很独立，所以可用静态方法。
    # 可以把静态方法改写成普通实例方法，把self写进形参即可 def handle_client(self, socket)，不影响结果，但是会多占用内存
    # 也可以把此函数写在类外面，但是代码工整度会欠缺
    @staticmethod
    def handle_client(new_socket):

        recv_data = new_socket.recv(4096)

        if len(recv_data) == 0:
            print('浏览器已关闭')
            new_socket.close()
            return

        recv_content = recv_data.decode('utf-8')
        print('web服务器接收的报文：', recv_content)
        request_list = recv_content.split(' ', maxsplit=2)
        request_path = request_list[1]
        print('web服务器提取出来的请求路径： ', request_path)

        if request_path == '/':
            request_path = '/index.html'

        # 判断是否是动态资源请求
        if request_path.endswith('.html'):
            # 动态请求找web框架处理, 把请求资源路径给web框架传参, 通过字典传参
            env = {'request_path': request_path}
            # 使用框架处理动态资源请求
            # 1. web框架把处理结果返回给web服务器
            # 2. web服务器把结果封装成响应报文发给浏览器
            status, headers, response_body = framework.handle_request(env)
            print(status, headers, response_body)
            # 响应行, 为什么不能直接写,不用%号
            response_line = 'HTTP/1.1 %s\r\n' % status
            # 响应头
            response_header = ''
            for header in headers:
                response_header += '%s: %s\r\n' % header
            # 拼接响应报文, 并编码
            response_data = (response_line +
                             response_header +
                             '\r\n' +
                             response_body).encode('utf-8')
            # 发送响应报文
            new_socket.send(response_data)
            new_socket.close()

        else:
            # 下面执行静态资源请求
            try:
                # 打开文件读取文件数据
                with open('static' + request_path, 'rb') as file:
                    file_data = file.read()

            except Exception as e:
                # 把数据封装成http 404 响应报文格式的数据
                with open('static/error.html', 'rb') as file:
                    file_data = file.read()
                # 响应行
                response_line = 'HTTP/1.1 404 Not Found\r\n'
                # 响应头
                response_header = 'Server: PWS/1.0\r\n'
                # 响应体
                response_body = file_data
                # print(type(file_data))
                response = (response_line + '\r\n').encode('utf-8') + response_body
                new_socket.send(response)

            else:
                # 把数据封装成http 响应报文格式的数据

                # 响应行
                response_line = 'HTTP/1.1 200 OK\r\n'
                # 响应头
                response_header = 'Server: PWS/1.0\r\n'
                # 响应体
                response_body = file_data
                print(type(file_data))
                response = (response_line + response_header + '\r\n').encode('utf-8') + response_body
                new_socket.send(response)

            finally:
                new_socket.close()


# 程序入口函数
def main():
    # 通过argv方法获取命令行参数，返还的是列表
    params = sys.argv
    if len(params) != 2:
        print('输入格式错误')
        return
    if not params[1].isdigit():
        print(params[1], '端口号必须得数字')
        return
    port = int(params[1])
    print('输入的端口号是：', port)
    print('输入正确，服务器启动~~~~~~~')
    web_server = HttpWebServer(port)
    web_server.start()


if __name__ == '__main__':
    main()


# 1. 响应头有那么一大长串，为什么代码就写第一行，怎么知道我用的什么server：
#    不必须要发那么多，可简略，保证响应行要有。server就是个名字，自己随便起
# 2. 用网络调试助手发送数据，一发送就断开,而且里面出现乱码
#    网络调试助手的问题
# 3. 用rb二进制方式打开html（相当于做了一次编码），需要用什么方式编码解码，gbk行吗
#    html默认用utf-8编码。如果不涉及中文，用gbk也能解码，统一最好用utf-8。浏览器支持多种格式解码
# 4. 有没有办法知道当前有哪几个线程，哪几个客户端在访问？
#    做一个空列表的全局变量，把收到的新socket打印出来
