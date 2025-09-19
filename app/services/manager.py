from .crawler import has_solved_problem

def update_penalties(study: dict):
    """
    스터디의 모든 멤버 벌금을 업데이트한다.
    """
    for member in study["members"]:
        all_solved = True
        for pid in member["problems"]:
            if not has_solved_problem(member["boj_id"], pid):
                all_solved = False
                break

        if all_solved:
            member["penalty"] = 0
        else:
            if member["penalty"] == 0:
                member["penalty"] = 2000
            else:
                member["penalty"] = min(member["penalty"] + 1000, 5000)
