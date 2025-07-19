from flask import Flask, request, redirect, url_for, send_from_directory, session
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import json
from functools import wraps

import logging
import traceback
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # 用于会话管理的密钥

# 配置日志
app.logger.setLevel(logging.DEBUG)
# 控制台日志
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
# 文件日志
file_handler = logging.FileHandler('/Volumes/DIS125G/网页制作/网盘/app.log')
file_handler.setLevel(logging.DEBUG)
# 日志格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
app.logger.addHandler(stream_handler)
app.logger.addHandler(file_handler)
app.logger.debug("日志系统初始化完成，已启用文件日志记录")
# 配置上传文件夹
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 支持所有文件类型
app.config['ALLOW_UNSAFE_FILES'] = True

# 取消文件大小限制
app.config['MAX_CONTENT_LENGTH'] = None

# 用户数据文件
USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users.json')

# 用户数据加载和保存函数
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}
    except Exception as e:
        app.logger.error(f"加载用户数据时出错: {str(e)}")
        return {}

def save_users(users):
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=4)
    except Exception as e:
        app.logger.error(f"保存用户数据时出错: {str(e)}")

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    # 允许所有文件类型
    return True

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET'])
@login_required
def upload_page():
    # 显示上传表单
    app.logger.debug('访问上传页面 - 方法: GET')
    return '''
    <!doctype html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>文件上传 - 网盘系统</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .container { max-width: 800px; margin: 2rem auto; }
            .card {{ box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/upload">网盘系统</a>
                <div class="collapse navbar-collapse">
                    <ul class="navbar-nav ms-auto">
                        <li class="nav-item"><a class="nav-link" href="/upload">上传文件</a></li>
                        <li class="nav-item"><a class="nav-link" href="/files">文件列表</a></li>
                    </ul>
                </div>
            </div>
        </nav>
        <div class="container mt-4">
            <div class="card p-4">
                <h2 class="mb-4">文件上传</h2>
                <form method=post action="/upload" enctype=multipart/form-data class="mb-3">
                    <div class="mb-3">
                        <label for="file" class="form-label">选择文件</label>
                        <input type=file name=file class="form-control" id="file" required>
                    </div>
                    <button type=submit value=上传 class="btn btn-primary">上传文件</button>
                </form>
                <div class="alert alert-info">
                    支持上传多种格式文件, 最大文件大小限制：10MB
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    print("开始处理文件上传...")
    app.logger.debug("进入文件上传路由")
    # 检查是否有文件部分
    if 'file' not in request.files:
        app.logger.error('上传请求中没有文件部分')
        return '上传请求中没有文件部分', 400
    file = request.files['file']
    app.logger.debug(f"获取到文件: {file.filename if file else '空'}")
    # 如果用户没有选择文件，浏览器会提交一个空部分
    if file.filename == '':
        app.logger.warning('未选择上传文件')
        return '未选择上传文件', 400
    if not allowed_file(file.filename):
        app.logger.warning(f"不允许的文件类型: {file.filename}")
        return '不允许的文件类型', 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        app.logger.debug(f"安全处理后的文件名: {filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        app.logger.debug(f"文件保存路径: {file_path}")
        try:
            # 确保上传目录存在
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            app.logger.debug(f"确保上传目录存在: {app.config['UPLOAD_FOLDER']}")
            # 检查文件是否已存在
            if os.path.exists(file_path):
                app.logger.warning(f'文件已存在: {file_path}')
                return f"文件已存在，请重命名后上传", 409
            # 保存文件
            file.save(file_path)
            app.logger.info(f"文件保存成功: {file_path}")
            # 验证文件是否保存成功
            if not os.path.exists(file_path):
                app.logger.error(f"文件保存失败: {file_path}")
                return f"文件保存失败, 请检查服务器权限", 500
            return redirect(url_for('files_list'))
        except PermissionError:
            app.logger.error(f"文件保存权限错误: {file_path} - {traceback.format_exc()}")
            return '服务器权限错误，无法保存文件', 500
        except OSError as e:
            app.logger.error(f"文件保存系统错误: {str(e)} - {file_path} - {traceback.format_exc()}")
            return f'文件保存失败: {str(e)}', 500
        except Exception as e:
            app.logger.error(f"文件上传未知错误: {str(e)} - {traceback.format_exc()}")
            return f'文件上传失败: {str(e)}', 500
    return '上传失败', 400

@app.route('/')
def home():
    return redirect(url_for('upload_file'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        try:
            app.logger.info(f"尝试加载用户数据文件: {USERS_FILE}")
            users = load_users()
            app.logger.info(f"成功加载用户数据，共 {len(users)} 个用户")
        except Exception as e:
            app.logger.error(f"加载用户数据失败: {str(e)}")
            return '''<div class='alert alert-danger text-center' role='alert'>服务器错误, 无法加载用户数据</div><div class='text-center mt-3'><a href='/login' class='btn btn-secondary'>返回登录</a></div>'''

        if username in users:
            return '''<div class="alert alert-danger text-center" role="alert">用户名已存在</div><div class="text-center mt-3"><a href="/register" class="btn btn-secondary">返回注册</a></div>'''

        # 密码哈希存储
        hashed_password = generate_password_hash(password, method='scrypt:32768:8:1')
        app.logger.info(f"注册用户: {username}, 生成哈希: {hashed_password}")
        users[username] = hashed_password
        save_users(users)
        return redirect(url_for('login'))

    return '''
    <!doctype html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>注册 - 网盘系统</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ background-color: #f5f5f5; }}
            .auth-container {{ max-width: 400px; margin: 5rem auto; }}
            .card {{ box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
        </style>
    </head>
    <body>
        <div class="auth-container">
            <div class="card p-4">
                <h2 class="text-center mb-4">用户注册</h2>
                <form method=post>
                    <div class="mb-3">
                        <label for="username" class="form-label">用户名</label>
                        <input type="text" class="form-control" id="username" name="username" placeholder="请创建用户名" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">密码</label>
                        <input type="password" class="form-control" id="password" name="password" placeholder="请创建密码" required>
                    </div>
                    <button type="submit" class="btn btn-success w-100">注册</button>
                </form>
                <div class="text-center mt-3">
                    <a href="/login" class="text-decoration-none">已有账号？立即登录</a>
                </div>
            </div>
        </div>
    </body>
    </html>'''

@app.route('/test', methods=['GET'])
def test():
    print("[DEBUG] 测试路由被访问")
    app.logger.info("[DEBUG] 测试路由被访问")
    return '测试路由正常工作'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        print(f"[DEBUG] 登录请求接收 - 方法: {request.method}, 表单数据: {request.form.to_dict()}")
        app.logger.info(f"登录请求接收 - 方法: {request.method}, 表单数据: {request.form.to_dict()}")
        print(f"[DEBUG] 登录尝试 - 原始用户名: {request.form.get('username')}, 处理后用户名: {username}, 密码长度: {len(password)}")
        app.logger.info(f"登录尝试 - 原始用户名: {request.form.get('username')}, 处理后用户名: {username}, 密码长度: {len(password)}")
        if not username or not password:
            return "Username and password cannot be empty. Please return to login page."
        try:
            users = load_users()
        except Exception as e:
            app.logger.error(f"加载用户数据失败: {str(e)}")
            return '''<div class="alert alert-danger text-center" role="alert">服务器错误, 无法加载用户数据</div><div class="text-center mt-3"><a href="/login" class="btn btn-secondary">返回登录</a></div>'''

        if username in users:
            app.logger.debug(f"[DEBUG] 找到用户: {username}, 存储的哈希: {users[username]}")
            # 生成输入密码的哈希用于调试
            generated_hash = generate_password_hash(password, method='scrypt:32768:8:1')
            app.logger.debug(f"[DEBUG] 输入密码生成的哈希: {generated_hash}")
            password_match = check_password_hash(users[username], password)
            print(f"[DEBUG] 密码比对结果: {password_match}")
            app.logger.info(f"密码比对结果: {password_match}")
            if password_match:
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('upload_file'))
            else:
                return '''<div class="alert alert-danger text-center" role="alert">密码错误</div><div class="text-center mt-3"><a href="/login" class="btn btn-secondary">返回登录</a></div>'''
        else:
            return '''<div class="alert alert-danger text-center" role="alert">用户名不存在</div><div class="text-center mt-3"><a href="/login" class="btn btn-secondary">返回登录</a></div>'''
    # GET请求返回登录表单
    return r'''
    <!doctype html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>登录 - 网盘系统</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="/static/css/login.css">
    </head>
    <body>
        <div class="auth-container">
            <div class="card p-4">
                <h2 class="text-center mb-4">用户登录</h2>
                <form method=post>
                    <div class="mb-3">
                        <label for="username" class="form-label">用户名</label>
                        <input type="text" class="form-control" id="username" name="username" placeholder="请输入用户名" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">密码</label>
                        <input type="password" class="form-control" id="password" name="password" placeholder="请输入密码" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">登录</button>
                </form>
                <div class="text-center mt-3">
                    <a href="/register" class="text-decoration-none">没有账号?立即注册</a>
                </div>
            </div>
        </div>
    </body>
    </html>'''

@app.route('/files')
@login_required
def files_list():
    try:
        # 添加调试信息
        app.logger.info(f"尝试列出目录: {app.config['UPLOAD_FOLDER']}")
        # 检查上传目录是否存在
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            app.logger.warning(f"上传目录不存在，创建目录: {app.config['UPLOAD_FOLDER']}")
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        app.logger.info(f"找到文件: {files}")
        file_links = []
        for file in files:
            # 排除系统隐藏文件
            if not file.startswith('.'):
                file_links.append(f'<li>{file} <a href="/download/{file}">下载</a></li>')
        return f'''
        <!doctype html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>文件列表 - 网盘系统</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="/static/css/style.css">
        </head>
        <body>
            <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
                <div class="container">
                    <a class="navbar-brand" href="/upload">网盘系统</a>
                    <div class="collapse navbar-collapse">
                        <ul class="navbar-nav ms-auto">
                            <li class="nav-item"><a class="nav-link" href="/upload">上传文件</a></li>
                            <li class="nav-item"><a class="nav-link active" href="/files">文件列表</a></li>
                        </ul>
                    </div>
                </div>
            </nav>
            <div class="container mt-4">
                <div class="card p-4">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h2>文件列表</h2>
                        <a href="/upload" class="btn btn-primary">上传新文件</a>
                    </div>
                    <p class="text-muted">存储路径: {app.config['UPLOAD_FOLDER']}</p>
                    {f'<div class="alert alert-info">找到 {len(file_links)} 个文件</div>' if file_links else '<div class="alert alert-warning">暂无上传文件</div>'}
                     <div class="table-responsive"><table class="table table-striped table-hover"><thead><tr><th>文件名</th><th>操作</th></tr></thead><tbody>{''.join([f'<tr><td>{file}</td><td><a href="/download/{file}" class="btn btn-sm btn-outline-primary">下载</a></td></tr>' for file in files if not file.startswith('.')])}</tbody></table></div>
                </div>
              </div>
              </body>
          </html>
        '''
    except Exception as e:
        app.logger.error(f"""文件列表错误: {str(e)}
{traceback.format_exc()}""")
        return f'''
        <!doctype html>
        <title>错误</title>
        <h1>无法加载文件列表</h1>
        <p>错误信息: {str(e)}</p>
        <p>存储路径: {app.config['UPLOAD_FOLDER']}</p>
        </html>
        <p><a href='/'>返回上传</a></p>
        '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)