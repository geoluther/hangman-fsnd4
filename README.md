# Full Stack Nanodegree Project 5: Hangman Game API

##Game Description:
In Hangman, the goal of theam is to guess the word by choosing one letter at a time
until the player can guess the full word, or when the max number of attempts are used.
Each game begins with a random 'word', with a maximum number of
'attempts'. 'Guesses' of letters are sent to the `make_move` endpoint which will reply
with either: 'letter in word', 'letter not in word, 'you already tried that letter',
or 'game over' (if the maximum number of attempts is reached). 'Guesses' by word return the same responses.
Players may only guess one letter or word at a time. The game keeps track of the current 'guess' state of the word.

Many different Hangman games can be played by many different Users at any
given time. Each game can be retrieved or played by using the path parameter
`urlsafe_game_key`.

## Score Keeping:
Games are scored and randed by the fewest number of guesses it takes a user to complete a game.
The game is lost if the user cannont guess the word in the required number of guesses.
Incorrect letter and incorrect word guesses count against the number of guesses.

##Endpoints:

 - **cancel_game**
	- Path: 'game/cancel_game/{urlsafe_game_key}''
    - Method: PUT
    - Parameters: urlsafe_game_key
    - Returns: StringMessage
    - Description: Cancels the game given, deleting it from the database.

 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will
    raise a ConflictException if a User with that user_name already exists.

 - **get_average_attempts_remaining**
 	- Path: 'games/average_attempts'
 	- Method: GET
 	- Parameters: None
 	- Returns: StringMessage
 	- Description: Get the cached average moves remaining

 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.

 - **get_game_history**
    - Path: 'game_history/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameHistoryForms
    - Description: Returns the move history GameHistoryForm for each move in the game, including
    the guess for each move and guess state.

 - **get_high_scores**
 	- Path: 'high_scores'
 	- Method: GET
 	- Parameters: top_n_games (default = 5)
 	- Returns: ScoreForms
 	- Description: Return high scores for number of games specified or default (5).

 - **get_ranks**
 	- Path: 'ranks'
 	- Method: GET
 	- Parameters: None
 	- Returns: RankForms
 	- Description: Return rankings of players based on average number of guesses from completed games.

 - **get_user_games**
	- Path: 'games/user/{user_name}'
	- Method: GET
	- Parameters: user_name
	- Returns: GameForms
	- Description: Returns all active Games for the provided player (unordered).
	Will raise a NotFoundException if the User does not exist.

 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms
    - Description: Returns all Scores for completed games recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.

(removed, make_move now checks words)
 - ~~**guess_word**~~
    ~~- Path: 'game/guess_word/{urlsafe_game_key}'~~
    - ~~Method: PUT~~
    - ~~Parameters: urlsafe_game_key, guess~~
    - ~~Returns: GameForm with new game state.~~

    - ~~Description: Accepts a word 'guess' and returns the updated state of the game.~~
      ~~If this causes a game to end, a corresponding Score entity will be created.~~

 - **make_move**
    - Path: 'game/make_move/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, guess
    - Returns: GameForm with new game state.
    - Description: Accepts a 'guess' of a single letter or a work and returns the updated state of the game, notifiying the user if the letter is in the word or the word guess was correct. If either incorrect, player will be penalized a move.
    If this causes a game to end, a corresponding Score entity will be created.

 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: attempts (default it 10)
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not. Also adds a task to a task queue to update the average moves remaining for active games.

##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.

 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.

 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.

 - **Guess**
 	- used as structered repeated property inside of the Game object.

##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, attempts_remaining,
    game_over flag, message, user_name).
 - **NewGameForm**
    - Used to create a new game (user_name, min, max, attempts)
 - **MakeMoveForm**
    - Inbound make move form (guess).
 - **ScoreForm**
    - Representation of a completed game's Score (user_name, date, won flag,
    guesses).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **StringMessage**
    - General purpose String container.
 - **RankForm**
    - Representation of a single player's rank
 - **RankForms**
    - Multiple RankForm container, sorted by highest rank (1 = highest)
 - **GameHistoryForm**
    - Representation of a move in a game.
 - **GameHistoryForms**
    - Full game history container of all moves in a game.
 - **GuessWordForm**
    - Used to create a word guess



