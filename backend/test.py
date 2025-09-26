import asyncio
import time
import httpx
import statistics
import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings

# ====== 配置 ======
BASE_URL = "http://127.0.0.1:8000/api/v1"  # 改成你的 FastAPI 地址
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
USER_ID = "37370a26-accc-4537-a6a9-c3f1e263f7ad"
EXPIRE_MINUTES = 60

# ====== 生成测试 Token ======
def generate_test_token(user_id: str = USER_ID, expire_minutes: int = EXPIRE_MINUTES):
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode = {"exp": expire, "sub": user_id}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

AUTH_TOKEN = generate_test_token()

HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}

# ----------- 压测函数 -----------

async def test_llm_generate(client: httpx.AsyncClient, idx: int):
    url = f"{BASE_URL}/conversations/generate"
    payload = {
        "name": f"测试角色{idx}",
        "character_type": "虚拟角色",
        "background": "这是一个测试背景"
    }
    return await send_request(client, url, payload)


async def test_stt(client: httpx.AsyncClient, idx: int):
    url = f"{BASE_URL}/stt/transcribe"
    payload = {
        "audio_url": "https://dashscope.oss-cn-beijing.aliyuncs.com/samples/audio/asr_example.wav"
    }
    return await send_request(client, url, payload)


async def test_tts(client: httpx.AsyncClient, idx: int):
    url = f"{BASE_URL}/tts/synthesize"
    payload = {
        "text": f"这是第 {idx} 条测试语音。",
        "voice": "Cherry"
    }
    return await send_request(client, url, payload)


# ----------- 公共函数 -----------

async def send_request(client: httpx.AsyncClient, url: str, payload: dict):
    start = time.perf_counter()
    try:
        resp = await client.post(url, headers=HEADERS, json=payload, timeout=60)
        duration = time.perf_counter() - start
        return resp.status_code, duration
    except Exception as e:
        return f"error: {e}", 0


async def run_benchmark(test_fn, num_requests: int, concurrency: int):
    results = []
    async with httpx.AsyncClient() as client:
        semaphore = asyncio.Semaphore(concurrency)

        async def bound_task(i):
            async with semaphore:
                return await test_fn(client, i)

        tasks = [bound_task(i) for i in range(num_requests)]
        for r in await asyncio.gather(*tasks):
            results.append(r)

    analyze_results(results, num_requests)


def analyze_results(results, num_requests):
    durations = [d for code, d in results if isinstance(code, int) and code == 200]
    errors = [code for code, _ in results if not (isinstance(code, int) and code == 200)]

    success_count = len(durations)
    fail_count = num_requests - success_count

    avg_time = statistics.mean(durations) if durations else 0
    p95_time = statistics.quantiles(durations, n=20)[18] if len(durations) >= 20 else 0
    total_time = sum(durations)
    qps = success_count / total_time if total_time > 0 else 0

    print("\n===== 压测结果 =====")
    print(f"总请求数: {num_requests}")
    print(f"成功数: {success_count}, 失败数: {fail_count}")
    print(f"平均响应时间: {avg_time:.2f} 秒")
    print(f"P95 响应时间: {p95_time:.2f} 秒")
    print(f"整体 QPS: {qps:.2f}")
    if errors:
        print(f"错误示例: {errors}")


# ----------- 入口 -----------

if __name__ == "__main__":
    service = "llm"   # 改成 "stt" 或 "tts"
    num_requests = 50  # 总请求数
    concurrency = 10   # 并发数

    if service == "llm":
        asyncio.run(run_benchmark(test_llm_generate, num_requests, concurrency))
    elif service == "stt":
        asyncio.run(run_benchmark(test_stt, num_requests, concurrency))
    elif service == "tts":
        asyncio.run(run_benchmark(test_tts, num_requests, concurrency))
