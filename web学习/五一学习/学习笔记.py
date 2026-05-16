from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="我的静态网页")

# 方式A：推荐 - 把整个静态目录挂载到根路径，让 / 直接访问 index.html
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# 如果你想把静态文件挂载到 /static 下（更常见于前后端分离）
# app.mount("/static", StaticFiles(directory="static", html=True), name="static")


# ----------------- 注释 -----------------
# 上面是fastapi如何提供页面给用户访问

# 如何启动fastapi
# 1. 安装fastapi和uvicorn
#    pip install fastapi uvicorn
# 2. 启动服务器
#    uvicorn main:app --reload
# 3. 在浏览器访问 http://localhost:8000
# 4. 你应该能看到 static/index.html 的内容被展示出来了

# 我要通过自己的电脑ip可以访问，启动方式为：
#    uvicorn main:app --reload --host 0.0.0.0 --port 8000