from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="局域网静态网页服务")

# 把整个 static 文件夹挂载到根路径 /
# html=True 表示访问 / 时自动返回 index.html
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# （可选）如果你以后想加纯 API 接口，可以继续写在这里
# @app.get("/api/hello")
# async def hello():
#     return {"message": "你好！这是后端返回的 JSON"}