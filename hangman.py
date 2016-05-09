## hangman game
## basic stand alone, **not** what the app runs
## todo: deal with whitespace

from random import choice

class Hangman():

    wordlist = ['apple', 'orange','banana',
                'mango', 'watermelon',
                'strawberry','canteloupe']

    def __init__(self, name):
        self.word = self._get_random_word()
        self.guesses_left = 10
        self.player = name
        self.display = self._make_display(self.word)
        self.guess_history = []


    def _get_random_word(self):
        return choice(self.wordlist)


    def guess_word(self, guess):
        if self.guesses_left < 1:
            print "Sorry, you are out of guesses"
            return
        self.guesses_left += -1
        self.guess_history.append(guess)

        response = "You guessed the word: {}".format(guess)
        if guess == self.word:
            print response + '\nYou guessed correctly!'
        else:
            print response + '\nGuess Again, that is not the correct word'

        self.report()
        return


    def guess_letter(self, letter):
        if self.guesses_left < 1:
            return "Sorry, you are out of guesses."

        if len(letter) != 1:
            return "Invalid guess, guess one letter at a time, try again."

        if letter in self.guess_history:
            return "You already guessed this letter, try again"

        self.guesses_left += -1
        self.guess_history.append(letter)

        if letter in self.word:

            print "{} is in the word".format(letter)
        else:
            print "{} is not in word".format(letter)

        self._update_display(letter)
        return


    def _update_display(self, letter):
        '''show letter in word display'''
        for i in range(len(self.word)):
            if letter == self.word[i]:
                self.display[i] = letter
        self.report()
        return


    def _make_display(self, secret_word):
        hidden_letters = []
        for i in range(len(secret_word)):
            if secret_word[i] == ' ':
                hidden_letters.append(' ')
            else:
                hidden_letters.append('_')
        return hidden_letters


    def _pretty_display(self):
        return ' '.join(self.display)


    def report(self):
        msg = "Player: {}\n"\
               + "Secret Word: {}\n"\
               + "Guess history: {}\n"\
               + "Guesses left: {}\n"\
               + "Letters and Words: {}"

        resp = msg.format(self.player,
                          self.word,
                          self.guess_history,
                          self.guesses_left,
                          self._pretty_display() )
        print resp


if __name__ == "__main__":
    game = Hangman("George")
    print "Welcome to Hangman"
    print "-----------------"
    game.report()


