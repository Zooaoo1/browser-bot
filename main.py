from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from playwright.async_api import async_playwright
import os

app = FastAPI()

# গ্লোবাল ভেরিয়েবল
playwright_instance = None
browser_instance = None
page_instance = None

class Command(BaseModel):
    action: str  # navigate, click, type, get_text, screenshot
    url: str = ""
    selector: str = ""
    text: str = ""

async def init_browser():
    global playwright_instance, browser_instance, page_instance
    if playwright_instance is None:
        playwright_instance = await async_playwright().start()
        browser_instance = await playwright_instance.chromium.launch(headless=True)
        context = await browser_instance.new_context()
        page_instance = await context.new_page()
    return True

@app.post("/execute")
async def execute_command(cmd: Command):
    try:
        await init_browser()
        
        if cmd.action == "navigate":
            await page_instance.goto(cmd.url)
            return {"status": "success", "message": f"Navigated to {cmd.url}"}
            
        elif cmd.action == "click":
            await page_instance.click(cmd.selector)
            return {"status": "success", "message": f"Clicked {cmd.selector}"}
            
        elif cmd.action == "type":
            await page_instance.fill(cmd.selector, cmd.text)
            return {"status": "success", "message": f"Typed '{cmd.text}' in {cmd.selector}"}
            
        elif cmd.action == "get_text":
            text = await page_instance.inner_text(cmd.selector)
            return {"status": "success", "data": text}
            
        elif cmd.action == "screenshot":
            path = "capture.png"
            await page_instance.screenshot(path=path)
            return {"status": "success", "path": path}
            
        else:
            raise HTTPException(status_code=400, detail="Unknown action")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
