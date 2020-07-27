from random import shuffle, choice, random, uniform #uniform is used as uniform(5,10) 5 can be chosen, 10 cant but 9.9999 can

"""
general plan:
- card class, simple
- deck class, also simple
- board class, (no pair class)
- player class
- game class
- maybe a population class, not sure though
- training class
"""

class Card():
	#A simple card, it just has a value
    def __init__(self, value):
        self.value = value
        self.visible_value = "F"

    def flip(self):
        self.visible_value = self.value

    def copy(self):
        c = Card(self.value)
        c.visible_value = self.visible_value
        return c

class Deck():
	#A deck, which is just a list of cards
    def __init__(self):
        self.cards = []
        self.fill_deck()
        self.shuffle()

    def fill_deck(self):
        for i in range(13):
            for j in range(7):
                self.cards.append(Card(i))
        for i in range(3):
            self.cards.append(Card(-5))

    def shuffle(self):
        shuffle(self.cards)

    def print(self):
        for card in self.cards:
            print(card.value)

    def draw(self):
        self.cards[0].flip()
        return self.cards.pop(0)

    def draw_face_down(self):
        return self.cards.pop(0)



class Board():

    NEITHER_FLIPPED = 0
    ONE_FLIPPED = 1
    BOTH_FLIPPED = 2
    BOTH_MATCH = 3

    def __init__(self):
        self.cards = []
        self.fill_blank()

    def fill_blank(self):
        for col in range(4):
            inner = []
            for row in range(2):
                inner.append(Card(69))
            self.cards.append(inner)

    def print(self):
        for row in range(2):
            for col in range(4):
                if isinstance(self.cards[col][row].visible_value, str):
                    print(" F", end = " ")
                else:
                    print("{:2}".format(self.cards[col][row].visible_value), end = " ")
            print("")
    
    def flip_all(self):
        for col in range(4):
            for row in range(2):
                self.cards[col][row].flip()

    def all_flipped(self):
        for col in range(4):
            for row in range(2):
                if self.cards[col][row].visible_value != self.cards[col][row].value:
                    return False
        return True

    def get_unflipped_locations(self):
        unflipped = []
        for col in range(4):
            for row in range(2):
                if self.cards[col][row].visible_value == "F":
                    unflipped.append((col, row))
        return unflipped

    def get_unmatched(self):
        unmatched = []
        for col in range(4):
            if self.get_state[col] == Board.ONE_FLIPPED or self.get_state[col] == Board.BOTH_FLIPPED:
                for row in range(2):
                    if self.cards[col][row].visible_value != "F":
                        unmatched.append(self.cards[col][row].visible_value)
        return unmatched

    def get_highest_unmatched(self):
        return max(self.unmatched())

    def get_location(self, card_val):
        for col in range(4):
            for row in range(2):
                if self.get_state(col) != Board.BOTH_MATCH and self.get_state(col) != Board.NEITHER_FLIPPED:
                    if self.cards[col][row].visible_value == card_val
                    return (col, row)

    def get_unflipped(self, col):
        if self.get_state(col) != Board.ONE_FLIPPED:
            return -1
        if self.cards[col][0].visible_value == "F":
            return 0
        else:
            return 1

    def get_matches(self):
        matches = []
        for col in range(4):
            if self.get_state(col) == Board.BOTH_MATCH:
                matches.append(self.cards[col][0])
        return matches

    def get_state(self, col):
        if self.cards[col][0].visible_value == "F" and self.cards[col][1].visible_value == "F":
            return Board.NEITHER_FLIPPED
        elif self.cards[col][0].visible_value == "F" or self.cards[col][1].visible_value == "F":
            return Board.ONE_FLIPPED
        elif self.cards[col][0].value == self.cards[col][1].value:
            return Board.BOTH_MATCH
        elif (self.cards[col][0].value == 0 or self.cards[col][0] == -5) and (self.cards[col][1].value == 0 or self.cards[col][1] == -5)
            return Board.BOTH_MATCH #makes joker and 0 count as a match
        else:
            return Board.BOTH_FLIPPED

    def get_score(self):
        score = 0
        matches = [] #could probably use new matches function here
        for i in range(4):
            if self.get_state(i) == Board.BOTH_FLIPPED:
                score += self.cards[i][0].value + self.cards[i][1].value
            elif self.get_state(i) == Board.BOTH_MATCH:
                if self.cards[i][0].value == -5:
                    score -= 10
                matches.append(self.cards[i][0].value)
        for val in matches:
            if matches.count(val) > 1:
                for i in range(matches.count(val)):
                    matches.remove(val)
                    score -= 5
        return score


