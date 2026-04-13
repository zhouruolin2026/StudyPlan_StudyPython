from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    # host="0.0.0.0" 表示监听所有网卡，局域网内其他设备可以访问
    uvicorn.run(app, host="0.0.0.0", port=8000)


# 方式一：直接运行 py 文件
# python main.py

# 方式二：用 uvicorn 命令（推荐，支持热重载）
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload