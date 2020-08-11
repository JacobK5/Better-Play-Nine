from random import shuffle, choice, random, randint #randint is used as randint(5,10) 5 and 10 can be chosen
import tkinter as tk
from tkinter import filedialog
import win32gui
import win32con
import win32com
import win32com.client
import re


debugging = False
print_drawn = debugging

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
            for j in range(8):
                self.cards.append(Card(i))
        for i in range(4):
            self.cards.append(Card(-5))

    def shuffle(self):
        shuffle(self.cards)

    def print(self):
        for card in self.cards:
            print(card.value)

    def draw(self):
        self.cards[0].flip()
        if print_drawn:
            print("Drew " + str(self.cards[0].visible_value))
        return self.cards.pop(0)

    def draw_face_down(self):
        return self.cards.pop(0)

    def remove_card(self, val):
        for c in self.cards:
            if c.value == val:
                self.cards.remove(c)
                break



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

    def copy(self):
        new_board = Board()
        for col in range(4):
            for row in range(2):
                new_board.cards[col][row] = self.cards[col][row]
        return new_board
    
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
            if self.get_state(col) == Board.ONE_FLIPPED or self.get_state(col) == Board.BOTH_FLIPPED:
                for row in range(2):
                    if self.cards[col][row].visible_value != "F":
                        unmatched.append(self.cards[col][row].visible_value)
        # if debugging:
        #     print("get unmatched called, it returned:")
        #     print(unmatched)
        return unmatched

    def get_highest_unmatched(self):
        if len(self.get_unmatched()) > 0:
            return max(self.get_unmatched())
        else: 
            return None

    def get_across_from_highest(self):
        highest = -6
        location = None
        realrow = None
        valrow = None
        for col in range(4):
            if self.get_state(col) == Board.ONE_FLIPPED:
                for row in range(2):
                    if self.cards[col][row].visible_value == "F":
                        realrow = row
                    else:
                        valrow = row #this is stupid but I think it should work
                val = self.cards[col][valrow].value
                if val > highest:
                    highest = val
                    location = (col, realrow)#there's a chance this doesn't work, but I think it should
        if debugging and location != None:
            print("Across from highest is at " + str(location[0]) + " and " + str(location[1]))
        return location

    def get_location(self, card_val):
        for col in range(4):
            for row in range(2):
                if self.get_state(col) != Board.BOTH_MATCH and self.get_state(col) != Board.NEITHER_FLIPPED:
                    if self.cards[col][row].visible_value == card_val:
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
        elif (self.cards[col][0].value == 0 or self.cards[col][0].value == -5) and (self.cards[col][1].value == 0 or self.cards[col][1].value == -5):
            return Board.BOTH_MATCH #makes joker and 0 count as a match
        else:
            return Board.BOTH_FLIPPED

    def get_score(self):
        score = 0
        matches = []
        for i in range(4):
            #If they match
            if self.cards[i][0].value == self.cards[i][1].value: #interesting note, could probably use walrus operator here
                #if they're jokers, subtract 10 instead of just adding 0
                if self.cards[i][0].value == -5:
                    score -= 10
                matches.append(self.cards[i][0].value)
            else:
                #otherwise they don't match, so add the value of each card
                score += self.cards[i][0].value + self.cards[i][1].value
        for val in matches:
            if matches.count(val) > 1:
                for i in range(matches.count(val)):
                    matches.remove(val)
                    score -= 5
        return score



class DNA():
    def __init__(self, genes = None):
        """
        the traits, in order, are:
        horizontal or vertical: if it prefers flipping with a flipped card or a new col
        highest to take (from discard): lowest number it will take from the discard pile
        highest to keep (fron deck): lowest number it will keep from the deck
        lowest to mitigate: lowest amount you need to save for it to mitigate
        higest card to go for -10 with
        end
        highest to go out with
        """
        if genes == None:
            self.genes = []
            for i in range(7):
                self.genes.append(self.random(i))
        else:
            self.genes = genes

    def random(self, gene):
        if gene == 0:
            if random() < 0.5:
                return True
            else:
                return False
        elif gene == 3:
            return randint(1, 12)
        elif gene == 5:
            return randint(1, 6)
        elif gene == 6:
            return randint(-9, 20)
        else:
            return randint(0, 12)

    def print(self):
        print("horizontal preference: " + str(self.genes[0]))
        print("highest to take (from discard):: " + str(self.genes[1]))
        print("highest to keep (fron deck): " + str(self.genes[2]))
        print("lowest to mitigate: " + str(self.genes[3]))
        print("higest card to go for -10 with: " + str(self.genes[4]))
        print("end: " + str(self.genes[5]))
        print("highest to go out with: " + str(self.genes[6]))




