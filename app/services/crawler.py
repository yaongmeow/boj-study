import requests

BASE_URL = "https://solved.ac/api/v3"

def has_solved_problem(boj_id: str, problem_id: str) -> bool:
    """
    solved.ac API를 이용해 특정 BOJ ID가 문제를 풀었는지 확인
    """
    url = f"{BASE_URL}/search/problem?query=solved_by:{boj_id}+id:{problem_id}"
    resp = requests.get(url)

    if resp.status_code != 200:
        print(f"[ERROR] API 요청 실패: {resp.status_code}")
        return False

    data = resp.json()
    return len(data.get("items", [])) > 0