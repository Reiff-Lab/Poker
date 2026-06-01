from player import Player

player = Player("Test Player", 100)

paid = player.all_in()

print("paid:", paid)
print("chips:", player.chips)
print("current_bet:", player.current_bet)
print("folded:", player.folded)
print("active:", player.active)
print("can_act:", player.can_act)