class Player():
    #Layout for a player, by default is a computer player
    def __init__(self, early = None, late = None):
        #make their board and a var for the card they last discarded
        self.board = Board()
        self.card_discarded = None
        #for debugging
        if debugging:
            self.code = randint(0, 100000)
        #make their score variable
        self.score = 0
        #make a variable for if they won
        self.winner = None
        #set up their dna
        self.earlyDNA = None
        self.lateDNA = None
        if early == None:
            self.earlyDNA = DNA()
        else:
            self.earlyDNA = early
        if late == None:
            self.lateDNA = DNA()
        else:
            self.lateDNA = late
        #set up dictionaries with gene info
        early_iterator = iter(self.earlyDNA.genes)
        self.early = {
            "horizontal preference": next(early_iterator),
            "highest to take": next(early_iterator),
            "highest to keep": next(early_iterator),
            "lowest to mitigate": next(early_iterator),
            "highest for -10": next(early_iterator),
            "end": next(early_iterator)
        }
        late_iterator = iter(self.lateDNA.genes)
        self.late = {
            "horizontal preference": next(late_iterator),
            "highest to take": next(late_iterator),
            "highest to keep": next(late_iterator),
            "lowest to mitigate": next(late_iterator),
            "highest for -10": next(late_iterator),
            "end for -10": next(late_iterator),
            "highest to go out with": next(late_iterator)
        }
        #variables for taking the turn
        self.one_flipped_per_row = False
        self.going_for_minus10 = []

    def flip_two(self):
        #will always flip this one
        self.board.cards[0][0].flip()
        #other one determined by preference
        if(self.early.get("horizontal preference")):
            if debugging:
                print("Flipping horizontal card")
            self.board.cards[1][0].flip()
        else:
            if debugging:
                print("Flipping vertical card")
            self.board.cards[0][1].flip()

    def take_turn(self, deck, discarded, opponents):
        #var to see if turn is done yet
        turn_done = False
        
        #figure out what stage we're in
        stage = 2
        #first, see if we have one flipped in every row
        if self.early.get("horizontal preference") and not self.one_flipped_per_row:
            self.one_flipped_per_row = True
            for col in range(4):
                if(self.board.get_state(col) == Board.NEITHER_FLIPPED):
                    self.one_flipped_per_row = False

        #now, if there isn't one flipped in every row, we are in stage 1
        if self.early.get("horizontal preference") and not self.one_flipped_per_row:
            stage = 1

        #now check if there is only one card left to be flipped
        if stage != 1:
            one_flipped_count = 0
            neither_flipped_count = 0
            for col in range(4):
                if self.board.get_state(col) == Board.ONE_FLIPPED:
                    one_flipped_count += 1
                if self.board.get_state(col) == Board.NEITHER_FLIPPED:
                    neither_flipped_count += 1
            if one_flipped_count == 1 and neither_flipped_count == 0:
                stage = 3

        #if neither of these are true, we are in stage 2

        #get info we need for turn
        #find how late in the game we are
        lowest_unflipped_opponent = 8
        for o in opponents:
            if len(o.board.get_unflipped_locations()) < lowest_unflipped_opponent:
                lowest_unflipped_opponent = len(o.board.get_unflipped_locations())
        if debugging:
            print("Lowest amount of unflipped cards of opponents is: " + str(lowest_unflipped_opponent))

        part = None
        if lowest_unflipped_opponent > self.early.get("end"):
            part = self.early
        else:
            part = self.late
        replace_minus10 = True
        if lowest_unflipped_opponent > self.late.get("end for -10"):
            replace_minus10 = False

        #now do logic for each turn
        if debugging:
            print("Starting the turn, stage is: " + str(stage))
            print("Checking discarded card")
        turn_done = self.check_card(discarded, stage, part.get("highest to take"), part, replace_minus10)
        if not turn_done:
            if debugging:
                print("Didn't use discarded card, drawing a card")
            card_drawn = deck.draw()
            turn_done = self.check_card(card_drawn, stage, part.get("highest to keep"), part, replace_minus10)
        if not turn_done:
            if not stage == 3:
                if debugging:
                    print("Didn't use drawn card so just flipping")
                self.flip_card(stage, card_drawn)
                turn_done = True
            else:
                if debugging:
                    print("Didn't use drawn card, so discarding and ending turn")
                self.card_discarded = card_drawn
                turn_done = True
        #turn is now done
        if debugging:
            print("Turn is ending")
        #return true if we went out, false otherwise
        return self.board.all_flipped()

    def take_last_turn(self, deck, discarded, opponents):
        turn_done = False
        if debugging:
            print("On last turn")
            print("checking discarded card")
        #really this should be a lot more complex than I'll make it initially
        #it should change depending on if you still need to make matches
        turn_done = self.check_card(discarded, 4, self.late.get("highest to keep"), self.late, True)
        if not turn_done:
            if debugging:
                print("Didn't take discarded card, so drawing a card")
            card_drawn = deck.draw()
            turn_done = self.check_card(card_drawn, 4, self.late.get("highest to keep"), self.late, True)
        if not turn_done:
            if debugging:
                print("Didn't use drawn card so just discarding")
            self.card_discarded = card_drawn
            turn_done = True
        self.board.flip_all()

    def check_card(self, card, stage, lowest, part, replace_minus10):
        #seperate logic just for jokers (-5s)
        if card.value == -5:
            if debugging:
                print("Card is a joker")
            if stage != 4:
                #check if there is another joker
                if card.value in self.board.get_unmatched():
                    #match it, going for -10 doesn't matter here cuz you wouldn't discard a joker for -10 (technically sometimes you should tho)
                    col, row = self.board.get_location(card.value)
                    if row == 0:
                        row = 1
                    else:
                        row = 0
                    self.switch_cards(card, col, row)
                    if debugging:
                        print("Matching the joker")
                    return True
                #if there is a 0, match the joker with the 0
                elif 0 in self.board.get_unmatched():
                    col, row = self.board.get_location(0)
                    if row == 0:
                        row = 1
                    else:
                        row = 0
                    self.switch_cards(card, col, row)
                    if debugging:
                        print("Matching the joker with a 0")
                    return True
                else:
                    #nothing to match it with, so either put it in new col or replace highest unflipped card
                    for col in range(4):
                        if self.board.get_state(col) == Board.NEITHER_FLIPPED:
                            self.switch_cards(card, col, 0)
                            if debugging:
                                print("Putting joker in a new col")
                            return True
                    #if not done yet
                    #Note: highest unmatched can't be none here, since we checked for empty cols already
                    col, row = self.board.get_location(self.board.get_highest_unmatched())
                    self.switch_cards(card, col, row)
                    if debugging:
                        print("Replacing highest unmatched with a joker")
                    return True

            else:
                #if we are on the last turn, replace highest card if it it above 5, otherwise replace facedown card
                if self.board.get_highest_unmatched() != None:
                    if self.board.get_highest_unmatched() > 5:
                        col, row = self.board.get_location(self.board.get_highest_unmatched())
                        self.switch_cards(card, col, row)
                        if debugging:
                            print("Replacing highest unmatched with a joker")
                        return True
                    else:
                        col, row = self.board.get_unflipped_locations()[0]
                        self.switch_cards(card, col, row)
                        if debugging:
                            print("Replacing unflipped card with a joker")
                        return True



        if stage == 1:
            #check if card is a match
            if card.value in self.board.get_unmatched():
                if debugging:
                    print("The discarded card matches an unmatched card, so we're matching it")
                col = self.board.get_location(card.value)[0]
                row = self.board.get_unflipped(col)
                self.switch_cards(card, col, row)
                #if there is another one of what we just matched, we can go for -10 with it (if it's low enough)
                if card.value in self.board.get_unmatched() and card.value <= part.get("highest for -10"):
                    self.going_for_minus10.append(card.value)
                return True
            #also match 0s with jokers
            if card.value == 0 and -5 in self.board.get_unmatched():
                #put it with a joker if there is one
                col, row = self.board.get_location(-5)
                if row == 0:
                    row = 1
                else:
                    row = 0
                self.switch_cards(card, col, row)
                if debugging:
                    print("Matching the zero with a joker")
                return True
            #if we aren't done, card doesn't match anything, let's see if its same as another match
            if card.value in self.board.get_matches() and card.value <= part.get("highest for -10"):
                #put it in a new col
                col = None
                row = 0
                for column in range(4):
                    if self.board.get_state(column) == Board.NEITHER_FLIPPED:
                        col = column
                self.switch_cards(card, col, row)
                self.going_for_minus10.append(card.value)
                if debugging:
                    print("Taking card since it is low enough to go for -10 with")
                return True
            #if neither of those happen, see if it is low enough to keep
            if card.value <= lowest:
                col = None
                for column in range(4):
                    if self.board.get_state(column) == Board.NEITHER_FLIPPED:
                        col = column
                self.switch_cards(card, col, 0)
                if debugging:
                    print("Card is low enough to keep so keeping it")
                return True
        elif stage == 2:
            #check if card matches an unmatched card
            if card.value in self.board.get_unmatched():
                if debugging:
                    print("Card matches an unmatched card")
                col, row = self.board.get_location(card.value)
                if row == 0:
                    row = 1
                else:
                    row = 0
                #check if card we're replacing is going for -10
                if self.board.cards[col][row].visible_value in self.going_for_minus10:
                    if debugging:
                        print("Card we would get rid of is going for -10")
                    if replace_minus10:
                        self.switch_cards(card, col, row)
                        #if there is another of what we just matched and it is low enough, go for -10 with it
                        if card.value in self.board.get_unmatched() and card.value <= part.get("highest for -10"):
                            self.going_for_minus10.append(card.value)
                        if debugging:
                            print("Replacing the card anyways")
                        return True
                    else:
                        if debugging:
                            print("We won't replace it")
                elif self.board.cards[col][row].visible_value != -5:
                    #if card we're replacing isnt going for -10, replace it as long as it's not a -5 (might change this not sure)
                    self.switch_cards(card, col, row)
                    if debugging:
                        print("Matching the card")
                    return True
            #if we're here, card doesn't match an unmatched card, so check if we can match a 0 with a -5
            if card.value == 0 and -5 in self.board.get_unmatched():
                #put it with a joker if there is one
                col, row = self.board.get_location(-5)
                if row == 0:
                    row = 1
                else:
                    row = 0
                self.switch_cards(card, col, row)
                if debugging:
                    print("Matching the zero with a joker")
                return True
            #if we're here, there is no match at all, check if card can go for -10
            if card.value in self.board.get_matches() and card.value <= part.get("highest for -10"):
                if debugging:
                    print("Card can go for -10 and is low enough")
                #now figure out where to put it
                #first check if there is empty col
                for col in range(4):
                    if self.board.get_state(col) == Board.NEITHER_FLIPPED:
                        if debugging:
                            print("There is an empty col, so putting it there")
                        self.going_for_minus10.append(card.value)
                        self.switch_cards(card, col, 0)
                        return True
                #if not, we can replace a flipped card or an unflipped card
                #we will replace a flipped card if we mitigate enough by doing so
                if self.board.get_highest_unmatched() != None:
                    if (self.board.get_highest_unmatched() - card.value) >= part.get("lowest to mitigate"):
                        col, row = self.board.get_location(self.board.get_highest_unmatched())
                        self.switch_cards(card, col, row)
                        if debugging:
                            print("We mitigate enough by replacing our highest card, so doing that")
                        return True
                #otherwise, replace the unflipped card across from the highest unmatched
                if self.board.get_across_from_highest() != None:
                    if debugging:
                        print("Putting card across from highest card with an unflipped card across from it")
                    col, row = self.board.get_across_from_highest()
                    self.switch_cards(card, col, row)
                    return True
                #we should never get this far within this if statement
                if debugging:
                    print("We aren't supposed to get here in stage 2")
            #if we're here, card can't go for -10 so check if it's low enough
            if card.value <= lowest:
                if debugging:
                    print("Card is low enough to keep")
                #now figure out where to put it
                #first check if there is empty col
                for col in range(4):
                    if self.board.get_state(col) == Board.NEITHER_FLIPPED:
                        if debugging:
                            print("There is an empty col, so putting it there")
                        self.going_for_minus10.append(card.value)
                        self.switch_cards(card, col, 0)
                        return True
                #if not, we can replace a flipped card or an unflipped card
                #we will replace a flipped card if we mitigate enough by doing so
                if self.board.get_highest_unmatched() != None:
                    if (self.board.get_highest_unmatched() - card.value) >= part.get("lowest to mitigate"):
                        col, row = self.board.get_location(self.board.get_highest_unmatched())
                        self.switch_cards(card, col, row)
                        if debugging:
                            print("We mitigate enough by replacing our highest card, so doing that")
                        return True
                #otherwise, replace the unflipped card across from the highest unmatched
                if self.board.get_across_from_highest() != None:
                    if debugging:
                        print("Putting card across from highest card with an unflipped card across from it")
                    col, row = self.board.get_across_from_highest()
                    self.switch_cards(card, col, row)
                    return True
        elif stage == 3:
            #get value of card in last row with an unflipped card
            last_card_col = None
            for col in range(4):
                if self.board.get_state(col) == Board.ONE_FLIPPED:
                    last_card_col = col
            #check if card matches unmatched card
            if card.value in self.board.get_unmatched():
                if debugging:
                    print("Card matches an unmatched card")
                col, row = self.board.get_location(card.value)
                if row == 0:
                    row = 1
                else:
                    row = 0
                #see if card will make us go out
                if col == last_card_col:
                    if debugging:
                        print("Card matches with last card, seeing if we wanna go out")
                    #see if going out is worth it
                    test_board = self.board.copy()
                    test_board.cards[col][row] = card
                    test_score = test_board.get_score()
                    if test_score <= self.late.get("highest to go out with"):
                        #then go out
                        self.switch_cards(card, col, row)
                        if debugging:
                            print("Will end with low enough score, so going out")
                        return True
                #check if it replaces a card we're going for -10 with
                elif self.board.cards[col][row].visible_value in self.going_for_minus10:
                    if debugging:
                        print("Card we would replace if going for -10")
                    if replace_minus10:
                        self.switch_cards(card, col, row)
                        #if there is another of what we just matched and it is low enough, go for -10 with it
                        if card.value in self.board.get_unmatched() and card.value <= part.get("highest for -10"):
                            self.going_for_minus10.append(card.value)
                        if debugging:
                            print("Replacing the card anyways")
                        return True
                    else:
                        if debugging:
                            print("We won't replace it")
                elif self.board.cards[col][row].visible_value != -5:
                    #if card we're replacing isnt going for -10, replace it as long as it's not a -5 (might change this not sure)
                    self.switch_cards(card, col, row)
                    if debugging:
                        print("Matching the card")
                    return True
            #check if we can match a 0 with a joker
            if card.value == 0 and -5 in self.board.get_unmatched():
                #put it with a joker if there is one
                col, row = self.board.get_location(-5)
                if row == 0:
                    row = 1
                else:
                    row = 0
                self.switch_cards(card, col, row)
                if debugging:
                    print("Matching the zero with a joker")
                return True
            #if we are here, card doesn't match an unmatched card
            #check if card matches a match we already have
            #Note: get_highest_unmatched shouldn't be able to be None here since we're in stage 3
            if card.value in self.board.get_matches() and card.value < self.board.get_highest_unmatched():
                if debugging:
                    print("Card makes -10 and is lower than highest unmatched, so taking it")
                self.going_for_minus10.append(card.value)
                col, row = self.board.get_location(board.get_highest_unmatched())
                self.switch_cards(card, col, row)
                return True
            #now check if we wanna just go out with some points
            test_board = self.board.copy()
            #get location of last card
            col = None
            for column in range(4):
                if self.board.get_state(column) == Board.ONE_FLIPPED:
                    col = column
                    row = self.board.get_unflipped(col)
            test_board.cards[col][row] = card
            test_score = test_board.get_score()
            if test_score <= self.late.get("highest to go out with"):
                #then go out
                self.switch_cards(card, col, row)
                if debugging:
                    print("Will end with low enough score, so going out")
                return True
            #see if card mitigates
            if (self.board.get_highest_unmatched() - card.value) >= part.get("lowest to mitigate"):
                if (self.board.get_highest_unmatched() in self.going_for_minus10 and replace_minus10) or (not self.board.get_highest_unmatched() in self.going_for_minus10):
                    #there is likely a better way to do that if statement
                    col, row = self.board.get_location(self.board.get_highest_unmatched())
                    self.switch_cards(card, col, row)
                    if debugging:
                        print("We mitigate enough by replacing our highest card, so doing that")
                    return True
                else:
                    #keep the -10 one, so mitigate next highest if there is one
                    highest = -5
                    for val in self.board.get_unmatched():
                        if val not in self.going_for_minus10 and val > highest:
                            highest = val
                    #found next highest, see if it is higher than drawn
                    if card.value < highest:
                        #switch these
                        col, row = self.board.get_location(highest)
                        self.switch_cards(card, col, row)
                        if debugging:
                            print("Keeping -10 one, so mitigating next highest")
                        return True
            #if card doesn't mitigate, we just return false
        elif stage == 4:
            if card.value in self.board.get_unmatched():
                if debugging:
                    print("The discarded card matches an unmatched card")
                col, row = self.board.get_location(card.value)
                if row == 0:
                    row = 1
                else:
                    row = 0
                if (card.value + self.board.cards[col][row].value) > (self.board.get_highest_unmatched() - card.value):
                    if debugging:
                        print("Matching saves more than mitigating")
                    self.switch_cards(card, col, row)
                    return True
                else:
                    if debugging:
                        print("Matching saves less than mitigating")
            #if no match or match saves less than mitigating, we either mitigate a flipped card (if it's above 5) or an unflipped card, or draw
            #if card is from discard or is below -5
            if lowest == part.get("highest to take") or card.value < 5:
                #then mitigate at all if we can
                if self.board.get_highest_unmatched() != None:
                    if card.value < self.board.get_highest_unmatched():
                        if self.board.get_highest_unmatched() > 5:
                            col, row = self.board.get_location(self.board.get_highest_unmatched())
                            self.switch_cards(card, col, row)
                            if debugging:
                                print("Switching out highest unmatched card")
                                return True
                        else:
                            col, row = self.board.get_unflipped_locations()[0]
                            self.switch_cards(card, col, row)
                            if debugging:
                                print("Switching out unflipped card")
                            return True
                else:
                    col, row = self.board.get_unflipped_locations()[0]
                    self.switch_cards(card, col, row)
                    if debugging:
                        print("Switching out unflipped card")
                    return True
        else:
            if debugging:
                print("I shouldn't get here, stage should only be 1, 2, or 3")
        #if the turn is never done (no switch is made) return false
        return False

    def flip_card(self, stage, to_discard):
        if stage == 1:
            for col in range(4):
                if self.board.get_state(col) == Board.NEITHER_FLIPPED:
                    self.board.cards[col][0].flip()
                    self.card_discarded = to_discard
                    if self.board.cards[col][0].value in self.board.get_matches():
                        self.going_for_minus10.append(self.board.cards[col][0].value)
                    return 0
        elif stage == 2:
            if self.early.get("horizontal preference"):
                for col in range(4):
                    if self.board.get_state(col) == Board.NEITHER_FLIPPED:
                        self.board.cards[col][0].flip()
                        self.card_discarded = to_discard
                        if self.board.cards[col][0].value in self.board.get_matches():
                            self.going_for_minus10.append(self.board.cards[col][0].value)
                        return 0
            #otherwise flip opposite highest col
            if self.board.get_across_from_highest() != None:
                if debugging:
                    print("Flipping card across from highest card with an unflipped card across from it")
                col, row = self.board.get_across_from_highest()
                self.board.cards[col][row].flip()
                self.card_discarded = to_discard
                if self.board.cards[col][row].value in self.board.get_matches():
                    self.going_for_minus10.append(self.board.cards[col][row].value)
                return 0
            #if there isn't one, flip new col
            for col in range(4):
                    if self.board.get_state(col) == Board.NEITHER_FLIPPED:
                        self.board.cards[col][0].flip()
                        self.card_discarded = to_discard
                        if self.board.cards[col][0].value in self.board.get_matches():
                            self.going_for_minus10.append(self.board.cards[col][0].value)
                        return 0
        return -1


    def switch_cards(self, card, col, row):
        #remove card from going for -10 if it is in there
        if self.board.cards[col][row].visible_value in self.going_for_minus10:
            self.going_for_minus10.remove(self.board.cards[col][row].value)
        #remove card from going for -10 if this gives us -10
        if card.visible_value in self.going_for_minus10:
            self.going_for_minus10.remove(card.value)
        #actually switch the cards
        self.card_discarded = self.board.cards[col][row]
        self.card_discarded.flip()
        self.board.cards[col][row] = card

    #evolution functions

    def calc_fitness(self, opponents): #might need to make this work for all rounds (multiply both sides by number of rounds)
        #fitness should really be based on how much you beat your opponent by, maybe we actually only breed winners
        #map score from 150 to -150 to be between 0 and 50
        if not self.winner:
            if debugging:
                print("Fitness is 0")
            return 0
        else:
            #get best opponent's score
            best_opponent = 150
            for o in opponents:
                if o.board.get_score() < best_opponent:
                    best_opponent = o.board.get_score()
            fitness =  best_opponent - self.board.get_score()
        if debugging:
            print("Fitness is " + str(fitness))
        return int(fitness)

    def mate(self, partner):
        new_early = DNA()
        new_late = DNA()
        for i in range(len(new_early.genes)):
            if random() < 0.5:
                new_early.genes[i] = self.earlyDNA.genes[i]
            else:
                new_early.genes[i] = partner.earlyDNA.genes[i]

        for i in range(len(new_late.genes)):
            if random() < 0.5:
                new_late.genes[i] = self.lateDNA.genes[i]
            else:
                new_late.genes[i] = partner.lateDNA.genes[i]
        return Player(new_early, new_late)

    def mutate(self, mutation_rate):
        # for i in range(len(self.earlyDNA.genes)):
        #     if random() < mutation_rate:
        #         self.earlyDNA.genes[i] = self.earlyDNA.random(i)

        # for i in range(len(self.lateDNA.genes)):
        #     if random() < mutation_rate:
        #         self.lateDNA.genes[i] = self.lateDNA.random(i)
        if random() < mutation_rate:
            self.earlyDNA = DNA()
            self.lateDNA = DNA()
            if debugging:
                print("Mutated")



