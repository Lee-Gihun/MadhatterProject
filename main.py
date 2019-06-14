from ChampionRecommender import ChampionRecommender

if __name__ == "__main__":
    user_name = input('Enter rank user name> ')
    champ_recommender = ChampionRecommender()
    print(champ_recommender.recommender(user_name))