class DNA():
    def __init__(self):
        """
        the traits, (not) in order, are:
        horizontal or vertical: if it prefers flipping with a flipped card or a new col
        lowest to take (from discard): lowest number it will take from the discard pile (maybe only if there is an unflipped col)
        draw bias: how often it'll take the card if its low enough vs draw a new one (maybe these should be combined in a formula)
        lowest to keep: from drawing
        when to start mitigating (based on opponents number of unflipped cards)
        lowest to mitigate: lowest amount you need to save for it to mitigate
        joker placement: if joker goes in new spot or replaces a flipped card
        higest card to go for -10 with
        when to stop going for -10 (maybe could be linked with above, make one formula that determines if -10 is worth it later on)
        draw card that doesnt match and is low, replace flipped card or put it with a flipped card or discard
        
        """
        genes = []


class Player():
    #Layout for a player, by default is a computer player
    def __init__(self):
        self.board = Board()
        self.card_discarded = None
        #something to hold the brains/logic
        #logic will be randomized by default and can be set after

    def flip_two(self):
        #will always flip this one
        self.board.cards[0][0].flip()
        #later this one will be determined by the logic
        self.board.cards[0][1].flip()#otherwise is [1][0]

    def take_turn(self, deck, discarded):
        #for now, for testing, will always draw and then put it in a random spot
        drawn = deck.draw()
        print("")
        print("Drew " + str(drawn.visible_value))
        print("")
        col, row = choice(self.board.get_unflipped_locations())
        self.card_discarded = self.board.cards[col][row]
        self.card_discarded.flip()
        self.board.cards[col][row] = drawn
        return self.board.all_flipped()

    def take_last_turn(self, deck, discarded):
        self.take_turn(deck, discarded)

    def check_card(self, card):
        #will need later
        pass

    """
    NOTE: I think it might be best to have all DNA logic be held in one array from DNA class, but as soon as the player is created,
          set the values in the array to their own descriptive variables in the player.
          I can make an iterator from the DNA list using iter(list) then assign each value to next(iterator) and it'll work perfectly
    """
        


class User(Player):
    def __init__(self):
        super(User, self).__init__()

    def flip_two(self):
        col = int(input("Enter col of card to flip ")) - 1
        while col < 0 or col > 3:
            print("Must be between 1 and 4")
            col = int(input("Enter col of card to flip ")) - 1

        row = int(input("Enter row of card to flip ")) - 1
        while row < 0 or row > 1:
            print("Must be between 1 and 2")
            row = int(input("Enter row of card to flip ")) - 1

        col2 = int(input("Enter col of second card to flip ")) - 1
        while col2 < 0 or col2 > 3:
            print("Must be between 1 and 4")
            col2 = int(input("Enter col of card to flip ")) - 1

        row2 = int(input("Enter row of second card to flip ")) - 1
        while row2 < 0 or row2 > 1:
            print("Must be between 1 and 2")
            row2 = int(input("Enter row of card to flip ")) - 1

        while(col == col2 and row == row2):
            print("You need to flip 2 different cards")
            col2 = int(input("Enter col of second card to flip ")) - 1
            while col2 < 0 or col2 > 3:
                print("Must be between 1 and 4")
                col2 = int(input("Enter col of card to flip ")) - 1

            row2 = int(input("Enter row of second card to flip ")) - 1
            while row2 < 0 or row2 > 1:
                print("Must be between 1 and 2")
                row2 = int(input("Enter row of card to flip ")) - 1

        self.board.cards[col][row].flip()
        self.board.cards[col2][row2].flip()

    def take_turn(self, deck, discarded):
        draw_card = input("Enter draw to draw a card, or discard to use the discarded card ")
        while draw_card.lower() != "discard" and draw_card.lower() != "draw":
            print("Invalid input")
            draw_card = input("Enter draw to draw a card, or discard to use the discarded card ")
        if draw_card.lower() == "draw":
            drawn = deck.draw()
            print("You drew " + str(drawn.visible_value))
            keep = input("Do you want to keep the card you drew (enter keep), or flip a card on your board (enter flip)? ")
            while keep.lower() != "keep" and keep.lower() != "flip":
                print("Invalid input")
                keep = input("Do you want to keep the card you drew (enter keep), or flip a card on your board (enter flip)? ")
            if keep.lower() == "keep":
                col = int(input("Enter col of where to put your card ")) - 1
                while col < 0 or col > 3:
                    print("Must be between 1 and 4")
                    col = int(input("Enter col of card to flip ")) - 1

                row = int(input("Enter row of where to put your card ")) - 1
                while row < 0 or row > 1:
                    print("Must be between 1 and 2")
                    row = int(input("Enter row of card to flip ")) - 1

                self.card_discarded = self.board.cards[col][row]
                self.card_discarded.flip()
                self.board.cards[col][row] = drawn
            elif keep.lower() == "flip":
                col = int(input("Enter col of card to flip ")) - 1
                while col < 0 or col > 3:
                    print("Must be between 1 and 4")
                    col = int(input("Enter col of card to flip ")) - 1

                row = int(input("Enter row of card to flip ")) - 1
                while row < 0 or row > 1:
                    print("Must be between 1 and 2")
                    row = int(input("Enter row of card to flip ")) - 1

                self.board.cards[col][row].flip()
                self.card_discarded = drawn
        elif draw_card.lower() == "discard":
            col = int(input("Enter col of where to put your card ")) - 1
            while col < 0 or col > 3:
                print("Must be between 1 and 4")
                col = int(input("Enter col of card to flip ")) - 1

            row = int(input("Enter row of where to put your card ")) - 1
            while row < 0 or row > 1:
                print("Must be between 1 and 2")
                row = int(input("Enter row of card to flip ")) - 1

            self.card_discarded = self.board.cards[col][row]
            self.card_discarded.flip()
            self.board.cards[col][row] = discarded
        return self.board.all_flipped()