class User(Player):
    def __init__(self):
        super(User, self).__init__()

    def flip_two(self):
        col = self.get_input("Enter col of card to flip ", [0, 1, 2, 3], True)
        if col == "exit":
            return "exit"
        row = self.get_input("Enter row of card to flip ", [0, 1], True)
        if row == "exit":
            return "exit"
        col2 = self.get_input("Enter col of second card to flip ", [0, 1, 2, 3], True)
        if col2 == "exit":
            return "exit"
        row2 = self.get_input("Enter row of second card to flip ", [0, 1], True)
        if row2 == "exit":
            return "exit"

        while(col == col2 and row == row2):
            print("You need to flip 2 different cards")
            col2 = self.get_input("Enter col of second card to flip ", [0, 1, 2, 3], True)
            if col2 == "exit":
                return "exit"
            row2 = self.get_input("Enter row of second card to flip ", [0, 1], True)
            if row2 == "exit":
                return "exit"

        self.board.cards[col][row].flip()
        self.board.cards[col2][row2].flip()

    def take_turn(self, deck, discarded, opponents):
        draw_card = self.get_input("Enter draw to draw a card, or keep to use the discarded card ", ["draw", "keep"])
        if draw_card == "exit":
            return "exit"
        if draw_card == "draw":
            #check if we're supposed to flip
            flip = True
            one_flipped_count = 0
            neither_flipped_count = 0
            for col in range(4):
                if self.board.get_state(col) == Board.ONE_FLIPPED:
                    one_flipped_count += 1
                if self.board.get_state(col) == Board.NEITHER_FLIPPED:
                    neither_flipped_count += 1
            if one_flipped_count == 1 and neither_flipped_count == 0:
                flip = False

            card_drawn = deck.draw()
            print("You drew " + str(card_drawn.visible_value))
            if flip:
                keep = self.get_input("Do you want to keep the card you drew (enter keep), or flip a card on your board (enter flip)? ", ["keep", "flip"])
            else:
                keep = self.get_input("Do you want to keep the card you drew (enter keep), or end the turn (enter end)? ", ["keep", "end"])
                if keep == "end":
                    return False
            if keep == "exit":
                return "exit"
            if keep == "keep":
                col = self.get_input("Enter col of where to put your card ", [0, 1, 2, 3], True)
                if col == "exit":
                    return "exit"
                row = self.get_input("Enter row of where to put your card ", [0, 1], True)
                if row == "exit":
                    return "exit"

                self.card_discarded = self.board.cards[col][row]
                self.card_discarded.flip()
                self.board.cards[col][row] = card_drawn
            elif keep == "flip":
                col = self.get_input("Enter col of card to flip ", [0, 1, 2, 3], True)
                if col == "exit":
                    return "exit"
                row = self.get_input("Enter row of card to flip ", [0, 1], True)
                if row == "exit":
                    return "exit"

                while self.board.cards[col][row].visible_value != "F":
                    print("You must flip an unflipped card")
                    col = self.get_input("Enter col of card to flip ", [0, 1, 2, 3], True)
                    if col == "exit":
                        return "exit"
                    row = self.get_input("Enter row of card to flip ", [0, 1], True)
                    if row == "exit":
                        return "exit"

                self.board.cards[col][row].flip()
                self.card_discarded = card_drawn
        elif draw_card == "keep":
            col = self.get_input("Enter col of where to put your card ", [0, 1, 2, 3], True)
            if col == "exit":
                return "exit"
            row = self.get_input("Enter row of where to put your card ", [0, 1], True)
            if row == "exit":
                return "exit"

            self.card_discarded = self.board.cards[col][row]
            self.card_discarded.flip()
            self.board.cards[col][row] = discarded
        return self.board.all_flipped()

    def take_last_turn(self, deck, discarded, opponents):
        print("This is your last turn")
        exited = self.take_turn(deck, discarded, opponents)
        self.board.flip_all()
        return exited


    def get_input(self, message, valid_inputs, is_int = False):
        nums = ["1", "2", "3", "4"]
        if is_int:
            real_valid = [x + 1 for x in valid_inputs]
        else:
            real_valid = valid_inputs
        real_valid.append("exit")
        my_input = input(message)
        if my_input == "exit":
            return "exit"
        if is_int and my_input in nums:
            my_input = int(my_input) - 1
        else:
            my_input = my_input.lower()
        while my_input not in valid_inputs:
            print("Invalid input, enter again (valid inputs are: " + str(real_valid))
            my_input = input(message)
            if my_input == "exit":
                return "exit"
            if is_int and my_input in nums:
                my_input = int(my_input) - 1
            else:
                my_input = my_input.lower()
        
        return my_input



