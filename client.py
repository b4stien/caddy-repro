import asyncio
import time

import httpx

BASE_URL = "http://localhost:8010"


async def client_get(client, client_get_args, client_get_kwargs):
    start_time = time.time()
    response = await client.get(*client_get_args, **client_get_kwargs)
    return response.status_code, int(time.time() - start_time)


async def two_gets():
    async with httpx.AsyncClient(http2=True) as client:
        tasks = [
            asyncio.create_task(client_get(client, [f"{BASE_URL}/ok-1s"], {"timeout": 180})) for _ in range(2)
        ]
        results = await asyncio.gather(*tasks)

    if set([r[0] for r in results]) == {200}:
        return True
    return False


LOOP = 20

async def main():
    both_gets_ok_count = 0

    for i in range(LOOP):
        start_time = time.time()
        success = await two_gets()
        iteration_time = int(time.time() - start_time)
        if success:
            both_gets_ok_count += 1
            print(f"Success (iteration {i} - {iteration_time}s)")
        else:
            print(f"Failure (iteration {i} - {iteration_time}s)")

        time.sleep(.5)

    print(f"{both_gets_ok_count} success(es), {LOOP-both_gets_ok_count} failure(s)")


asyncio.run(main())