class Game():
    #basic game, only with 2 players for now
    def __init__(self, playable, player1 = None, player2 = None):
        self.players = []
        if playable:
            self.players.append(Player())
            self.players.append(User())
        else:
            self.players.append(player1)
            self.players.append(player2)
        self.discard_pile_card = None

    def print_discarded(self):
        print(str(self.discard_pile_card.visible_value) + " F")

    def deal(self, deck):
        for p in self.players:
            for col in range(4):
                for row in range(2):
                    p.board.cards[col][row] = deck.draw_face_down()

    def play(self):
        game_done = False
        for i in range(9):
            play_round()
        end_game()

    def play_round(self):
        #basic setup
        deck = Deck()
        self.deal(deck)
        self.discard_pile_card = deck.draw()
        #start the game
        for p in self.players:
            p.flip_two()
        #variables needed to know the state of the round
        round_over = False
        someone_went_out = False
        last_turn = False
        p_who_went_out = None


        #play each player's turn
        while not round_over:
            for i in range(len(self.players)):
                p = self.players[i]

                if p != p_who_went_out:
                    print("")
                    print("Player " + str(i + 1) + "'s turn")
                    print("")
                    self.print_discarded()
                    print("")
                    p.board.print()

                    if not last_turn:
                        someone_went_out = p.take_turn(deck, self.discard_pile_card)
                        self.discard_pile_card = p.card_discarded
                    else:
                        p.take_last_turn(deck, self.discard_pile_card)
                        self.discard_pile_card = p.card_discarded

                    if someone_went_out and not last_turn:
                        print("Someone went out")
                        p_who_went_out = p
                        last_turn = True
                    print("After the turn:")
                    print("")
                    p.board.print()
                else:
                    round_over = True
                    break
        print("")
        print("The round is over")
        #print the scores
        print("The scores for this round are: ")
        for i in range(len(self.players)):
            print("Player " + str(i + 1) + ": " + str(self.players[i].board.get_score()))



    def end_game(self):
        pass
        #probably just gonna be used to calculate the player's fitness


game = Game(True)
game.play_round()