class Game():
    #basic game, only with 2 players for now
    def __init__(self, playable = False, show_text = False, player1 = None, player2 = None, out_of = None):
        self.out_of = out_of
        self.players = []
        self.show_text = show_text
        if playable:
            self.players.append(Player())
            self.players.append(User())
        elif player1 == None:
            self.players.append(Player())
            self.players.append(Player())
        else:
            self.players.append(player1)
            self.players.append(player2)
        self.discard_pile_card = None
        self.scores_check = []

    def print_discarded(self):
        print(str(self.discard_pile_card.visible_value) + " F")

    def deal(self, deck):
        for p in self.players:
            for col in range(4):
                for row in range(2):
                    p.board.cards[col][row] = deck.draw_face_down()

    def reshuffle(self, deck):
        temp = Deck()
        for p in self.players:
            for col in range(4):
                for row in range(2):
                    if debugging:
                        print("removing " + str(p.board.cards[col][row].value))
                    temp.remove_card(p.board.cards[col][row].value)
        return temp

    def play(self):
        if self.out_of != None:
            wins = [0, 0]
            while wins[0] < (self.out_of / 2) and wins[1] < (self.out_of / 2):
                self.play_one_game()
                if self.players[0].winner:
                    wins[0] += 1
                else:
                    wins[1] += 1
            if wins[0] < wins[1]:
                self.players[0].winner = True
                self.players[1].winner = False
            else:
                self.players[1].winner = True
                self.players[0].winner = False
        else:
            self.play_one_game()

    def play_one_game(self):
        game_done = False
        for i in range(9):
            if self.show_text:
                print("")        
                print("Starting round " + str(i + 1))
                print("")
            done = self.play_round()
            if done == "exit":
                return
        self.end_game()

    def play_round(self):
        #for debugging
        #turns = 0
        #basic setup
        deck = Deck()
        self.deal(deck)
        self.discard_pile_card = deck.draw()
        #start the game
        for p in self.players:
            exited = p.flip_two()
            if exited == "exit":
                return "exit"
        #variables needed to know the state of the round
        round_over = False
        someone_went_out = False
        last_turn = False
        p_who_went_out = None

        #play each player's turn
        while not round_over:
            #turns += 1
            self.scores_check.append(self.players[0].board.get_score()) #could also count turns and if its more than like 5000 turns then do same thing
            if len(self.scores_check) > 1000:
                if self.scores_check[len(self.scores_check) - 1000] == self.scores_check[len(self.scores_check) - 1]:
                    self.players[0].late["highest to go out with"] = 10
                    if debugging:
                        print("Made someone go out cuz game was never changing")
            for i in range(len(self.players)):
                #check if deck is empty
                if len(deck.cards) == 0:
                    deck = self.reshuffle(deck)
                    if debugging:
                        print("Deck shuffled")
                p = self.players[i]
                #make list of all opponents
                opponents = self.players.copy()
                opponents.remove(p)

                if p != p_who_went_out:
                    if self.show_text:
                        print("")
                        print("")
                        print("Player " + str(i + 1) + "'s turn")
                        print("")
                        self.print_discarded()
                        print("")
                        p.board.print()

                    if not last_turn:
                        someone_went_out = p.take_turn(deck, self.discard_pile_card, opponents)
                        if someone_went_out == "exit":
                            return "exit"
                        self.discard_pile_card = p.card_discarded
                    else:
                        exited = p.take_last_turn(deck, self.discard_pile_card, opponents)#likely don't need opponents, just here for now for debugging
                        if exited == "exit":
                            return "exit"
                        self.discard_pile_card = p.card_discarded

                    if someone_went_out and not last_turn:
                        if self.show_text:
                            print("Someone went out")
                        p_who_went_out = p
                        last_turn = True
                    if self.show_text:
                        print("After the turn:")
                        print("")
                        p.board.print()
                else:
                    round_over = True
                    break
        if self.show_text:
            print("")
            print("The round is over")
        #add each player's score for the round to their total score
        for p in self.players:
            p.score += p.board.get_score()
        #print the scores
        if self.show_text:
            print("The scores for this round are: ")
            for i in range(len(self.players)):
                print("Player " + str(i + 1) + ": " + str(self.players[i].board.get_score()))
            print("The total scores are:")
            for i in range(len(self.players)):
                print("Player " + str(i + 1) + ": " + str(self.players[i].score))



    def end_game(self):
        if debugging and self.show_text:
            print("The game is over")
        #probably just gonna be used to calculate the player's fitness
        scores = []
        winner_indexes = []
        #find all the scores
        for p in self.players:
            scores.append(p.board.get_score())
        #find the lowest score
        winning_score = min(scores)
        #see who had that score
        for i in range(len(self.players)):
            if self.players[i].board.get_score() == winning_score:
                winner_indexes.append(i)
        #if your score is a winning score, you're a winner, otherwise you're a loser
        for i in range(len(self.players)):
            if i in winner_indexes:
                self.players[i].winner = True
            else:
                self.players[i].winner = False
        #this makes everyone lose if there's a tie (this can be commented out)
        if len(winner_indexes) > 1:
            for p in self.players:
                p.winner = False


