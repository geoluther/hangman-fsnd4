"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

## george's version for hangman

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb

# put random choices for wordlist here
WORDLIST = ['apple', 'orange','watermelon',
            'papaya','raspberry', 'cucumber', 'rutabaga',
            'pineapple', 'jicama']

class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()


class Guess(ndb.Model):
    guess = ndb.StringProperty(required=True)
    msg = ndb.StringProperty(required=True)
    word_state = ndb.StringProperty(default="foo")
    guess_num = ndb.IntegerProperty(default=0)


class Game(ndb.Model):
    """Game object"""

    target = ndb.StringProperty(required=True)
    attempts_allowed = ndb.IntegerProperty(required=True, default=10)
    attempts_remaining = ndb.IntegerProperty(required=True, default=10)
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    guess_history = ndb.StringProperty(repeated=True)
    guess_hist_obj = ndb.StructuredProperty(Guess, repeated=True)
    guess_state = ndb.StringProperty(repeated=True)


    @classmethod
    def new_game(cls, user, attempts):
        """Creates and returns a new game"""
        game =Game(user=user,
                    target=random.choice(WORDLIST),
                    attempts_allowed=attempts,
                    attempts_remaining=attempts,
                    game_over=False)
        game._set_guess_state()
        game.put()
        return game

    def _set_guess_state(self):
        """init the guess state display"""
        g = []
        for letter in self.target:
            g.append("_")
        self.guess_state = g

    def update_guess_state(self, letter):
        """update letters in word display"""
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

    def return_history(self, message):
        form = GameHistoryForm()
        hist = [ m.msg + m.guess for m in self.guess_hist_obj]
        form.message = "You got the Moves"
        form.moves = "Like Jagger"
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
    def to_rank(self):
        return RankForm(user_name=self.user.get().name, won=self.won,
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


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    attempts = messages.IntegerField(4, default=10)


class CancelGameForm(messages.Message):
    """Cancel and Delete A Game"""
    cancel = messages.BooleanField(1, default=False, required=True)


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


class GameHistoryForm(messages.Message):
    """ move in a game's history"""
    message = messages.StringField(1, required=True)
    moves = messages.StringField(2, required=True)


class GuessForm(messages.Message):
    message = messages.StringField(1, required=True)
    move = messages.StringField(2, required=True)
    word_state = messages.StringField(3, default="foo")
    guess_num = messages.IntegerField(4, default=42)


class GameHistoryForms(messages.Message):
    items = messages.MessageField(GuessForm, 1, repeated=True)


class GuessHistoryForms(messages.Message):
    items = messages.MessageField(GuessForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)


class HighScoreForm(messages.Message):
    """enter Top N rankings to display, default = 5"""
    top_n_games = messages.IntegerField(1, required=True, default=5)


# Rank Forms
class RankForm(messages.Message):
    """User Name and average guesses"""
    user = messages.StringField(1, required=True)
    avg_guesses =  messages.FloatField(2, required=True)


class RankForms(messages.Message):
    """Users, sorted by lowest average guesses"""
    items = messages.MessageField(RankForm, 1, repeated=True)
