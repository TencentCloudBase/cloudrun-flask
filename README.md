# 快速部署 Flask 应用

本篇文章为您介绍应用控制台的部署方案, 您可以通过以下操作完成部署。

## 模版部署 Flask 应用

1、登录 [腾讯云托管控制台](https://tcb.cloud.tencent.com/dev#/platform-run/service/create?type=image)

2、点击通过模版部署，选择 ```Flask 模版```

3、输入自定义服务名称，点击部署

4、等待部署完成之后，点击左上角箭头，返回到服务详情页

5、点击概述，获取默认域名并访问，会显示云托管默认首页

## 自定义部署 Flask 应用

### 创建一个 Flask 应用

要创建新的 Flask 应用程序，需要机器上安装[Python](https://www.python.org/downloads/)和 Flask。

按照以下步骤在目录中设置项目。

创建一个```cloudrun-flask```目录, ```cd```进入该目录。

创建虚拟环境

```sh
python -m venv env
```

激活虚拟环境

```sh
source env/bin/activate
```

安装 Flask

```sh
python -m pip install flask
```

在`cloudrun-flask`目录中创建一个新文件 `manage.py`, 内容如下:

```py
import os
from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello world!'
```

1、`from flask import Flask`

- 此行从 Flask 框架导入 Flask 类，用于创建和管理 Web 应用程序。

2、`app = Flask(__name__)`

- 此行创建 Flask 类的实例并将其分配给 app 变量。
- 该**name**参数帮助 Flask 识别应用程序的位置。它对于确定资源路径和错误报告很有用。

3、`@app.route('/')`

- 该`@app.route('/')`装饰器为应用设置了 URL 路由。当(/)访问根 URL 时，Flask 将执行紧接着该装饰器下方的函数。

4、`def hello()`

- 该 hello 函数返回一条纯文本消息“Hello world!”，当访问应用程序的根 URL 时，该消息将显示在浏览器中。

在`cloudrun-flask`目录下执行`python3 manage.py runserver 0.0.0.0:8080` 启动服务, 打开浏览器并查看`http://127.0.0.1:8080`查看返回结果。

### 源码

[cloudrun-flask](https://github.com/TencentCloudBase/tcbr-templates/tree/main/cloudrun-flask)

### 部署到云托管

1、配置依赖项

建 `requirements.txt` 文件:
要跟踪部署的所有依赖项，请创建一个`requirements.txt`文件:

```sh
pip freeze > requirements.txt
```

Note: 只有在虚拟环境中运行上述命令才是安全的，否则它将生成系统上所有安装的 python 包。可能导致云托管上无法启动该应用程序。

2、在cloudrun-flask目录下创建一个名称为Dockerfile的新文件,内容如下:

```
FROM alpine

# 容器默认时区为UTC，如需使用上海时间请启用以下时区设置命令
RUN apk add tzdata && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo Asia/Shanghai > /etc/timezone

# 选用国内镜像源以提高下载速度
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tencent.com/g' /etc/apk/repositories \
&& apk add --update --no-cache python3 py3-pip gcc python3-dev linux-headers musl-dev \
&& rm -rf /var/cache/apk/*

# 使用 HTTPS 协议访问容器云调用证书安装
RUN apk add ca-certificates

# 拷贝当前项目到/app目录下(.dockerignore中文件除外)
COPY . /app

# 设定当前的工作目录
WORKDIR /app

# 安装依赖到指定的/install文件夹
# 选用国内镜像源以提高下载速度
RUN pip config set global.index-url http://mirrors.cloud.tencent.com/pypi/simple \
&& pip config set global.trusted-host mirrors.cloud.tencent.com \
&& pip install --upgrade pip --break-system-packages \
# pip install scipy 等数学包失败，可使用 apk add py3-scipy 进行， 参考安装 https://pkgs.alpinelinux.org/packages?name=py3-scipy&branch=v3.13
&& pip install --user -r requirements.txt --break-system-packages

# 执行启动命令
# 写多行独立的CMD命令是错误写法！只有最后一行CMD命令会被执行，之前的都会被忽略，导致业务报错。
# 请参考[Docker官方文档之CMD命令](https://docs.docker.com/engine/reference/builder/#cmd)
CMD ["python3", "manage.py", "runserver","0.0.0.0:8080"]
```

3、进入 [腾讯云托管](https://tcb.cloud.tencent.com/dev#/platform-run/service/create?type=package),

4、选择 ```通过本地代码``` 部署，

5、填写配置信息:

  * 代码包类型: 选择文件夹
  * 代码包: 点击选择 cloudrun-flask 目录，并上传目录文件
  * 服务名称: 填写服务名称
  * 部署类型: 选择容器服务型
  * 端口: 默认填写 8080
  * 目标目录: 默认为空
  * Dockerfile 名称: Dockerfile
  * 环境变量: 如果有按需要填写
  * 公网访问: 默认打开
  * 内网访问: 默认关闭

5、配置填写完成之后，点击部署等待部署完成，

6、部署完成之后，跳转到服务概述页面，点击默认域名进行公网访问及测试。
