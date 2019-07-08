from jinja2 import FileSystemLoader, Environment
from utils import log
import os


def template(name):
    """
    根据名字读取 templates 文件夹里的一个文件并返回
    """
    path = 'templates/' + name
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def response_with_headers(headers, code=200):
    """
    Content-Type: text/html
    Set-Cookie: user=maixy
    """
    header = 'HTTP/1.x {} VERY OK\r\n'.format(code)
    header += ''.join([
        '{}: {}\r\n'.format(k, v) for k, v in headers.items()
    ])
    return header


def formatted_header(headers, code=200):
    """
    Content-Type: text/html
    Set-Cookie: user=maixy
    """
    header = 'HTTP/1.1 {} OK Maixy\r\n'.format(code)
    header += ''.join([
        '{}: {}\r\n'.format(k, v) for k, v in headers.items()
    ])
    return header


def html_response(filename, **kwargs):
    body = MxTemplate.render(filename, **kwargs)

    # 下面 3 行可以改写为一条函数, 还把 headers 也放进函数中
    headers = {
        'Content-Type': 'text/html',
    }
    header = formatted_header(headers)
    r = header + '\r\n' + body
    return r.encode()


def configured_environment():
    path = os.path.join(os.path.dirname(__file__), 'templates')
    log('test path', __file__, os.path.dirname(__file__), path)
    # 创建一个加载器, jinja2 会从这个目录中加载模板
    loader = FileSystemLoader(path)
    # 用加载器创建一个环境, 有了它才能读取模板文件
    e = Environment(loader=loader)
    return e


class MxTemplate:
    e = configured_environment()

    @classmethod
    def render(cls, filename, **kwargs):
        tpl = cls.e.get_template(filename)
        return tpl.render(**kwargs)


def render_response(filename, **kwargs):
    body = MxTemplate.render(filename, **kwargs)
    return html_response(body)
