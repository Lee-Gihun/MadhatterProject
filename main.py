from champion_recommender import ChampionRecommender

if __name__ == "__main__":
    user_name = input('Enter user name> ')
    champ_recommender = ChampionRecommender()
    recommended = champ_recommender.recommender(user_name)

    i = 1
    for champ_name, score in recommended[0].items():
        print('[{}] {} - {}'.format(i, champ_name, round(score, 8)))
        i += 1