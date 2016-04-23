# hangman-skel
skele functions for hangman fsnd gae project


score: number of moves to guess word

get_user_games:
-- be sure to include
word guess state
number of guesses left
letters guessed


get_game_history:
[
('Guess': 'a', result: 'found', guess_state: "_ a _ a _ a _ "),
('Guess': 'w', result: 'not found', guess_state:"_ a _ a _ a _ "),
('Guess': 'bananas', result: 'Win. Game over')
]

Modify the SendReminderEmail handler so that this reminder email is only sent to users that have incomplete games.

