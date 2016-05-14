"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

## george's version for hangman

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb

# put possible choice for wordlist here
WORDLIST = ['apple', 'orange','watermelon',
            'papaya','raspberry', 'cucumber']

class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()


class Game(ndb.Model):
    """Game object"""

    target = ndb.StringProperty(required=True)
    attempts_allowed = ndb.IntegerProperty(required=True, default=10)
    attempts_remaining = ndb.IntegerProperty(required=True, default=10)
    game_over = ndb.BooleanProperty(required=True, default=False)
    cancelled = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    # since users have to be unique, can i use user for ancestor query?
    organizerUserId = ndb.StringProperty()
    guess_history = ndb.StringProperty(repeated=True)
    guess_state = ndb.StringProperty(repeated=True)


    @classmethod
    def new_game(cls, user, min, max, attempts):
        """Creates and returns a new game"""

        ## todo: remove max min vars from method and arguments
        if max < min:
            raise ValueError('Maximum must be greater than minimum')
        game = Game(user=user,
                    target=random.choice(WORDLIST),
                    attempts_allowed=attempts,
                    attempts_remaining=attempts,
                    game_over=False)
        game.set_guess_state()
        game.put()
        return game

    def set_guess_state(self):
        """init the guess state display"""
        g = []
        for letter in self.target:
            g.append("_")
        self.guess_state = g

    def update_guess_state(self, letter):
        """update letter in word display"""
        for i in range(len(self.target)):
            if letter == self.target[i]:
                self.guess_state[i] = letter
        self.put()


    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.attempts_remaining = self.attempts_remaining
        form.game_over = self.game_over
        form.message = message
        # guess_state is a list, convert to string
        form.guess_state = ' '.join(self.guess_state)
        return form

    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.put()
        # Add the game to the score 'board'
        score = Score(user=self.user, date=date.today(), won=won,
                      guesses=self.attempts_allowed - self.attempts_remaining)
        score.put()


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    guesses = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name, won=self.won,
                         date=str(self.date), guesses=self.guesses)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    attempts_remaining = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    user_name = messages.StringField(5, required=True)
    guess_state = messages.StringField(6, required=True)


## for get_user_games
class GameForms(messages.Message):
    """Return multiple GameForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)


## won't need min max, but could enter words?
class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    min = messages.IntegerField(2, default=1)
    max = messages.IntegerField(3, default=10)
    attempts = messages.IntegerField(4, default=10)

class CancelGameForm(messages.Message):
    """Enter 1 to cancel a game"""
    cancel = messages.BooleanField(1, default=False, required=True)


## implement separate guess letter, guess word
class MakeMoveForm(messages.Message):
    """Used to make a move, (Guess a letter) in an existing game"""
    guess = messages.StringField(1, required=True)


class GuessWordForm(messages.Message):
    """Used to guess the word in the current game"""
    guess = messages.StringField(1, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    guesses = messages.IntegerField(4, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
