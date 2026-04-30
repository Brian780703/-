import httpx
import asyncio
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="比價馬拉松-商用引擎")

# 讓網頁可以順利讀取資料
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 你的專屬賺錢設定 ---
CONFIG = {
    "API_KEY": "2OcskKTaftA0s1QiNz",
    "MEMBER_ID": "af000148608",
    "ENDPOINT": "https://api.ichannels.com.tw/v1/products"
}

@app.get("/api/compare")
async def compare_api(q: str = Query(..., description="搜尋關鍵字")):
    params = {
        "apikey": CONFIG["API_KEY"],
        "member_id": CONFIG["MEMBER_ID"],
        "keyword": q,
        "sort": "price_asc",
        "limit": 12
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(CONFIG["ENDPOINT"], params=params, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                # 取得商品列表
                raw_items = data.get('data', [])
                
                clean_results = []
                for item in raw_items:
                    clean_results.append({
                        "name": item.get('name'),
                        "price": int(item.get('price', 0)),
                        "platform": item.get('site_name', '合作電商'),
                        "link": item.get('url'), # 通路王 API 會自動把網址轉成帶有 af000148608 的分潤連結
                        "image": item.get('image_url')
                    })
                return {"status": "success", "results": clean_results}
            return {"status": "error", "message": "API 請求失敗"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