class Evolution():
    def __init__(self, master, display_window = True):
        #need to set up both actual evolution stuff and tkinter window stuff
        #evolution stuff
        self.population_size = 50 #must be even number
        self.mutation_rate = 0.01
        self.population = []
        self.mating_pool = []
        self.games = []
        self.generations = 0
        self.paused = True
        self.first_run = True

        #for stats
        self.best_fitness = 0
        self.average_score = None
        self.total_of_scores = 0
        self.total_scores = 0
        self.best_early = DNA()
        self.best_late = DNA()


        self.display_window = display_window
        self.master = master


        #make the window
        #set up window basics
        if display_window:
            self.make_window()


    def make_window(self):
        self.stat_frm = tk.Frame(master = self.master, width=100, height=100)
        self.btn_frm = tk.Frame(master = self.master, width=100, height=100)
        self.title_lbl = tk.Label(master = self.master, text = "PlayNine Evolution", fg = "black", width = 20, height = 3)
        #self.window.configure(background="white")
        # self.stat_frm.config(bg = "white")
        # self.btn_frm.config(bg = "white")
        # self.title_lbl.config(bg = "white")
        self.title_lbl.pack()

        #set up label frame
        self.lbl_frame_labels = []
        #generations
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "Generations: 0"))
        #best score
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "Best fitness: Waiting for first run"))
        #average score
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "Average score: Waiting for first run"))
        #best genes
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "Best genes of generation:"))
        #early genes
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "Early:"))
        #horizontal preference (true or false)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "horizontal preference: Waiting for first run"))
        #highest to take (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "highest to take (btwn 0 and 12): Waiting for first run"))
        #highest to keep (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "highest to keep (btwn 0 and 12): Waiting for first run"))
        #lowest to mitigate (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "lowest to mitigate (btwn 0 and 12): Waiting for first run"))
        #highest for -10 (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "highest for -10 (btwn 0 and 12): Waiting for first run"))
        #end (btwn 1 and 6)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "end (btwn 1 and 6): Waiting for first run"))
        #highest to go out with (btwn -9 and 20)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "highest to go out with (btwn -9 and 20): Waiting for first run"))
        #late genes
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "Late:"))
        #horizontal preference (true or false)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "horizontal preference: Waiting for first run"))
        #highest to take (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "highest to take (btwn 0 and 12): Waiting for first run"))
        #highest to keep (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "highest to keep (btwn 0 and 12): Waiting for first run"))
        #lowest to mitigate (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "lowest to mitigate (btwn 0 and 12): Waiting for first run"))
        #highest for -10 (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "highest for -10 (btwn 0 and 12): Waiting for first run"))
        #end for -10 (btwn 1 and 6)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "end for -10 (btwn 1 and 6): Waiting for first run"))
        #highest to go out with (btwn -9 and 20)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "highest to go out with (btwn -9 and 20): Waiting for first run"))
        
        #add all labels to the frame
        for l in self.lbl_frame_labels:
            l.pack(anchor = "w")
            #l.config(bg = "white")
            if debugging:
                l.config(borderwidth=1, relief="solid")

        #set up button frame
        self.btn_frame_buttons = []
        #start button
        self.btn_frame_buttons.append(tk.Button(master = self.btn_frm, text = "Start", command = self.start))
        #stop button
        self.btn_frame_buttons.append(tk.Button(master = self.btn_frm, text = "Stop", command = self.stop))
        #load button
        self.btn_frame_buttons.append(tk.Button(master = self.btn_frm, text = "Load", command = self.load))
        #save button
        self.btn_frame_buttons.append(tk.Button(master = self.btn_frm, text = "Save Population", command = self.save))
        #save best player button
        self.btn_frame_buttons.append(tk.Button(master = self.btn_frm, text = "Save Best Player", command = self.save_best))
        #mutation rate label
        self.btn_frame_buttons.append(tk.Label(master = self.btn_frm, text = "Mutation rate:"))
        #mutation rate spinbox
        self.btn_frame_buttons.append(tk.Spinbox(master = self.btn_frm, from_ = 0, to = 1, increment = 0.001, width = 6, command = self.spin))
        self.btn_frame_buttons[6].delete(0,"end")
        self.btn_frame_buttons[6].insert(0,0.01)

        #add all buttons to the frame
        for b in self.btn_frame_buttons:
            b.pack()

        #add the frames to the window
        self.btn_frm.pack(fill=tk.BOTH, side=tk.RIGHT)
        self.stat_frm.pack(fill=tk.BOTH, side=tk.RIGHT)


    def start(self):
        #start button
        if debugging:
            print("Start button pressed")
        #make paused false, call run
        self.paused = False
        self.run()


    def stop(self):
        #stop button
        if debugging:
            print("Stop button pressed")
        #make paused true
        self.paused = True


    def load(self):
        #load button
        if debugging:
            print("Load button pressed")
        #we dont want the population to be randomized if we load a pop in right away
        self.first_run = False
        new_pop = []
        with open(filedialog.askopenfilename(defaultextension = ".txt", initialdir = "Saves/Populations"), 'r') as reader:
            for line in reader:
                #break out of loop once we get to last 3 lines
                if len(line) < 20:
                    self.generations = int(line.strip())
                    break
                new_early = []
                new_late = []
                genes = line.split(",")
                early = genes[0].split("/")
                late = genes[1].split("/")
                new_early.append(early[0] == "True")
                for i in range(6):
                    new_early.append(int(early[i + 1]))
                #do the same for late
                new_late.append(late[0] == "True")
                for i in range(6):
                    new_late.append(int(late[i + 1]))
                #now add player to new pop with those genes
                new_pop.append(Player(DNA(new_early), DNA(new_late)))
                #Player(DNA(early), DNA(late)) will be the format
            self.best_fitness = int(reader.readline().strip())
            self.average_score = float(reader.readline().strip())
            self.population = new_pop
            self.population_size = len(new_pop)
            #now need to load in best stats
            new_best_early = []
            new_best_late = []
            genes = reader.readline().split(",")
            early = genes[0].split("/")
            late = genes[1].split("/")
            new_best_early.append(early[0] == "True")
            for i in range(6):
                new_best_early.append(int(early[i + 1]))
            #do the same for late
            new_best_late.append(late[0] == "True")
            for i in range(6):
                new_best_late.append(int(late[i + 1]))
        self.best_early.genes = new_best_early
        self.best_late.genes = new_best_late
        self.update_window()
        if debugging:
            print("File read")


    def save(self):
        #save button
        if debugging:
            print("Save button pressed")
        with open(filedialog.asksaveasfilename(defaultextension = ".txt", initialdir = "Saves/Populations"), 'w') as writer:
            for p in self.population:
                line = ""
                for g in p.earlyDNA.genes:
                    line += str(g) + "/"
                line += ","
                for g in p.lateDNA.genes:
                    line += str(g) + "/"
                line += "\n"
                writer.write(line)
            writer.write(str(self.generations) + "\n")
            writer.write(str(self.best_fitness) + "\n")
            writer.write(str(self.average_score) + "\n")
            #now need to save best stats
            line = ""
            for g in self.best_early.genes:
                line += str(g) + "/"
            line += ","
            for g in self.best_late.genes:
                line += str(g) + "/"
            line += "\n"
            writer.write(line)


    def save_best(self):
        #save button
        if debugging:
            print("Save button pressed")
        with open(filedialog.asksaveasfilename(defaultextension = ".txt", initialdir = "Saves/Players"), 'w') as writer:
            writer.write(str(0) + "\n")
            writer.write(str(0) + "\n")
            writer.write(str(0) + "\n")
            #now need to save best stats
            line = ""
            for g in self.best_early.genes:
                line += str(g) + "/"
            line += ","
            for g in self.best_late.genes:
                line += str(g) + "/"
            line += "\n"
            writer.write(line)


    def spin(self):
        self.mutation_rate = float(self.btn_frame_buttons[6].get())


    def run(self):
        #create the first random population if it's the first run
        if self.first_run:
            for i in range(self.population_size):
                self.population.append(Player())
            self.first_run = False
        while not self.paused:
            #add one to generations
            self.generations += 1
            if debugging:
                print("Generation: " + str(self.generations))
            #clear the old games
            self.games.clear()
            #fill up the games
            for i in range(0, self.population_size - 1, 2):
                self.games.append(Game(False, debugging, self.population[i], self.population[i + 1]))
            if debugging:
                print("Games size: " + str(len(self.games)))
            #play the games
            for g in self.games:
                g.play()
            #reset total of scores, total scores, and best fitness
            self.best_fitness = 0
            self.total_of_scores = 0
            self.total_scores = 0
            self.mating_pool.clear()
            #calculate all the fitnesses, add to mating pool
            for i in range(len(self.population)):
                p = self.population[i]
                #make array of opponents
                opponents = []
                if debugging:
                    print("Score is " + str(p.board.get_score()))
                #if the player's index is even, the opponent was at the player's index plus one
                if i % 2 == 0:
                    opponents.append(self.population[i + 1])
                    if debugging:
                        print("Opponents score is " + str(self.population[i + 1].board.get_score()))
                else:
                    opponents.append(self.population[i - 1])
                    if debugging:
                        print("Opponents score is " + str(self.population[i - 1].board.get_score()))
                fitness = p.calc_fitness(opponents)
                for i in range(fitness):
                    self.mating_pool.append(p)
                #check if fitness is a new record
                if fitness > self.best_fitness:
                    self.best_fitness = fitness
                    self.best_early = DNA(p.earlyDNA.genes)
                    self.best_late = DNA(p.lateDNA.genes)
                #adjust average score
                self.total_of_scores += p.board.get_score()
                self.total_scores += 1
                self.average_score = self.total_of_scores / self.total_scores
            if debugging:
                print("Mating pool size: " + str(len(self.mating_pool)))

            #now make new population
            self.population.clear()
            for i in range(self.population_size):
                #choose 2 random players that aren't the same
                p1 = choice(self.mating_pool)
                p2 = choice(self.mating_pool)
                while p1 == p2:
                    p2 = choice(self.mating_pool)
                child = p1.mate(p2)
                child.mutate(self.mutation_rate)
                self.population.append(child)

            if debugging:
                print("Population size: " + str(len(self.population)))
                print("")

            if self.display_window:
                #update the window
                self.update_window()
                self.master.update()

        

    def update_window(self):
        self.lbl_frame_labels[0]["text"] = "Generations: " + str(self.generations)
        self.lbl_frame_labels[1]["text"] = "Best fitness: " + str(self.best_fitness)
        self.lbl_frame_labels[2]["text"] = "Average score: " + str(self.average_score)
        self.lbl_frame_labels[5]["text"] = "horizontal preference: " + str(self.best_early.genes[0])
        self.lbl_frame_labels[6]["text"] = "highest to take (btwn 0 and 12): " + str(self.best_early.genes[1])
        self.lbl_frame_labels[7]["text"] = "highest to keep (btwn 0 and 12): " + str(self.best_early.genes[2])
        self.lbl_frame_labels[8]["text"] = "lowest to mitigate (btwn 0 and 12): " + str(self.best_early.genes[3])
        self.lbl_frame_labels[9]["text"] = "highest for -10 (btwn 0 and 12): " + str(self.best_early.genes[4])
        self.lbl_frame_labels[10]["text"] = "end (btwn 1 and 6): " + str(self.best_early.genes[5])
        self.lbl_frame_labels[11]["text"] = "highest to go out with (btwn -9 and 20): " + str(self.best_early.genes[6])
        self.lbl_frame_labels[13]["text"] = "horizontal preference: " + str(self.best_late.genes[0])
        self.lbl_frame_labels[14]["text"] = "highest to take (btwn 0 and 12): " + str(self.best_late.genes[1])
        self.lbl_frame_labels[15]["text"] = "highest to keep (btwn 0 and 12): " + str(self.best_late.genes[2])
        self.lbl_frame_labels[16]["text"] = "lowest to mitigate (btwn 0 and 12): " + str(self.best_late.genes[3])
        self.lbl_frame_labels[17]["text"] = "highest for -10 (btwn 0 and 12): " + str(self.best_late.genes[4])
        self.lbl_frame_labels[18]["text"] = "end (btwn 1 and 6): " + str(self.best_late.genes[5])
        self.lbl_frame_labels[19]["text"] = "highest to go out with (btwn -9 and 20): " + str(self.best_late.genes[6])



