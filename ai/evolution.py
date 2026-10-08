import random


class EvolutionEngine:
    """Handles creature evolution, mutation, and selection."""

    MUTATION_RATE = 0.15
    MUTATION_RANGE = 15
    TRAIT_MIN = 1
    TRAIT_MAX = 100

    TRAIT_KEYS = ['speed', 'strength', 'intelligence', 'agility', 'stamina']

    @classmethod
    def mutate(cls, value, rate=None, range_=None):
        rate = rate if rate is not None else cls.MUTATION_RATE
        range_ = range_ if range_ is not None else cls.MUTATION_RANGE
        if random.random() < rate:
            value += random.randint(-range_, range_)
        return max(cls.TRAIT_MIN, min(cls.TRAIT_MAX, value))

    @classmethod
    def evolve(cls, parent_traits, mutation_rate=None, mutation_range=None):
        offspring = {}
        for key in cls.TRAIT_KEYS:
            offspring[key] = cls.mutate(
                parent_traits.get(key, 50),
                rate=mutation_rate,
                range_=mutation_range
            )
        return offspring

    @classmethod
    def crossover(cls, traits_a, traits_b):
        child = {}
        for key in cls.TRAIT_KEYS:
            a = traits_a.get(key, 50)
            b = traits_b.get(key, 50)
            blend = random.uniform(0, 1)
            child[key] = int(a * blend + b * (1 - blend))
        return child

    @classmethod
    def evaluate(cls, traits):
        return round(
            traits.get('speed', 0) * 0.20 +
            traits.get('strength', 0) * 0.25 +
            traits.get('intelligence', 0) * 0.25 +
            traits.get('agility', 0) * 0.15 +
            traits.get('stamina', 0) * 0.15,
            2
        )

    @classmethod
    def simulate_environment(cls, traits):
        base = cls.evaluate(traits)
        env_bonus = random.uniform(-5, 5)
        return round(max(0, base + env_bonus), 2)

    @classmethod
    def describe_mutation(cls, old_traits, new_traits):
        changes = []
        for key in cls.TRAIT_KEYS:
            old_v = old_traits.get(key, 0)
            new_v = new_traits.get(key, 0)
            diff = new_v - old_v
            if diff != 0:
                sign = '+' if diff > 0 else ''
                changes.append(f"{key}: {old_v} \u2192 {new_v} ({sign}{diff})")
        return changes