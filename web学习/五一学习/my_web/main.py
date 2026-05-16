from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="我的多页面网站")

# 把整个 static 文件夹挂载到根路径 /
app.mount("/", StaticFiles(directory="static", html=True), name="static")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


# uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# 访问 http://localhost:8000 就能看到 static/index.html 的内容了