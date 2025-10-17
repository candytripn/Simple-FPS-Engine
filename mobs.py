class mob:
    def __init__(self, name, health, attack):
        self.name = name
        self.health = health
        self.attack = attack

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def is_alive(self):
        return self.health > 0
    def attack_player(self, player):
        player.health -= self.attack
        if player.health < 0:
            player.health = 0
    def __str__(self):
        return f"{self.name} (Health: {self.health}, Attack: {self.attack})"
# Example mobss