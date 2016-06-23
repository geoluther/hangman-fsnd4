
### Reflect on Your Design

Document your design decisions by answering the following questions:

- What additional properties did you add to your models and why?
	- Game Model: I added _set_guess_state, and update_guess_state models to track
	what guesses the user had made, I also added the Guess model, to help track guesses,
	guess state, messages, and guess number for the current game. The Guess model is used when
	generating a game's history.
	- I also added a _return_history method to Game that returns all the moves and messages
	for the given game.

- What were some of the trade-offs or struggles you faced when implementing the new game logic?
	- While the guess_history, guess_hist_obj, and guess_state values are a bit redundant,
	they were convenient in the generation of move forms and the game history output.
	- Ancestor queries are still a bit murky for me, in calling the cron job to notify users for unfinished,
	games, I used multiple queries, whereas a simpler query that returned all users who had unfinished games would have been more elegant...
	- another struggle was separating guessing single letters vs. words, thanks to the reviewer feedback, i was able to add functionality for both in the same function.


- Note:
	- hangman.py file was a preliminary class to sketch out game logic before implementing into the api.




