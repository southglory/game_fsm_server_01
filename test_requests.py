import asyncio
import httpx
from datetime import datetime
from zoneinfo import ZoneInfo


async def send_event(client: httpx.AsyncClient, machine_type: str, entity_id: str, event_name: str, metadata: dict = None):
    if metadata is None:
        metadata = {}

    response = await client.post(
        f"http://localhost:8000/fsm/machines/{machine_type}/entities/{entity_id}/events", json={"name": event_name, "timestamp": datetime.now(ZoneInfo("UTC")).isoformat(), "metadata": metadata}
    )
    return response.json()


async def quest_flow(client: httpx.AsyncClient, player_id: str):
    # 퀘스트 시작
    print(f"\n플레이어 {player_id} 퀘스트 시작...")
    result = await send_event(client, "quest", player_id, "start", {"quest_name": f"플레이어 {player_id}의 퀘스트", "difficulty": "normal"})
    print(f"플레이어 {player_id} 시작 결과:", result)

    # 잠시 대기
    await asyncio.sleep(1)

    # 50% 확률로 성공 또는 실패
    import random

    if random.random() > 0.5:
        print(f"\n플레이어 {player_id} 퀘스트 완료!")
        result = await send_event(client, "quest", player_id, "complete", {"completion_time": "1h 30m", "score": 95})
    else:
        print(f"\n플레이어 {player_id} 퀘스트 실패!")
        result = await send_event(client, "quest", player_id, "fail", {"reason": "동전 던져서 50% 확률 실패", "progress": 75})

        # 실패한 경우 재시도
        await asyncio.sleep(1)
        print(f"\n플레이어 {player_id} 퀘스트 재시도!")
        result = await send_event(client, "quest", player_id, "retry", {"attempt_count": 2})

    print(f"플레이어 {player_id} 최종 상태:", result)


async def main():
    async with httpx.AsyncClient() as client:
        # 5명의 플레이어가 동시에 퀘스트 진행
        players = [f"player_{i}" for i in range(1, 6)]
        tasks = [quest_flow(client, player_id) for player_id in players]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
