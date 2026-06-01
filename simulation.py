from collections import Counter
from cards import Card, Deck
from evaluator import HandEvaluator

def run_simulation(num_trials=10000):
    deck = Deck()
    evaluator = HandEvaluator()

    results = Counter()

    for _ in range(num_trials):
        deck.reset()

        cards = deck.draw(7)

        best_hand = evaluator.best_rank(cards)

        results[best_hand.category] += 1

    return results
    
def print_results(results, num_trials):
    print("\nPoker Hand Probability Simulation\n")
    print(f"Total simulations: {num_trials}\n")

    for category in results:
        probability = (results[category] / num_trials)
        print(f"{category.name:<20} {probability * 100:.2f}%")


        
def main():
    num_trials = 10000
     
    results = run_simulation(num_trials)
    print_results(results, num_trials)

if __name__ == "__main__":
    main()
