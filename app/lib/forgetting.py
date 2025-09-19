from datetime import datetime, timedelta
import math

LAMBDA = 0.35
THETA  = 0.4

def decay(s: float, days: float, lam=LAMBDA):
    return s * math.exp(-lam * max(days, 0))

def review_boost(s: float, alpha=0.6):
    return min(1.0, s + alpha*(1.0 - s))

def update_fish_state(fish, now: datetime, reviewed_today: bool):
    days = (now - fish.last_update).total_seconds()/86400
    s = decay(fish.s, days)
    if reviewed_today:
        s = review_boost(s)

    health = max(0, min(100, round(100*s)))
    status = 'dead' if health == 0 else ('weak' if health < 30 else 'alive')
    weight = fish.weight_g + (5 if reviewed_today else -2)
    weight = max(50, weight)

    # 次回due（しきい値THETAを下回る前）
    next_days = max(1, round(-math.log(THETA/max(s,1e-6)) / LAMBDA))
    next_due = now + timedelta(days=next_days)

    fish.s = s; fish.health = health; fish.status = status
    fish.weight_g = weight; fish.last_update = now; fish.next_due = next_due
    return fish
