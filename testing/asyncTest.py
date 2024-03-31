import asyncio

async def task():
    for i in range(10):
        print(f"Iteration {i}")
        await asyncio.sleep(0)

async def main():
    asyncTask = asyncio.create_task(task())
    
    for i in range(10):
        print(f"Main loop {i}")
        await asyncio.sleep(0)
    

asyncio.run(main())
