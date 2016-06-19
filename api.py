# -*- coding: utf-8 -*-`
"""api.py -  Create, configure and operate a hangman game"""

import logging
import endpoints
from operator import itemgetter, attrgetter, methodcaller

from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import User, Game, Score, Guess
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    ScoreForms, GuessWordForm, CancelGameForm, GameForms, GameHistoryForm,\
    GuessForm, GuessHistoryForms, HighScoreForm, GameHistoryForm, \
    RankForm, RankForms
from utils import get_by_urlsafe

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)

CANCEL_GAME_REQUEST = endpoints.ResourceContainer(
  urlsafe_game_key=messages.StringField(1),)

GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)

MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)

GUESS_WORD_REQUEST = endpoints.ResourceContainer(
    GuessWordForm,
    urlsafe_game_key=messages.StringField(1),)

USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))

HI_SCORE_REQUEST = endpoints.ResourceContainer(HighScoreForm)

MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'

# rename guess number to hangman


@endpoints.api(name='hangman', version='v1')
class GuessANumberApi(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        try:
            game = Game.new_game(user.key, request.attempts)
        except ValueError:
            raise endpoints.BadRequestException('Username required!')

        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        taskqueue.add(url='/tasks/cache_average_attempts')
        return game.to_form('Good luck playing Hangman!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/make_move/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """endpoint to guess a letter"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        guess_obj = Guess(guess=request.guess, msg="")

        if game.game_over:
            raise endpoints.ForbiddenException('Illegal action: Game is already over.')

        guess_obj.guess_num = 1 + len(game.guess_history)
        guess_obj.word_state = ' '.join(game.guess_state)

        # check if isalpha
        if request.guess.isalpha() == False:
            raise endpoints.ForbiddenException('Illegal action: Letters only.')

        if request.guess == game.target:
            print "hooray! you win"

        #  check guess is one letter only
        if len(request.guess) != 1:
            msg = 'One letter at a time please, guess again.'
            guess_obj.msg = msg
            game.guess_hist_obj.append(guess_obj)
            game.put()
            return game.to_form(msg)

        # check if guess is already in history
        if request.guess in game.guess_history:
            msg = 'You already tried that, guess again.'
            guess_obj.msg = msg

        game.guess_history.append(request.guess)

        if request.guess in game.target:
            msg = 'The word contains your letter!'
            game.update_guess_state(request.guess)
            guess_obj.word_state = ' '.join(game.guess_state)
        else:
            msg = 'Letter not in word.'
            game.attempts_remaining -= 1

        if game.target == ''.join(game.guess_state):
            game.end_game(True)
            msg = 'You guessed all the letters, you win!'
            guess_obj.msg = msg
            game.guess_hist_obj.append(guess_obj)
            game.put()
            return game.to_form(msg)

        if game.attempts_remaining < 1:
            game.end_game(False)
            guess_obj.msg = msg + ' Game over!'
            game.guess_hist_obj.append(guess_obj)
            game.put()
            return game.to_form(msg + ' Game over!')
        else:
            guess_obj.msg = msg
            game.guess_hist_obj.append(guess_obj)
            game.put()
            return game.to_form(msg)

    @endpoints.method(request_message=GUESS_WORD_REQUEST,
                      response_message=GameForm,
                      path='game/guess_word/{urlsafe_game_key}',
                      name='guess_word',
                      http_method='PUT')
    def guess_word(self, request):
        """endpoint to guess a word"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            return game.to_form('Game already over!')

        guess_obj = Guess(guess=request.guess, msg="")

        game.attempts_remaining -= 1
        guess_obj.guess_num = 1 + len(game.guess_history)
        guess_obj.word_state = ' '.join(game.guess_state)

        if request.guess in game.guess_history:
            msg = 'You already tried that word, guess again.'
            guess_obj.msg = msg

        game.guess_history.append(request.guess)

        if request.guess == game.target:
            msg = "You guessed the word, you win!"
            game.update_guess_state(request.guess)
            guess_obj.msg = msg
            game.guess_hist_obj.append(guess_obj)
            game.end_game(True)
            game.put()
            return game.to_form(msg)
        else:
            game.update_guess_state(request.guess)
            msg = "That's not the word."

        if game.attempts_remaining < 1:
            game.end_game(True)
            guess_obj.msg = msg
            game.guess_hist_obj.append(msg + ' Game over!')
            game.put()
            return game.to_form(msg + ' Game over!')
        else:
            guess_obj.msg = msg
            game.guess_hist_obj.append(guess_obj)
            game.put()
            return game.to_form(msg)

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(response_message=StringMessage,
                      path='games/average_attempts',
                      name='get_average_attempts_remaining',
                      http_method='GET')
    def get_average_attempts(self, request):
        """Get the cached average moves remaining"""
        return StringMessage(message=memcache.get(MEMCACHE_MOVES_REMAINING) or '')

## new endpoints

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='games/user/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Returns all of an individual User's active games"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        games = Game.query(Game.user == user.key, Game.game_over == False)
        return GameForms(items=[game.to_form("") for game in games])

    @endpoints.method(request_message=CANCEL_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/cancel_game/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='DELETE')
    def cancel_game(self, request):
        """cancel a game in progress"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            return game.to_form("Game already over, can't cancel!")
        else:
            game.key.delete()
            return game.to_form("Game Deleted.")

    @endpoints.method(request_message=HI_SCORE_REQUEST,
                      response_message=ScoreForms,
                      path='high_scores',
                      name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
        """get_high_scores, filter by top 10 add
        request_message with optional number to results
        order by guess, descendng, and game_over = True"""
        ng = request.top_n_games
        print "number of games: ", ng

        high_scores=[score.to_form() for
          score in Score.query(Score.won == True).order(Score.guesses).fetch(ng)]

        return ScoreForms(items=high_scores)

    @endpoints.method(response_message=RankForms,
                      path='ranks',
                      name='get_ranks',
                      http_method='GET')
    def get_ranks(self, request):
        """Return rankings of players based on average guesses"""
        users = User.query().fetch()
        ranks = []

        for user in users:
            games = Score.query(Score.user == user.key).fetch()
            if len(games) != 0:
                total_guesses = sum([g.guesses for g in games])
                print total_guesses
                avg_guesses = float(total_guesses) / len(games)
                rankform = RankForm(user = user.name,
                    avg_guesses = avg_guesses)
                ranks.append(rankform)

        s = sorted(ranks, key=attrgetter('avg_guesses') )
        return RankForms(items=s)

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GuessHistoryForms,
                      path='game_history/{urlsafe_game_key}',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return the move history of the game."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            history = [GuessForm(message=g.msg, move=g.guess,
                                word_state=g.word_state,
                                guess_num=g.guess_num) for g in game.guess_hist_obj]
            return GuessHistoryForms(items=history)
        else:
            raise endpoints.NotFoundException('Game not found!')

    @staticmethod
    def _cache_average_attempts():
        """Populates memcache with the average moves remaining of Games"""
        games = Game.query(Game.game_over == False).fetch()
        if games:
            count = len(games)
            total_attempts_remaining = sum([game.attempts_remaining
                                        for game in games])
            average = float(total_attempts_remaining)/count
            memcache.set(MEMCACHE_MOVES_REMAINING,
                         'The average moves remaining is {:.2f}'.format(average))


api = endpoints.api_server([GuessANumberApi])
