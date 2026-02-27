def finger_states(hand):
    tips = [4, 8, 12, 16, 20]
    states = []

    for tip in tips[1:]:
        states.append(
            1 if hand.landmark[tip].y < hand.landmark[tip - 2].y else 0
        )
    states.insert(0, 0)  # Thumb simplified
    return states