class Fights():
    def __init__(self, master, pool = None):
        #need to set up both actual evolution stuff and tkinter window stuff
        #fight stuff
        self.fighter = None
        self.total_fights = 0
        self.current_players_fights = 0
        self.most_wins = 0
        #maybe add a setting for what it's the best out of
        self.out_of = 5

        self.pool = pool

        #stuff for running it
        self.paused = True
        self.first_run = True

        #for stats
        self.best_early = DNA() #it's easier to just have it start as a random one
        self.best_late = DNA()

        #make the window
        self.master = master
        self.make_window()

        if isinstance(self.pool, Player):
            self.start()


    def make_window(self):
        #set up window basics
        self.stat_frm = tk.Frame(master = self.master, width=100, height=100)
        self.btn_frm = tk.Frame(master = self.master, width=100, height=100)
        self.title_lbl = tk.Label(master = self.master, text = "PlayNine Fights", fg = "black", width = 20, height = 3)
        #self.window.configure(background="white")
        # self.stat_frm.config(bg = "white")
        # self.btn_frm.config(bg = "white")
        # self.title_lbl.config(bg = "white")
        self.title_lbl.pack()
        #set up label frame
        self.lbl_frame_labels = []
        #total fights
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "Total Fights: 0"))
        #total players fights
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "Current player's fights: Waiting for first run"))
        #most wins
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "Most Wins: 0"))
        #best genes
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "Best genes:"))
        #early genes
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "Early:"))
        #horizontal preference (true or false)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "horizontal preference: Waiting for first run"))
        #highest to take (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "highest to take (btwn 0 and 12): Waiting for first run"))
        #highest to keep (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "highest to keep (btwn 0 and 12): Waiting for first run"))
        #lowest to mitigate (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "lowest to mitigate (btwn 0 and 12): Waiting for first run"))
        #highest for -10 (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "highest for -10 (btwn 0 and 12): Waiting for first run"))
        #end (btwn 1 and 6)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "end (btwn 1 and 6): Waiting for first run"))
        #highest to go out with (btwn -9 and 20)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "highest to go out with (btwn -9 and 20): Waiting for first run"))
        #late genes
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "Late:"))
        #horizontal preference (true or false)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "horizontal preference: Waiting for first run"))
        #highest to take (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "highest to take (btwn 0 and 12): Waiting for first run"))
        #highest to keep (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "highest to keep (btwn 0 and 12): Waiting for first run"))
        #lowest to mitigate (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "lowest to mitigate (btwn 0 and 12): Waiting for first run"))
        #highest for -10 (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "highest for -10 (btwn 0 and 12): Waiting for first run"))
        #end for -10 (btwn 1 and 6)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "end for -10 (btwn 1 and 6): Waiting for first run"))
        #highest to go out with (btwn -9 and 20)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "highest to go out with (btwn -9 and 20): Waiting for first run"))

        #add all labels to the frame
        for l in self.lbl_frame_labels:
            l.pack(anchor = "w")
            #l.config(bg = "white")
            if debugging:
                l.config(borderwidth=1, relief="solid")

        #set up button frame
        self.btn_frame_buttons = []
        #start button
        self.btn_frame_buttons.append(tk.Button(master = self.btn_frm, text = "Start", command = self.start))
        #stop button
        self.btn_frame_buttons.append(tk.Button(master = self.btn_frm, text = "Stop", command = self.stop))
        #load button
        self.btn_frame_buttons.append(tk.Button(master = self.btn_frm, text = "Load", command = self.load))
        #save button
        self.btn_frame_buttons.append(tk.Button(master = self.btn_frm, text = "Save", command = self.save))

        #add all buttons to the frame
        for b in self.btn_frame_buttons:
            b.pack()

        #add the frames to the window
        self.btn_frm.pack(fill=tk.BOTH, side=tk.RIGHT)
        self.stat_frm.pack(fill=tk.BOTH, side=tk.RIGHT)


    def start(self):
        #start button
        if debugging:
            print("Start button pressed")
        #make paused false, call run
        self.paused = False
        self.run()

    def stop(self):
        #stop button
        if debugging:
            print("Stop button pressed")
        #make paused true
        self.paused = True


    def load(self):
        #load button
        if debugging:
            print("Load button pressed")
        with open(filedialog.askopenfilename(defaultextension = ".txt", initialdir = "Saves/Players"), 'r') as reader:
            #load in general stats
            self.total_fights = int(reader.readline().strip())
            self.current_players_fights = int(reader.readline().strip())
            self.most_wins = int(reader.readline().strip())
            #now need to load in best genes
            new_best_early = []
            new_best_late = []
            genes = reader.readline().split(",")
            early = genes[0].split("/")
            late = genes[1].split("/")
            new_best_early.append(early[0] == "True")
            for i in range(6):
                new_best_early.append(int(early[i + 1]))
            #do the same for late
            new_best_late.append(late[0] == "True")
            for i in range(6):
                new_best_late.append(int(late[i + 1]))
        self.best_early.genes = new_best_early
        self.best_late.genes = new_best_late
        self.fighter = Player(DNA(new_best_early), DNA(new_best_late))
        self.update_window()
        if debugging:
            print("File read")


    def save(self):
        #save button
        if debugging:
            print("Save button pressed")
        with open(filedialog.asksaveasfilename(defaultextension = ".txt", initialdir = "Saves/Players"), 'w') as writer:
            writer.write(str(self.total_fights) + "\n")
            writer.write(str(self.current_players_fights) + "\n")
            writer.write(str(self.most_wins) + "\n")
            #now need to save best stats
            line = ""
            for g in self.best_early.genes:
                line += str(g) + "/"
            line += ","
            for g in self.best_late.genes:
                line += str(g) + "/"
            line += "\n"
            writer.write(line)


    def run(self):
        if self.first_run:
            self.fighter = Player()
        if isinstance(self.pool, Player) and self.first_run:
            self.fighter = self.pool
        self.first_run = False
        while not self.paused:
            winner = None
            #add one to generations
            self.total_fights += 1
            # self.current_players_fights += 1 #might change this again not sure
            #make the opponent
            if self.pool == None:
                opponent = Player()
            elif isinstance(self.pool, Player):
                opponent = self.pool
            else:
                opponent = choice(self.pool)
                opponent.mutate(0.01)
            #make the game and play it
            game = Game(False, debugging, self.fighter, opponent, self.out_of)
            game.play()
            if self.fighter.winner:
                winner = self.fighter
                self.current_players_fights += 1
                if debugging:
                    print("Fighter won")
            else:
                winner = opponent
                if debugging:
                    print("Opponent won")
                if self.current_players_fights > self.most_wins:
                    self.most_wins = self.current_players_fights
                    self.best_early = self.fighter.earlyDNA
                    self.best_late = self.fighter.lateDNA
                self.current_players_fights = 0
                    
            if debugging:
                print("Winner is: " + str(winner.code))
            #once there's a winner, do this
                
            self.fighter = winner#really winner var is not necessary

            #update the window
            self.update_window()
            self.master.update()

        

    def update_window(self):
        self.lbl_frame_labels[0]["text"] = "Total Fights: " + str(self.total_fights)
        self.lbl_frame_labels[1]["text"] = "Current Player's Fights: " + str(self.current_players_fights)
        self.lbl_frame_labels[2]["text"] = "Most Wins: " + str(self.most_wins)
        self.lbl_frame_labels[5]["text"] = "horizontal preference: " + str(self.best_early.genes[0])
        self.lbl_frame_labels[6]["text"] = "highest to take (btwn 0 and 12): " + str(self.best_early.genes[1])
        self.lbl_frame_labels[7]["text"] = "highest to keep (btwn 0 and 12): " + str(self.best_early.genes[2])
        self.lbl_frame_labels[8]["text"] = "lowest to mitigate (btwn 0 and 12): " + str(self.best_early.genes[3])
        self.lbl_frame_labels[9]["text"] = "highest for -10 (btwn 0 and 12): " + str(self.best_early.genes[4])
        self.lbl_frame_labels[10]["text"] = "end (btwn 1 and 6): " + str(self.best_early.genes[5])
        self.lbl_frame_labels[11]["text"] = "highest to go out with (btwn -9 and 20): " + str(self.best_early.genes[6])
        self.lbl_frame_labels[13]["text"] = "horizontal preference: " + str(self.best_late.genes[0])
        self.lbl_frame_labels[14]["text"] = "highest to take (btwn 0 and 12): " + str(self.best_late.genes[1])
        self.lbl_frame_labels[15]["text"] = "highest to keep (btwn 0 and 12): " + str(self.best_late.genes[2])
        self.lbl_frame_labels[16]["text"] = "lowest to mitigate (btwn 0 and 12): " + str(self.best_late.genes[3])
        self.lbl_frame_labels[17]["text"] = "highest for -10 (btwn 0 and 12): " + str(self.best_late.genes[4])
        self.lbl_frame_labels[18]["text"] = "end (btwn 1 and 6): " + str(self.best_late.genes[5])
        self.lbl_frame_labels[19]["text"] = "highest to go out with (btwn -9 and 20): " + str(self.best_late.genes[6])



