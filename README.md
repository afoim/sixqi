# 六子棋游戏

这是一个基于Python和WebSocket的在线六子棋游戏。游戏支持两名玩家在线对战，采用19x19的标准棋盘。

## 游戏规则

1. 使用19x19的标准棋盘
2. 黑棋先手，第一步只能下一子
3. 之后双方轮流每步下两子
4. 无禁手规则，允许长连
5. 任意一方先连成6子（或以上）即获胜

## 技术特点

- 前端：HTML5 Canvas + WebSocket
- 后端：Python Flask + Flask-SocketIO
- 实时多人对战支持
- 响应式游戏界面

## 安装说明

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行服务器：
```bash
python server.py
```

3. 访问游戏：
- 打开浏览器
- 访问 http://localhost:5000
- 等待对手加入即可开始游戏

## 游戏操作

1. 第一位进入游戏的玩家将使用黑子
2. 第二位进入的玩家将使用白子
3. 点击棋盘交叉点放置棋子
4. 游戏界面会实时显示当前轮到谁下子
5. 一方胜利后游戏自动结束并显示获胜方