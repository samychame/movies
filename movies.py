class Movie:
    def __init__(self, title):
        self.title = title
        self.rating = None

    def set_rating(self, rating):
        if 1 <= rating <= 10:
            self.rating = rating
        else:
            raise ValueError("Rating must be between 1 and 10.")

    def __str__(self):
        return f"{self.title}: {self.rating if self.rating is not None else 'No rating'}"


class MovieManager:
    def __init__(self):
        self.movies = {}  # Dictionary: title -> Movie object

    def collect_movies(self):
        print("Enter movie names (type 'סיום' to finish):")
        while True:
            title = input("Movie name: ").strip()
            if title.lower() == "סיום":
                if not self.movies:
                    print("You must enter at least one movie.")
                    continue
                break
            if not title:
                print("Movie title cannot be empty.")
                continue
            if title in self.movies:
                print("This movie already exists. Please enter a different title.")
                continue
            self.movies[title] = Movie(title)
            print(self.movies)

    def add_ratings(self):
        for title, movie in self.movies.items():
            while True:
                try:
                    rating_input = input(f"Enter a rating for '{title}' (1-10): ").strip()
                    rating = int(rating_input)
                    movie.set_rating(rating)
                    break
                except ValueError:
                    print("Invalid input. Please enter a number between 1 and 10.")

    def display_movies(self):
        print("\nMovie Ratings:")
        for movie in self.movies.values():
            print(movie)


class MovieStats:
    def __init__(self, movies_dict):
        self.movies = movies_dict  # {title: Movie}

    def average_rating(self):
        rated_movies = [movie.rating for movie in self.movies.values() if movie.rating is not None]
        if not rated_movies:
            return None
        return sum(rated_movies) / len(rated_movies)

    def highest_rated(self):
        rated = [movie for movie in self.movies.values() if movie.rating is not None]
        if not rated:
            return None
        return max(rated, key=lambda m: m.rating)

    def lowest_rated(self):
        rated = [movie for movie in self.movies.values() if movie.rating is not None]
        if not rated:
            return None
        return min(rated, key=lambda m: m.rating)

    def display_stats(self):
        print("\n--- Movie Statistics ---")
        avg = self.average_rating()
        print(f"Average rating: {avg:.2f}" if avg is not None else "No ratings available.")

        top = self.highest_rated()
        if top:
            print(f"Highest rated: {top.title} ({top.rating})")

        low = self.lowest_rated()
        if low:
            print(f"Lowest rated: {low.title} ({low.rating})")


def main():
    manager = MovieManager()
    manager.collect_movies()
    manager.add_ratings()
    manager.display_movies()

    stats = MovieStats(manager.movies)
    stats.display_stats()


if __name__ == "__main__":
    main()
