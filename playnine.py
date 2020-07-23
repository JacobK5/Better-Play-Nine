from random import shuffle, choice

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

    def unflipped_locations(self):
        unflipped = []
        for col in range(4):
            for row in range(2):
                if self.cards[col][row].visible_value == "F":
                    unflipped.append((col, row))
        return unflipped

    def get_state(self, col):
        if self.cards[col][0].visible_value == "F" and self.cards[col][1].visible_value == "F":
            return Board.NEITHER_FLIPPED
        elif self.cards[col][0].visible_value == "F" or self.cards[col][1].visible_value == "F":
            return Board.ONE_FLIPPED
        elif self.cards[col][0].value == self.cards[col][1].value:
            return Board.BOTH_MATCH
        else:
            return Board.BOTH_FLIPPED

    def get_score(self):
        score = 0
        matches = []
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
        col, row = choice(self.board.unflipped_locations())
        self.card_discarded = self.board.cards[col][row]
        self.card_discarded.flip()
        self.board.cards[col][row] = drawn
        return self.board.all_flipped()

    def take_last_turn(self, deck, discarded):
        self.take_turn(deck, discarded)

    def check_card(self, card):
        #will need later
        pass
        


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