class Head_2_Head:
    def __init__(self, master):
        self.master = master
        self.player1 = Player()
        self.player2 = Player()
        self.total_games = 0
        self.player1_wins = 0
        self.player2_wins = 0
        self.paused = True
        self.make_window()

    def make_window(self):
        #set up window basics
        self.stat_frm = tk.Frame(master = self.master, width=100, height=100)
        self.p1_frm = tk.Frame(master = self.stat_frm, width=100, height=100)
        self.p2_frm = tk.Frame(master = self.stat_frm, width=100, height=100)
        self.btn_frm = tk.Frame(master = self.master, width=100, height=100)
        self.title_lbl = tk.Label(master = self.master, text = "PlayNine Head 2 Head", fg = "black", width = 20, height = 3)
        #self.window.configure(background="white")
        # self.stat_frm.config(bg = "white")
        # self.btn_frm.config(bg = "white")
        # self.title_lbl.config(bg = "white")
        self.title_lbl.pack(anchor = "center")
        #set up label frame
        self.lbl_frame_labels = []
        #total games
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "Total Games: 0"))
        #p1 wins
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "Player 1 wins: 0"))
        #p2 wins
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "Player 2 wins: 0"))
        #p1 genes
        self.lbl_frame_labels.append(tk.Label(self.p1_frm, text = "Player 1's genes:"))
        #early genes
        self.lbl_frame_labels.append(tk.Label(self.p1_frm, text = "Early:"))
        #horizontal preference (true or false)
        self.lbl_frame_labels.append(tk.Label(self.p1_frm, text = "horizontal preference: Waiting for first run"))
        #highest to take (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.p1_frm, text = "highest to take (btwn 0 and 12): Waiting for first run"))
        #highest to keep (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.p1_frm, text = "highest to keep (btwn 0 and 12): Waiting for first run"))
        #lowest to mitigate (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.p1_frm, text = "lowest to mitigate (btwn 0 and 12): Waiting for first run"))
        #highest for -10 (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.p1_frm, text = "highest for -10 (btwn 0 and 12): Waiting for first run"))
        #end (btwn 1 and 6)
        self.lbl_frame_labels.append(tk.Label(self.p1_frm, text = "end (btwn 1 and 6): Waiting for first run"))
        #highest to go out with (btwn -9 and 20)
        self.lbl_frame_labels.append(tk.Label(self.p1_frm, text = "highest to go out with (btwn -9 and 20): Waiting for first run"))
        #late genes
        self.lbl_frame_labels.append(tk.Label(self.p1_frm, text = "Late:"))
        #horizontal preference (true or false)
        self.lbl_frame_labels.append(tk.Label(self.p1_frm, text = "horizontal preference: Waiting for first run"))
        #highest to take (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.p1_frm, text = "highest to take (btwn 0 and 12): Waiting for first run"))
        #highest to keep (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.p1_frm, text = "highest to keep (btwn 0 and 12): Waiting for first run"))
        #lowest to mitigate (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.p1_frm, text = "lowest to mitigate (btwn 0 and 12): Waiting for first run"))
        #highest for -10 (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.p1_frm, text = "highest for -10 (btwn 0 and 12): Waiting for first run"))
        #end for -10 (btwn 1 and 6)
        self.lbl_frame_labels.append(tk.Label(self.p1_frm, text = "end for -10 (btwn 1 and 6): Waiting for first run"))
        #highest to go out with (btwn -9 and 20)
        self.lbl_frame_labels.append(tk.Label(self.p1_frm, text = "highest to go out with (btwn -9 and 20): Waiting for first run"))
        #p2 genes
        self.lbl_frame_labels.append(tk.Label(self.p2_frm, text = "Player 2's genes:"))
        #early genes
        self.lbl_frame_labels.append(tk.Label(self.p2_frm, text = "Early:"))
        #horizontal preference (true or false)
        self.lbl_frame_labels.append(tk.Label(self.p2_frm, text = "horizontal preference: Waiting for first run"))
        #highest to take (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.p2_frm, text = "highest to take (btwn 0 and 12): Waiting for first run"))
        #highest to keep (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.p2_frm, text = "highest to keep (btwn 0 and 12): Waiting for first run"))
        #lowest to mitigate (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.p2_frm, text = "lowest to mitigate (btwn 0 and 12): Waiting for first run"))
        #highest for -10 (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.p2_frm, text = "highest for -10 (btwn 0 and 12): Waiting for first run"))
        #end (btwn 1 and 6)
        self.lbl_frame_labels.append(tk.Label(self.p2_frm, text = "end (btwn 1 and 6): Waiting for first run"))
        #highest to go out with (btwn -9 and 20)
        self.lbl_frame_labels.append(tk.Label(self.p2_frm, text = "highest to go out with (btwn -9 and 20): Waiting for first run"))
        #late genes
        self.lbl_frame_labels.append(tk.Label(self.p2_frm, text = "Late:"))
        #horizontal preference (true or false)
        self.lbl_frame_labels.append(tk.Label(self.p2_frm, text = "horizontal preference: Waiting for first run"))
        #highest to take (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.p2_frm, text = "highest to take (btwn 0 and 12): Waiting for first run"))
        #highest to keep (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.p2_frm, text = "highest to keep (btwn 0 and 12): Waiting for first run"))
        #lowest to mitigate (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.p2_frm, text = "lowest to mitigate (btwn 0 and 12): Waiting for first run"))
        #highest for -10 (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.p2_frm, text = "highest for -10 (btwn 0 and 12): Waiting for first run"))
        #end for -10 (btwn 1 and 6)
        self.lbl_frame_labels.append(tk.Label(self.p2_frm, text = "end for -10 (btwn 1 and 6): Waiting for first run"))
        #highest to go out with (btwn -9 and 20)
        self.lbl_frame_labels.append(tk.Label(self.p2_frm, text = "highest to go out with (btwn -9 and 20): Waiting for first run"))

        #add all labels to the frame
        for i in range(len(self.lbl_frame_labels)):
            if i < 3:
                self.lbl_frame_labels[i].pack(anchor = "center")
            else:
                self.lbl_frame_labels[i].pack(anchor = "w")
            #l.config(bg = "white")
            if debugging:
                l.config(borderwidth=1, relief="solid")

        #set up button frame
        self.btn_frame_buttons = []
        #start button
        self.btn_frame_buttons.append(tk.Button(master = self.btn_frm, text = "Start", command = self.start))
        #stop button
        self.btn_frame_buttons.append(tk.Button(master = self.btn_frm, text = "Stop", command = self.stop))
        #load button
        self.btn_frame_buttons.append(tk.Button(master = self.btn_frm, text = "Load P1", command = self.load1))
        #save button
        self.btn_frame_buttons.append(tk.Button(master = self.btn_frm, text = "Load P2", command = self.load2))

        #add all buttons to the frame
        for b in self.btn_frame_buttons:
            b.pack()

        #add the frames to the window
        self.btn_frm.pack(fill=tk.BOTH, side=tk.RIGHT)
        self.stat_frm.pack(fill=tk.BOTH, side=tk.RIGHT)
        self.p1_frm.pack(fill=tk.BOTH, side=tk.LEFT)
        self.p2_frm.pack(fill=tk.BOTH, side=tk.LEFT)


    def start(self):
        #start button
        if debugging:
            print("Start button pressed")
        #make paused false, call run
        self.paused = False
        self.run()

    def stop(self):
        #stop button
        if debugging:
            print("Stop button pressed")
        #make paused true
        self.paused = True


    def load1(self):
        #load button
        if debugging:
            print("Load button pressed")
        #reset stats
        self.total_games = 0
        self.player1_wins = 0
        self.player2_wins = 0
        with open(filedialog.askopenfilename(defaultextension = ".txt", initialdir = "Saves/Players"), 'r') as reader:
            #skip general stats
            for i in range(3):
                reader.readline()
            #now need to load in the genes
            new_early = []
            new_late = []
            genes = reader.readline().split(",")
            early = genes[0].split("/")
            late = genes[1].split("/")
            new_early.append(early[0] == "True")
            for i in range(6):
                new_early.append(int(early[i + 1]))
            #do the same for late
            new_late.append(late[0] == "True")
            for i in range(6):
                new_late.append(int(late[i + 1]))
        self.player1 = Player(DNA(new_early), DNA(new_late))
        self.update_window()
        if debugging:
            print("File read")


    def load2(self):
        #load button
        if debugging:
            print("Load button pressed")
        #reset stats
        self.total_games = 0
        self.player1_wins = 0
        self.player2_wins = 0
        with open(filedialog.askopenfilename(defaultextension = ".txt", initialdir = "Saves/Players"), 'r') as reader:
            #skip general stats
            for i in range(3):
                reader.readline()
            #now need to load in the genes
            new_early = []
            new_late = []
            genes = reader.readline().split(",")
            early = genes[0].split("/")
            late = genes[1].split("/")
            new_early.append(early[0] == "True")
            for i in range(6):
                new_early.append(int(early[i + 1]))
            #do the same for late
            new_late.append(late[0] == "True")
            for i in range(6):
                new_late.append(int(late[i + 1]))
        self.player2 = Player(DNA(new_early), DNA(new_late))
        self.update_window()
        if debugging:
            print("File read")


    def run(self):
        while not self.paused:
            #make the game
            game = Game(False, debugging, self.player1, self.player2)
            #play the game
            game.play()
            #add to total games
            self.total_games += 1
            #see who won
            if self.player1.winner:
                self.player1_wins += 1
            elif self.player2.winner:
                self.player2_wins += 1
            #update the window
            self.update_window()
            self.master.update()


    def update_window(self):
        self.lbl_frame_labels[0]["text"] = "Total Games: " + str(self.total_games)
        if self.total_games == 0:
            self.lbl_frame_labels[1]["text"] = "Player 1 wins: 0"
            self.lbl_frame_labels[2]["text"] = "Player 2 wins: 0"
        else:
            self.lbl_frame_labels[1]["text"] = "Player 1 wins: " + str(self.player1_wins) + " (" + str(round((self.player1_wins / self.total_games * 100))) + "%)"
            self.lbl_frame_labels[2]["text"] = "Player 2 wins: " + str(self.player2_wins) + " (" + str(round((self.player2_wins / self.total_games * 100))) + "%)"
        self.lbl_frame_labels[5]["text"] = "horizontal preference: " + str(self.player1.earlyDNA.genes[0])
        self.lbl_frame_labels[6]["text"] = "highest to take (btwn 0 and 12): " + str(self.player1.earlyDNA.genes[1])
        self.lbl_frame_labels[7]["text"] = "highest to keep (btwn 0 and 12): " + str(self.player1.earlyDNA.genes[2])
        self.lbl_frame_labels[8]["text"] = "lowest to mitigate (btwn 0 and 12): " + str(self.player1.earlyDNA.genes[3])
        self.lbl_frame_labels[9]["text"] = "highest for -10 (btwn 0 and 12): " + str(self.player1.earlyDNA.genes[4])
        self.lbl_frame_labels[10]["text"] = "end (btwn 1 and 6): " + str(self.player1.earlyDNA.genes[5])
        self.lbl_frame_labels[11]["text"] = "highest to go out with (btwn -9 and 20): " + str(self.player1.earlyDNA.genes[6])
        self.lbl_frame_labels[13]["text"] = "horizontal preference: " + str(self.player1.lateDNA.genes[0])
        self.lbl_frame_labels[14]["text"] = "highest to take (btwn 0 and 12): " + str(self.player1.lateDNA.genes[1])
        self.lbl_frame_labels[15]["text"] = "highest to keep (btwn 0 and 12): " + str(self.player1.lateDNA.genes[2])
        self.lbl_frame_labels[16]["text"] = "lowest to mitigate (btwn 0 and 12): " + str(self.player1.lateDNA.genes[3])
        self.lbl_frame_labels[17]["text"] = "highest for -10 (btwn 0 and 12): " + str(self.player1.lateDNA.genes[4])
        self.lbl_frame_labels[18]["text"] = "end (btwn 1 and 6): " + str(self.player1.lateDNA.genes[5])
        self.lbl_frame_labels[19]["text"] = "highest to go out with (btwn -9 and 20): " + str(self.player1.lateDNA.genes[6])
        self.lbl_frame_labels[22]["text"] = "horizontal preference: " + str(self.player2.earlyDNA.genes[0])
        self.lbl_frame_labels[23]["text"] = "highest to take (btwn 0 and 12): " + str(self.player2.earlyDNA.genes[1])
        self.lbl_frame_labels[24]["text"] = "highest to keep (btwn 0 and 12): " + str(self.player2.earlyDNA.genes[2])
        self.lbl_frame_labels[25]["text"] = "lowest to mitigate (btwn 0 and 12): " + str(self.player2.earlyDNA.genes[3])
        self.lbl_frame_labels[26]["text"] = "highest for -10 (btwn 0 and 12): " + str(self.player2.earlyDNA.genes[4])
        self.lbl_frame_labels[27]["text"] = "end (btwn 1 and 6): " + str(self.player2.earlyDNA.genes[5])
        self.lbl_frame_labels[28]["text"] = "highest to go out with (btwn -9 and 20): " + str(self.player2.earlyDNA.genes[6])
        self.lbl_frame_labels[30]["text"] = "horizontal preference: " + str(self.player2.lateDNA.genes[0])
        self.lbl_frame_labels[31]["text"] = "highest to take (btwn 0 and 12): " + str(self.player2.lateDNA.genes[1])
        self.lbl_frame_labels[32]["text"] = "highest to keep (btwn 0 and 12): " + str(self.player2.lateDNA.genes[2])
        self.lbl_frame_labels[33]["text"] = "lowest to mitigate (btwn 0 and 12): " + str(self.player2.lateDNA.genes[3])
        self.lbl_frame_labels[34]["text"] = "highest for -10 (btwn 0 and 12): " + str(self.player2.lateDNA.genes[4])
        self.lbl_frame_labels[35]["text"] = "end (btwn 1 and 6): " + str(self.player2.lateDNA.genes[5])
        self.lbl_frame_labels[36]["text"] = "highest to go out with (btwn -9 and 20): " + str(self.player2.lateDNA.genes[6])





