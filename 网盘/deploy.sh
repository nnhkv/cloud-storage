#!/bin/bash

# 检查Heroku CLI是否安装
if ! command -v heroku &> /dev/null
then
    echo "正在安装Heroku CLI..."
    curl https://cli-assets.heroku.com/install.sh | sh
fi

echo "正在检查Heroku API密钥..."
if [ -z "$HEROKU_API_KEY" ]; then
  echo "错误: 未设置HEROKU_API_KEY环境变量"
  echo "请先设置API密钥: export HEROKU_API_KEY=你的密钥"
  exit 1
fi
heroku login -i <<< "$HEROKU_API_KEY"

# 创建Heroku应用
heroku create

# 推送代码到Heroku
git push heroku main

# 打开应用
heroku open