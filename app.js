// 页面元素
const loginPage = document.getElementById('login-page');
const registerPage = document.getElementById('register-page');
const mainPage = document.getElementById('main-page');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const showRegisterBtn = document.getElementById('show-register');
const showLoginBtn = document.getElementById('show-login');
const logoutBtn = document.getElementById('logout-btn');
const uploadBtn = document.getElementById('upload-btn');
const fileUpload = document.getElementById('file-upload');
const filesList = document.getElementById('files-list');
const currentUserSpan = document.getElementById('current-user');

// 状态管理
let currentUser = null;
let files = [];

// 初始化
function init() {
    // 检查是否有登录状态
    checkLoginStatus();

    // 绑定事件
    showRegisterBtn.addEventListener('click', showRegisterPage);
    showLoginBtn.addEventListener('click', showLoginPage);
    loginForm.addEventListener('submit', handleLogin);
    registerForm.addEventListener('submit', handleRegister);
    logoutBtn.addEventListener('click', logout);
    uploadBtn.addEventListener('click', () => fileUpload.click());
    fileUpload.addEventListener('change', handleFileUpload);
}

// 检查登录状态
function checkLoginStatus() {
    const user = localStorage.getItem('currentUser');
    if (user) {
        currentUser = JSON.parse(user);
        showMainPage();
    } else {
        showLoginPage();
    }
}

// 显示登录页面
function showLoginPage() {
    loginPage.classList.add('active');
    registerPage.classList.remove('active');
    mainPage.classList.remove('active');
}

// 显示注册页面
function showRegisterPage() {
    loginPage.classList.remove('active');
    registerPage.classList.add('active');
    mainPage.classList.remove('active');
}

// 显示主页面
function showMainPage() {
    loginPage.classList.remove('active');
    registerPage.classList.remove('active');
    mainPage.classList.add('active');

    // 更新当前用户信息
    currentUserSpan.textContent = `欢迎, ${currentUser.username}`;

    // 加载文件列表
    loadFiles();
}

// 处理登录
function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    // 从本地存储获取用户数据
    const users = JSON.parse(localStorage.getItem('users') || '[]');
    console.log('用户列表:', users);
    console.log('尝试登录的用户名:', username);
    
    const user = users.find(u => u.username === username && u.password === password);

    if (user) {
        currentUser = user;
        localStorage.setItem('currentUser', JSON.stringify(user));
        showMainPage();
    } else {
        // 检查是否存在用户名相同但密码不同的情况
        const existingUser = users.find(u => u.username === username);
        if (existingUser) {
            console.log('用户名存在，但密码不匹配');
            alert('密码错误，请重新输入');
        } else {
            console.log('用户名不存在');
            alert('用户名不存在，请先注册');
        }
    }
}

// 处理注册
function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm-password').value;

    // 验证密码
    if (password !== confirmPassword) {
        alert('两次输入的密码不一致');
        return;
    }

    // 从本地存储获取用户数据
    const users = JSON.parse(localStorage.getItem('users') || '[]');

    // 检查用户名是否已存在
    if (users.some(u => u.username === username)) {
        alert('用户名已存在');
        return;
    }

    // 创建新用户
    const newUser = { username, password };
    users.push(newUser);

    // 保存到本地存储
    localStorage.setItem('users', JSON.stringify(users));

    // 自动登录
    currentUser = newUser;
    localStorage.setItem('currentUser', JSON.stringify(newUser));

    showMainPage();
}

// 退出登录
function logout() {
    currentUser = null;
    localStorage.removeItem('currentUser');
    showLoginPage();
}

