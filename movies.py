import json
from statistics import mean
from abc import ABC, abstractmethod
from termcolor import colored


class Movie:
    def __init__(self, title, rating=None, genre=None):
        self.title = title
        self.rating = rating
        self.genre = genre

    def to_dict(self):
        return {"rating": self.rating, "genre": self.genre}

    @staticmethod
    def from_dict(title, data):
        return Movie(title, data.get("rating"), data.get("genre"))


class User:
    def __init__(self, username):
        self.username = username
        self.movies = {}  # title -> Movie
        self.preferences = []

    def add_movie(self, title):
        if title not in self.movies:
            self.movies[title] = Movie(title)

    def rate_movie(self, title, rating):
        if title in self.movies:
            self.movies[title].rating = rating

    def set_genre(self, title, genre):
        if title in self.movies:
            self.movies[title].genre = genre

    def set_preferences(self, genres):
        self.preferences = [g.strip() for g in genres if g.strip()]

    def get_rated_movies(self):
        return [m for m in self.movies.values() if m.rating is not None]

    def to_dict(self):
        return {
            "movies": {title: m.to_dict() for title, m in self.movies.items()},
            "preferences": self.preferences
        }

    @staticmethod
    def from_dict(username, data):
        user = User(username)
        user.movies = {title: Movie.from_dict(title, m) for title, m in data["movies"].items()}
        user.preferences = data.get("preferences", [])
        return user


class Storage:
    @staticmethod
    def save(users, filename="movies_data.json"):
        with open(filename, "w") as f:
            json.dump({u.username: u.to_dict() for u in users.values()}, f, indent=4)
        print("Data saved.")

    @staticmethod
    def load(filename="movies_data.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                return {u: User.from_dict(u, d) for u, d in data.items()}
        except FileNotFoundError:
            print("No saved data.")
            return {}


class IRecommender(ABC):
    @abstractmethod
    def recommend(self, user, users):
        pass


class GenreRecommender(IRecommender):
    def recommend(self, user, users):
        prefs = user.preferences
        matches = [m for m in user.movies.values() if m.rating and m.genre in prefs]
        matches.sort(key=lambda m: m.rating, reverse=True)
        return matches


class UserSimilarityRecommender(IRecommender):
    def recommend(self, user, users):
        best_match = None
        best_score = -1

        for other in users.values():
            if other.username == user.username:
                continue

            score = sum(
                1 for t in user.movies
                if t in other.movies
                and user.movies[t].rating is not None
                and other.movies[t].rating is not None
                and abs(user.movies[t].rating - other.movies[t].rating) <= 2
            )

            if score > best_score:
                best_match = other
                best_score = score

        if not best_match:
            return []

        return sorted(
            [m for t, m in best_match.movies.items()
             if t not in user.movies or user.movies[t].rating is None and m.rating],
            key=lambda m: m.rating, reverse=True
        )[:5]


class MovieApp:
    def __init__(self):
        self.users = Storage.load()
        self.current_user = None

    def run(self):
        while True:
            print(f"\n--- Movie Recommender ---")
            print(f"Logged in as: {self.current_user.username}" if self.current_user else "Not logged in.")
            print("""1. Register
2. Login
3. Add Movie
4. Rate Movie
5. Set Genre
6. Set Preferences
7. Show Stats
8. Recommend by Genre
9. Recommend by Users
10. Save
11. Load
12. Exit""")

            choice = input("Choice: ").strip()
            match choice:
                case "1": self.register()
                case "2": self.login()
                case "3": self.guard(self.add_movie)
                case "4": self.guard(self.rate_movies)
                case "5": self.guard(self.set_genres)
                case "6": self.guard(self.set_preferences)
                case "7": self.guard(self.show_stats)
                case "8": self.guard(lambda: self.recommend(GenreRecommender()))
                case "9": self.guard(lambda: self.recommend(UserSimilarityRecommender()))
                case "10": Storage.save(self.users)
                case "11": self.users = Storage.load()
                case "12": break
                case _: print("Invalid.")

    def register(self):
        name = self.input_nonempty("New username: ")
        if name in self.users:
            print("User exists.")
        else:
            user = User(name)
            self.users[name] = user
            self.current_user = user
            print(f"User '{name}' registered and logged in.")

    def login(self):
        name = self.input_nonempty("Username: ")
        if name in self.users:
            self.current_user = self.users[name]
            print(f"Logged in as '{name}'")
        else:
            print("User not found.")

    def add_movie(self):
        while True:
            title = input("Movie title (or 'done'): ").strip()
            if title.lower() == "done":
                break
            self.current_user.add_movie(title)

    def rate_movies(self):
        for t, m in self.current_user.movies.items():
            try:
                r = int(input(f"Rate '{t}' (1-10): "))
                if 1 <= r <= 10:
                    self.current_user.rate_movie(t, r)
            except ValueError:
                print("Invalid number.")

    def set_genres(self):
        for t, m in self.current_user.movies.items():
            g = input(f"Genre for '{t}': ").strip()
            self.current_user.set_genre(t, g)

    def set_preferences(self):
        genres = input("Favorite genres (comma-separated): ").split(",")
        self.current_user.set_preferences(genres)

    def show_stats(self):
        rated = self.current_user.get_rated_movies()
        if not rated:
            print("No rated movies.")
            return

        avg = mean([m.rating for m in rated])
        high = max(rated, key=lambda m: m.rating)
        low = min(rated, key=lambda m: m.rating)

        print(colored(f"Average Rating: {avg:.2f}", "yellow"))
        print(colored(f"Highest Rated: {high.title} ({high.rating})", "green"))
        print(colored(f"Lowest Rated: {low.title} ({low.rating})", "red"))

    def recommend(self, recommender: IRecommender):
        recs = recommender.recommend(self.current_user, self.users)
        if not recs:
            print("No recommendations.")
        else:
            print("Recommended:")
            for m in recs:
                print(f"- {m.title} ({m.rating})")

    def guard(self, func):
        if self.current_user:
            func()
        else:
            print("Please login first.")

    def input_nonempty(self, prompt):
        while True:
            val = input(prompt).strip()
            if val:
                return val
            print("Cannot be empty.")


if __name__ == "__main__":
    MovieApp().run()