class WindowManager: #This class and the instances of it are copied and pasted from SimKev2 on stack overflow
    def __init__(self):
        self._handle = None

    def _window_enum_callback( self, hwnd, wildcard ):
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) != None:
            self._handle = hwnd

    #CASE SENSITIVE
    def find_window_wildcard(self, wildcard):
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def set_foreground(self):
        win32gui.ShowWindow(self._handle, win32con.SW_RESTORE)
        win32gui.SetWindowPos(self._handle,win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)  
        win32gui.SetWindowPos(self._handle,win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)  
        win32gui.SetWindowPos(self._handle,win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_SHOWWINDOW + win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
        #shell = win32com.client.Dispatch("WScript.Shell")
        #shell.SendKeys('%')           turns out this is not needed, and when I have it in it makes windows diplay numlock icon (but not change numlock)
        win32gui.SetForegroundWindow(self._handle)

    def find_and_set(self, search):
        self.find_window_wildcard(search)
        self.set_foreground()



class Main_Window:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.evolution = tk.Button(self.frame, text = "Evolution", width = 15, height = 2, command = self.evolution_button)
        self.evolution.pack()
        self.fight = tk.Button(self.frame, text = "Fight", width = 15, height = 2, command = self.fight_button)
        self.fight.pack()
        self.head2head = tk.Button(self.frame, text = "Head 2 Head", width = 15, height = 2, command = self.head2head_button)
        self.head2head.pack()
        self.play_round = tk.Button(self.frame, text = "Play Round", width = 15, height = 2, command = self.play_round_button)
        self.play_round.pack()
        self.play_game = tk.Button(self.frame, text = "Play Nine", width = 15, height = 2, command = self.play_game_button)
        self.play_game.pack()
        self.frame.pack()
        self.new_window = None
        self.game = None


    def evolution_button(self):
        self.new_window = tk.Toplevel(self.master)
        self.new_window.protocol("WM_DELETE_WINDOW", self.window_closed)
        self.master.withdraw()
        ev = Evolution(self.new_window)

    def fight_button(self):
        self.new_window = tk.Toplevel(self.master)
        self.new_window.protocol("WM_DELETE_WINDOW", self.window_closed)
        self.master.withdraw()
        ft = Fights(self.new_window)

    def head2head_button(self):
        self.new_window = tk.Toplevel(self.master)
        self.new_window.protocol("WM_DELETE_WINDOW", self.window_closed)
        self.master.withdraw()
        h2h = Head_2_Head(self.new_window)

    def play_round_button(self):
        self.game = False
        self.new_window = tk.Toplevel(self.master)
        self.new_window.protocol("WM_DELETE_WINDOW", self.window_closed)
        label = tk.Label(self.new_window, text = "Do you want to load your opponent? (If not opponent will be random)")
        label.pack()
        yes = tk.Button(self.new_window, text = "Yes", width = 15, height = 2, command = self.yes_button)
        yes.pack()
        no = tk.Button(self.new_window, text = "No", width = 15, height = 2, command = self.no_button)
        no.pack()
        self.master.withdraw()

    def play_game_button(self):
        self.game = True
        self.new_window = tk.Toplevel(self.master)
        self.new_window.protocol("WM_DELETE_WINDOW", self.window_closed)
        label = tk.Label(self.new_window, text = "Do you want to load your opponent? (If not opponent will be random)")
        label.pack()
        yes = tk.Button(self.new_window, text = "Yes", width = 15, height = 2, command = self.yes_button)
        yes.pack()
        no = tk.Button(self.new_window, text = "No", width = 15, height = 2, command = self.no_button)
        no.pack()
        self.master.withdraw()

    def yes_button(self):
        self.new_window.destroy()
        #load opponent
        with open(filedialog.askopenfilename(defaultextension = ".txt", initialdir = "Saves/Players"), 'r') as reader:
            for i in range(3):
                reader.readline()
            earlyDNA = []
            lateDNA = []
            genes = reader.readline().split(",")
            early = genes[0].split("/")
            late = genes[1].split("/")
            earlyDNA.append(early[0] == "True")
            for i in range(6):
                earlyDNA.append(int(early[i + 1]))
            #do the same for late
            lateDNA.append(late[0] == "True")
            for i in range(6):
                lateDNA.append(int(late[i + 1]))
        #give focus to cmd
        w = WindowManager()
        w.find_and_set(".*cmd.exe*")
        #now make and play the game
        game = Game(True, True, User(), Player(DNA(earlyDNA), DNA(lateDNA)))
        if self.game:
            game.play()
        else:
            game.play_round()
        self.master.deiconify()

    def no_button(self):
        self.new_window.destroy()
        #give focus to cmd
        w = WindowManager()
        w.find_and_set(".*cmd.exe*")
        game = Game(True, True, User(), Player())
        if self.game:
            game.play()
        else:
            game.play_round()
        self.master.deiconify()

    def window_closed(self):
        self.new_window.destroy()
        self.master.deiconify()



def main(): 
    root = tk.Tk()
    app = Main_Window(root)
    root.mainloop()

if __name__ == '__main__':
    main()





"""
Known bugs:
None so far!

What I have left to do:
Just maybe add tournament

Other idea:
Add in tournament style version
"""