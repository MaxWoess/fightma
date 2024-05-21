from flask import Flask, request, render_template, redirect, url_for, flash
import pickle

app = Flask(__name__)
app.secret_key = 'your_secret_key'

class Fighter:
    def __init__(self, name, weight_class, wins=0, losses=0, ranking=None):
        self.name = name
        self.weight_class = weight_class
        self.wins = wins
        self.losses = losses
        self.ranking = ranking
        self.fight_history = []

    def update_stats(self, wins=None, losses=None, ranking=None):
        if wins is not None:
            self.wins = wins
        if losses is not None:
            self.losses = losses
        if ranking is not None:
            self.ranking = ranking

    def add_fight(self, opponent, result):
        self.fight_history.append((opponent, result))

    def sortable_ranking(self):
        if self.ranking == 'C':
            return (0,)
        elif isinstance(self.ranking, int):
            return (1, self.ranking)
        else:
            return (2,)

    def __str__(self):
        ranking = 'C' if self.ranking == 'C' else str(self.ranking)
        return f'{ranking}. {self.name}, Wins: {self.wins}, Losses: {self.losses}, Weight Class: {self.weight_class}'

class Championship:
    def __init__(self):
        self.fighters = []

    def add_fighter(self, name, weight_class, wins=0, losses=0, ranking=None):
        fighter = Fighter(name, weight_class, wins, losses, ranking)
        self.fighters.append(fighter)

    def delete_fighter(self, name, weight_class):
        fighter = self.find_fighter(name, weight_class)
        if fighter:
            self.fighters.remove(fighter)
            return True
        return False

    def find_fighter(self, name, weight_class):
        for fighter in self.fighters:
            if fighter.name == name and fighter.weight_class == weight_class:
                return fighter
        return None

    def update_fighter(self, name, weight_class, wins=None, losses=None, ranking=None):
        fighter = self.find_fighter(name, weight_class)
        if fighter:
            fighter.update_stats(wins, losses, ranking)
            return True
        return False

    def list_fighters(self, weight_class=None):
        self.fighters.sort(key=lambda x: (x.weight_class, x.sortable_ranking()))
        if weight_class:
            return [fighter for fighter in self.fighters if fighter.weight_class == weight_class]
        return self.fighters

    def save_to_file(self, filepath):
        with open(filepath, 'wb') as file:
            pickle.dump(self, file)

    @staticmethod
    def load_from_file(filepath):
        with open(filepath, 'rb') as file:
            return pickle.load(file)

championship = Championship()

@app.route('/')
def index():
    fighters = championship.list_fighters()
    return render_template('index.html', fighters=fighters)

@app.route('/add_fighter', methods=['GET', 'POST'])
def add_fighter():
    if request.method == 'POST':
        name = request.form['name']
        weight_class = request.form['weight_class']
        wins = int(request.form['wins'])
        losses = int(request.form['losses'])
        ranking = request.form['ranking']
        if ranking.isdigit():
            ranking = int(ranking)
        championship.add_fighter(name, weight_class, wins, losses, ranking)
        flash('Fighter added successfully!')
        return redirect(url_for('index'))
    return render_template('add_fighter.html')

@app.route('/edit_fighter/<name>/<weight_class>', methods=['GET', 'POST'])
def edit_fighter(name, weight_class):
    fighter = championship.find_fighter(name, weight_class)
    if not fighter:
        flash('Fighter not found!')
        return redirect(url_for('index'))

    if request.method == 'POST':
        wins = request.form['wins']
        losses = request.form['losses']
        ranking = request.form['ranking']
        wins = int(wins) if wins else None
        losses = int(losses) if losses else None
        ranking = int(ranking) if ranking.isdigit() else ranking if ranking == 'C' else None
        championship.update_fighter(name, weight_class, wins, losses, ranking)
        flash('Fighter updated successfully!')
        return redirect(url_for('index'))
    
    return render_template('edit_fighter.html', fighter=fighter)

@app.route('/delete_fighter/<name>/<weight_class>', methods=['POST'])
def delete_fighter(name, weight_class):
    if championship.delete_fighter(name, weight_class):
        flash('Fighter deleted successfully!')
    else:
        flash('Fighter not found!')
    return redirect(url_for('index'))

@app.route('/save', methods=['POST'])
def save_championship():
    filepath = request.form['filepath']
    championship.save_to_file(filepath)
    flash('Championship saved successfully!')
    return redirect(url_for('index'))

@app.route('/load', methods=['POST'])
def load_championship():
    filepath = request.form['filepath']
    global championship
    championship = Championship.load_from_file(filepath)
    flash('Championship loaded successfully!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
