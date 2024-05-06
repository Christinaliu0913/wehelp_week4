from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
# 初始化Jinja2
templates = Jinja2Templates(directory="templates")

#middleware
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# 定義用戶狀態的鍵
USER_STATE_KEY = "SIGNED-IN"

#登入時
def user_logged_in(req:Request):
    req.session[USER_STATE_KEY]=True

#登出時
def user_logger_out(req:Request):
    req.session.pop(USER_STATE_KEY,None)


#檢查用戶是否登入
def check_log(req:Request):
    return req.session.get(USER_STATE_KEY,False)

# 首頁
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

#登入驗證
@app.post("/signin")
async def signin_post(req: Request, username: str = Form(default=""), password: str = Form(default=""), agreement: bool=Form(default='')):
    if not agreement:
        return RedirectResponse(url="/", status_code=303)#避免重複提交表單數據，303 See Other 表示原始請求已經被處理完成，客户端應該重新定向，並使用 GET 方法來獲取重定向後的資源。
    if not username or not password:
        return RedirectResponse(url="/error?message=請輸入帳號或密碼", status_code=303)
    if username != "test" or password != "test":
        return RedirectResponse(url="/error?message=您的帳號或密碼不正確", status_code=303)
    user_logged_in(req)
    return RedirectResponse(url="/member", status_code=303) 
    


# 顯示不同錯誤的消息
@app.get("/error", response_class=HTMLResponse)
async def error(req: Request, message: str = None):
    return templates.TemplateResponse("error.html", {"request": req, "message": message})



# 會員頁面限制只有登入狀態才行登入
@app.get("/member", response_class=HTMLResponse)
async def member(req: Request): 
    session = req.session
    if not session.get(USER_STATE_KEY, False):
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("member.html", {"request": req})


#退出登入
@app.get('/signout',response_class=HTMLResponse)
async def signout( req: Request):
    user_logger_out(req)
    return RedirectResponse(url='/',status_code=303)



# 讓termial run python main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