"""
NOTES:
Should (probably) be 3 stages to the game:
1. Getting one card flipped in each col
2. Filling in board till one card left
3. Finishing the round
Alternatively, if vertical is preferred (would rather place cards in same col as already flipped cards):
Same but without step 1

Logic for each stage:
1. 
a. Check if discard matches a card you're trying to match, if it is match it (obviously)
b. If drawing bias is low enough and it is low enough, or if it is low enough and is same as a match you already 
   have take the discarded card and put it in a new unflipped col
c. Otherwise, draw a card
d. If card drawn matches, put it with the match
e. If it is low enough, or if it is low enough and is same as a match you already have, put it in a new unflipped col
f. Otherwise, flip a card in a new unflipped col
Note: Steps are essentially the same for checking the card, which should be in its own function

2.
a. Check if discard matches a card you're trying to match, if it is match it (obviously) (unless the other card is going for -10 already)
b. If the discard card is same as a match you've already made and it is early enough and it is low enough, take it and replace your highest
   unmatched card if you save enough otherwise put it across from your highest card (tough choice here, plus it makes a tough choice later on
   if you can match the highest card)
c. If discard is low enough and it is late enough and the drawing bias is low, replace highest card with discard (mitigate)
d. If it is low enough and drawing bias is low, place the discarded card with the highest card
e. Otherwise, draw a card
f. Check if it matches a card you're trying to match, if it is match it (obviously) (unless the other card is going for -10 already)
g. If the drawn card is same as a match you've already made and it is early enough and it is low enough, take it and replace your highest
   unmatched card if you save enough otherwise put it across from your highest card (tough choice here, plus it makes a tough choice later on
   if you can match the highest card)
h. If drawn card is low enough and it is late enough, replace highest card with discard (mitigate)
i. If it is low enough and flipping bias is low, place the drawn card with the highest card
j. Otherwise, flip a card across from the highest card

3. 
a. If discard matches an unmatched card that doesn't end the game, match it (duh) (unless the other card is going for -10 already)
b. If the discard matches the card that ends the game, and you'll end with a low enough amount of points, match it
c. If discard is same as a match you have and isn't too much higher than your highest unmatched card and -10 bias is high, replace highest
   unmatched card with discard
d. If discard is lower than your highest unmatched card and it mitigates enough and your drawing bias is low, replace highest card with discard
e. Otherwise, draw a card
f. If drawn card matches an unmatched card that doesn't end the game, match it (duh) (unless the other card is going for -10 already)
g. If the drawn card matches the card that ends the game, and you'll end with a low enough amount of points, match it
h. If drawn card is same as a match you have and isn't too much higher than your highest unmatched card and -10 bias is high, replace highest
   unmatched card with discard
i. If drawn is lower than your highest unmatched card and your highest unmatched card isn't going for -10 if -10 bias is high, replace highest 
   card with discard (need to figure out the math for this step with -10 bias), otherwise replace next highest unmatched card


Variables that each step use (not final):
1.
a. -10 bias, latest you go for -10, lowest for -10 (possibly something else about how much you save, or just factor that into calculation with -10 bias)
b. drawing bias, lowest for -10, lowest to keep
c. None
d. -10 bias, latest you go for -10, lowest for -10 (same as step a)
e. lowest for -10, lowest to keep (same as b but without drawing bias)
f. None

2.
a. -10 bias, latest you go for -10. lowest for -10
b. -10 bias, latest you go for -10. lowest for -10, some kind of mitigation factor and time factor
c. mitigation factor, time factor, drawing bias
d. lowest to keep, drawing bias
e. None
f. -10 bias, latest you go for -10. lowest for -10
g. -10 bias, latest you go for -10. lowest for -10, some kind of mitigation factor and time factor
h. mitigation factor, time factor
i. flipping bias, lowest to keep (maybe should be different from lowest to keep)
j. None

3.
a. -10 bias, latest you go for -10. lowest for -10
b. Lowest to go out with
c. -10 bias, highest you'll gain for -10
d. drawing bias, possibly a new mitigation factor (might just somehow multiply drawing bias by how much you'll save)
e. None
f. -10 bias, latest you go for -10. lowest for -10 (not sure these are exactly what I want here)
g. Lowest to go out with
h. -10 bias, highest you'll gain for -10
i. -10 bias (maybe a different version of it though)


NOTE: Flipping bias is only for flipping across from a flipped card, not flipping a card in a totally unflipped row, since there is definitive mathematical
      logic for taking cards below 5 and not otherwise
NOTE: There should probably be one time factor for anything related to time, and you multiply it by how many unflipped cards your opponent with the
      lowest amount of unflipped cards has left, to determine how much you care about the time left
NOTE: In general, the more variables the better, since some variable values may do well early game but may do not as well in very similar but slightly
      different situations later in the game
NOTE: At all points, if a 0 is drawn and there is an unmatched joker the 0 should be put with the joker

Trying to figure out conditions for each step:
1.
a. Does it match? If yes, match it (in theory this is always replacing a face down card at this point) (including matching joker with 0)
b. If discard is a joker, keep it (in unmatched col). Is discard same as match you already have? If yes, is it low enough to go for -10 (is it lower than 
   lowest for -10 times time multiplier over how many unflipped cards opponent has)? Then keep it, otherwise, if it is lower than lowest to keep and 
   random number btwn 0 and 1 is higher than drawing bias (so that a high drawing bias means you draw more often), keep it
c. Nothing
d. Does it match? If yes, match it
e. Is it same as match you already have? If yes, is it low enough to go for -10 (is it lower than lowest for -10 times time multiplier over how many 
   unflipped cards opponent has), then keep it.


List of all DNA variables:
horizontal_preference (true or false)
drawing_bias (btwn 0 and 1)
flipping_bias (btwn 0 and 1)
minus10_bias (btwn 0 and 1)
time_multiplier (btwn 1 and 10) - might need to be slightly different
lowest_to_keep (btwn 0 and 12)
lowest_for_minus10 (btwn 0 and 12)
lowest_to_go_out_with (btwn 0 and 10) - eventually will be based on opponents boards too





Time multiplier:

Opponent can have between 6 and 1 cards unflipped. 1 over these gives a range from 0.16 to 1. Maybe it can work like time multiplier over cards unflipped
is how much you subtract from lowest to keep (normal and -10), and lowest youll mitigate to save



Should put joker logic here seperately (since it can be handled seperately in an initial if statement when checking a card):


"""