// 处理文件上传
function handleFileUpload() {
    const selectedFiles = fileUpload.files;
    if (selectedFiles.length === 0) return;

    // 从本地存储获取文件数据
    files = JSON.parse(localStorage.getItem(`files_${currentUser.username}`) || '[]');

    for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i];

        // 检查文件是否已存在
        if (files.some(f => f.name === file.name && f.size === file.size)) {
            alert(`文件 ${file.name} 已存在`);
            continue;
        }

        // 创建文件对象
        const fileObj = {
            id: Date.now() + i,
            name: file.name,
            size: file.size,
            type: file.type,
            date: new Date().toISOString()
        };

        files.push(fileObj);

        // 模拟上传进度
        // 实际应用中，这里应该有一个真实的上传过程
    }

    // 保存文件数据
    localStorage.setItem(`files_${currentUser.username}`, JSON.stringify(files));

    // 重新加载文件列表
    loadFiles();

    // 重置文件输入
    fileUpload.value = '';
}

// 加载文件列表
function loadFiles() {
    // 从本地存储获取文件数据
    files = JSON.parse(localStorage.getItem(`files_${currentUser.username}`) || '[]');

    // 清空文件列表
    filesList.innerHTML = '';

    // 没有文件时显示提示
    if (files.length === 0) {
        filesList.innerHTML = '<p class="no-files">暂无文件，请上传文件</p>';
        return;
    }

    // 渲染文件列表
    files.forEach(file => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';

        // 确定文件图标
        let iconClass = 'file-icon';
        if (file.type.startsWith('image/')) {
            iconClass += ' file-image';
        } else if (file.type.startsWith('video/')) {
            iconClass += ' file-video';
        } else if (file.type.startsWith('audio/')) {
            iconClass += ' file-audio';
        } else if (file.type.includes('pdf')) {
            iconClass += ' file-pdf';
        } else if (file.type.includes('text') || file.name.endsWith('.txt')) {
            iconClass += ' file-text';
        } else {
            iconClass += ' file-generic';
        }

        // 格式化文件大小
        let sizeText = '';
        if (file.size < 1024) {
            sizeText = `${file.size} B`;
        } else if (file.size < 1024 * 1024) {
            sizeText = `${(file.size / 1024).toFixed(2)} KB`;
        } else {
            sizeText = `${(file.size / (1024 * 1024)).toFixed(2)} MB`;
        }

        // 格式化日期
        const date = new Date(file.date);
        const dateText = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;

        fileItem.innerHTML = `
            <div class="${iconClass}">📄</div>
            <div class="file-name">${file.name}</div>
            <div class="file-size">${sizeText}</div>
            <div class="file-date">${dateText}</div>
            <div class="file-actions">
                <button class="btn btn-secondary download-btn" data-id="${file.id}">下载</button>
                <button class="btn btn-secondary delete-btn" data-id="${file.id}">删除</button>
            </div>
        `;

        filesList.appendChild(fileItem);
    });

    // 绑定下载和删除事件
    document.querySelectorAll('.download-btn').forEach(btn => {
        btn.addEventListener('click', handleDownload);
    });

    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', handleDelete);
    });
}

// 处理文件下载
function handleDownload(e) {
    const fileId = parseInt(e.target.getAttribute('data-id'));
    const file = files.find(f => f.id === fileId);

    if (file) {
        // 创建一个临时的blob对象和URL
        // 注意：这里只是模拟下载，实际应用中应该从服务器获取文件
        const blob = new Blob(['这是一个模拟的文件内容。在实际应用中，这里应该是真实的文件内容。'], {
            type: file.type
        });
        const url = URL.createObjectURL(blob);

        // 创建一个临时的a标签来触发下载
        const a = document.createElement('a');
        a.href = url;
        a.download = file.name;
        document.body.appendChild(a);
        a.click();

        // 清理
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 0);

        alert(`开始下载文件: ${file.name}`);
    }
}

// 处理文件删除
function handleDelete(e) {
    const fileId = parseInt(e.target.getAttribute('data-id'));

    if (confirm('确定要删除这个文件吗？')) {
        // 过滤掉要删除的文件
        files = files.filter(f => f.id !== fileId);

        // 保存文件数据
        localStorage.setItem(`files_${currentUser.username}`, JSON.stringify(files));

        // 重新加载文件列表
        loadFiles();
    }
}

// 启动应用
init();