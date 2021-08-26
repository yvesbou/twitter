import twitter

import unittest
import responses
from responses import GET

import json
import re

URL = re.compile(r"https://api.twitter.com/2*")


class TwitterAPITest(unittest.TestCase):

    @responses.activate
    def setUp(self):
        """
        instantiate api and twitter user, since many functions need a user instance
        :return:
        """
        self.api = twitter.TwitterAPI('xxx')
        self.responses = responses.RequestsMock()
        self.responses.start()

        with open('../testdata/user_without_expansion.json', 'r') as f:
            data = f.read()
            f.close()

        self.responses.add(GET, url=URL, body=data)

        self.user = self.api.getUser(userName="AliAbdaal", withExpansion=False)

        self.addCleanup(self.responses.stop)
        self.addCleanup(self.responses.reset)

    def tearDown(self):
        self.addCleanup(self.responses.stop)
        self.addCleanup(self.responses.reset)

    def testSetUpAPI(self):
        self.assertEqual('xxx', self.api._TwitterAPI__bearer_token)

    @responses.activate
    def testGetUser_withoutExpansion_wUserId(self):
        self.responses = responses.RequestsMock()
        self.responses.start()
        with open('../testdata/user_without_expansion.json', 'r') as f:
            data = f.read()
            f.close()
        self.responses.add(GET, url=URL, body=data)
        user = self.api.getUser(userId=30436279, withExpansion=False)
        self.assertEqual(user.name, "Ali Abdaal")
        self.assertEqual(user.tweets, {})
        self.assertIsInstance(user, twitter.TwitterUser)

    @responses.activate
    def testGetUser_withoutExpansion(self):
        self.assertEqual(self.user.name, "Ali Abdaal")
        self.assertEqual(self.user.tweets, {})
        self.assertIsInstance(self.user, twitter.TwitterUser)

    @responses.activate
    def testGetUsers_withExpansion_wMultipleUserNames(self):
        self.responses = responses.RequestsMock()
        self.responses.start()
        with open('../testdata/multiple_users_with_expansion.json', 'r') as f:
            data = f.read()
            f.close()
        self.responses.add(GET, url=URL, body=data)
        users = self.api.getUsers(userNames=['AliAbdaal', 'boutellier_yves', 'michael_saylor'])
        self.assertEqual(users[1].username, 'boutellier_yves')
        # todo: write assert for pinnedTweet

    @responses.activate
    def testGetUsers_withExpansion_wMultipleIds(self):
        self.responses = responses.RequestsMock()
        self.responses.start()
        with open('../testdata/multiple_users_with_expansion.json', 'r') as f:
            data = f.read()
            f.close()
        self.responses.add(GET, url=URL, body=data)
        users = self.api.getUsers(userIds=[30436279, 1380593146971762690, 244647486])
        self.assertEqual(users[0].username, 'AliAbdaal')

    @responses.activate
    def testGetUser_noArgument(self):
        self.responses = responses.RequestsMock()
        self.responses.start()
        with open('../testdata/multiple_users_with_expansion.json', 'r') as f:
            data = f.read()
            f.close()
        self.responses.add(GET, url=URL, body=data)
        self.assertRaises(twitter.APIError, self.api.getUser)

    @responses.activate
    def testGetUser_withExpansion(self):
        self.responses = responses.RequestsMock()
        self.responses.start()
        with open('../testdata/user_with_expansion.json', 'r') as f:
            data = f.read()
            f.close()
        self.responses.add(GET, url=URL, body=data)
        resp = self.api.getUser(userName="AliAbdaal", withExpansion=True)
        tweet = next(iter(resp.tweets.values()))  # just one entry
        self.assertIsInstance(tweet, twitter.Tweet)

    @responses.activate
    def testGetUser_withExpansion_missingTweet(self):
        self.responses = responses.RequestsMock()
        self.responses.start()
        with open('../testdata/user_with_expansion_missingTweet.json', 'r') as f:
            data = f.read()
            f.close()
        self.responses.add(GET, url=URL, body=data)
        resp = self.api.getUser(userName="boutellier_yves", withExpansion=True)
        self.assertEqual('boutellier_yves', resp.username)

    @responses.activate
    def testGetFollowers_1page_withoutExpansion(self):
        self.responses = responses.RequestsMock()
        self.responses.start()
        with open('../testdata/followers_1page_w1000_without_expansion.json', 'r') as f:
            data = f.read()
            f.close()
        self.responses.add(GET, url=URL, body=data)
        resp = self.api.getFollowers(user=self.user, numPages=1, withExpansion=False)
        follower = next(iter(resp.values()))
        self.assertEqual(len(resp), 1000)
        self.assertIsInstance(resp, dict)
        self.assertIsInstance(follower, twitter.TwitterUser)

    @responses.activate
    def testGetFollowers_2pages_withoutExpansion(self):
        self.responses = responses.RequestsMock()
        self.responses.start()
        with open('../testdata/followers_2pages1_2_w1000_without_expansion.json', 'r') as f:
            data_1st_page = f.read()
            f.close()
        with open('../testdata/followers_2pages2_2_w1000_without_expansion.json', 'r') as f:
            data_2nd_page = f.read()
            f.close()
        self.responses.add(GET, url=URL, body=data_1st_page)
        self.responses.add(GET, url=URL, body=data_2nd_page)
        resp = self.api.getFollowers(user=self.user, numPages=2, withExpansion=False)
        follower = next(iter(resp.values()))
        self.assertEqual(len(resp), 2000)
        self.assertEqual(follower.tweets, {})
        self.assertIsInstance(resp, dict)
        self.assertIsInstance(follower, twitter.TwitterUser)

    @responses.activate
    def testGetFollowers_1page_withExpansion(self):
        self.responses = responses.RequestsMock()
        self.responses.start()
        with open("../testdata/followers_1page_w1000_with_expansion.json", "r") as f:
            data = f.read()
            f.close()
        self.responses.add(GET, url=URL, body=data)
        resp = self.api.getFollowers(user=self.user, numPages=1, withExpansion=True)
        follower = resp["2919776594"]  # need example that has actually a pinned Tweet
        pinnedTweet = next(iter(follower.tweets.values()))
        self.assertEqual(1000, len(resp))
        self.assertIsInstance(resp, dict)
        self.assertIsInstance(pinnedTweet, twitter.Tweet)
        self.assertEqual(follower.id, pinnedTweet.author_id)

    @responses.activate
    def testsGetFollowers_2page_withExpansion(self):
        self.responses = responses.RequestsMock()
        self.responses.start()
        with open('../testdata/followers_2pages1_2_w1000_with_expansion.json', 'r') as f:
            data_1st_page = f.read()
            f.close()
        with open('../testdata/followers_2pages2_2_w1000_with_expansion.json', 'r') as f:
            data_2nd_page = f.read()
            f.close()
        self.responses.add(GET, url=URL, body=data_1st_page)
        self.responses.add(GET, url=URL, body=data_2nd_page)
        resp = self.api.getFollowers(user=self.user, numPages=2, withExpansion=True)
        follower = resp["2919776594"]  # need example that has actually a pinned Tweet
        pinnedTweet = next(iter(follower.tweets.values()))
        self.assertEqual(2000, len(resp))
        self.assertIsInstance(resp, dict)
        self.assertIsInstance(pinnedTweet, twitter.Tweet)
        self.assertEqual(follower.id, pinnedTweet.author_id)

    @responses.activate
    def testGetFriends_1page_withoutExpansion(self):
        self.responses = responses.RequestsMock()
        self.responses.start()
        with open('../testdata/friends_2pages1_2_w1000_without_expansion.json', 'r') as f:
            data = f.read()
            f.close()
        self.responses.add(GET, url=URL, body=data)
        resp = self.api.getFriends(user=self.user, numPages=1, withExpansion=False)
        friend = next(iter(resp.values()))
        self.assertEqual(len(resp), 1000)
        self.assertIsInstance(resp, dict)
        self.assertIsInstance(friend, twitter.TwitterUser)

    @responses.activate
    def testGetFriends_2pages_withoutExpansion(self):
        self.responses = responses.RequestsMock()
        self.responses.start()
        with open('../testdata/friends_2pages1_2_w1000_without_expansion.json', 'r') as f:
            data_1st_page = f.read()
            f.close()
        with open('../testdata/friends_2pages2_2_w1000_without_expansion.json', 'r') as f:
            data_2nd_page = f.read()
            f.close()
        self.responses.add(GET, url=URL, body=data_1st_page)
        self.responses.add(GET, url=URL, body=data_2nd_page)
        resp = self.api.getFriends(user=self.user, numPages=2, withExpansion=False)
        friend = next(iter(resp.values()))
        self.assertAlmostEqual(len(resp), self.user.getFriendsCount(), delta=5)
        self.assertEqual(friend.tweets, {})
        self.assertIsInstance(resp, dict)
        self.assertIsInstance(friend, twitter.TwitterUser)

    @responses.activate
    def testGetFriends_1page_withExpansion(self):
        self.responses = responses.RequestsMock()
        self.responses.start()
        with open("../testdata/friends_2pages1_2_w1000_with_expansion.json", "r") as f:
            data = f.read()
            f.close()
        self.responses.add(GET, url=URL, body=data)
        resp = self.api.getFriends(user=self.user, numPages=1, withExpansion=True)
        friend = resp["14372143"]  # need example that has actually a pinned Tweet
        pinnedTweet = next(iter(friend.tweets.values()))
        self.assertEqual(1000, len(resp))
        self.assertIsInstance(resp, dict)
        self.assertIsInstance(pinnedTweet, twitter.Tweet)
        self.assertEqual(friend.id, pinnedTweet.author_id)

    @responses.activate
    def testsGetFriends_2page_withExpansion(self):
        self.responses = responses.RequestsMock()
        self.responses.start()
        with open('../testdata/friends_2pages1_2_w1000_with_expansion.json', 'r') as f:
            data_1st_page = f.read()
            f.close()
        with open('../testdata/friends_2pages2_2_w1000_with_expansion.json', 'r') as f:
            data_2nd_page = f.read()
            f.close()
        self.responses.add(GET, url=URL, body=data_1st_page)
        self.responses.add(GET, url=URL, body=data_2nd_page)
        resp = self.api.getFriends(user=self.user, numPages=2, withExpansion=True)
        friend = resp["14372143"]  # need example that has actually a pinned Tweet
        pinnedTweet = next(iter(friend.tweets.values()))
        self.assertAlmostEqual(len(resp), self.user.getFriendsCount(), delta=5)
        self.assertIsInstance(resp, dict)
        self.assertIsInstance(pinnedTweet, twitter.Tweet)
        self.assertEqual(friend.id, pinnedTweet.author_id)

    @responses.activate
    def testGetTweet(self):
        self.responses = responses.RequestsMock()
        self.responses.start()
        with open('../testdata/tweet_withoutExpansion.json', 'r') as f:
            data = f.read()
            f.close()
        self.responses.add(GET, url=URL, body=data)
        tweet = self.api.getTweet(tweetId=1424757354290159621, withExpansion=False)
        self.assertIsInstance(tweet, twitter.Tweet)
        self.assertEqual("1424757354290159621", tweet.id)
        self.assertEqual("1424757354290159621", tweet.conversation_id)
        self.assertEqual("Get startup news for founders, not consumers 👉 https://t.co/bSR19MNh6s\n\nAlso, tweet @IndieHackers or use hashtag #indiehackers and we'll retweet genuine questions and requests.\n\nWe've got over 70,000 followers who can potentially help you! 🗺 🧠 👇 https://t.co/ANfyyZY2Jx", tweet.text)
        self.assertEqual("756326958946922496", tweet.author_id)
        self.assertEqual("en", tweet.lang)
        self.assertEqual("2021-08-09T15:39:58.000Z", tweet.created_at)
        self.assertEqual("Twitter Web App", tweet.source)
        self.assertEqual("everyone", tweet.reply_settings)
        self.assertEqual(False, tweet.possibly_sensitive)
        self.assertEqual(0, tweet.reply_count)
        self.assertEqual(0, tweet.retweet_count)
        self.assertEqual(16, tweet.like_count)
        self.assertEqual(0, tweet.quote_count)
        self.assertEqual(False, tweet.pinned)
        self.assertEqual(None, tweet.in_reply_to_user_id)
        self.assertEqual(None, tweet.referenced_tweets)
        self.assertEqual([], tweet.realWorldEntities)
        self.assertEqual([{"start": 47, "end": 70, "url": "https://t.co/bSR19MNh6s", "expanded_url": "https://www.indiehackers.com/newsletter", "display_url": "indiehackers.com/newsletter", "status": 200, "unwound_url": "https://www.indiehackers.com/newsletter"}, {"start": 246, "end": 269, "url": "https://t.co/ANfyyZY2Jx", "expanded_url": "https://twitter.com/IndieHackers/status/1424757354290159621/photo/1", "display_url": "pic.twitter.com/ANfyyZY2Jx"}], tweet.urls)
        self.assertEqual([], tweet.geo)  # place_id is associated with a place
        self.assertEqual([], tweet.poll)
        self.assertEqual([{"start": 113, "end": 126, "tag": "indiehackers"}], tweet.hashtags)
        self.assertEqual('756326958946922496', tweet.mentions[0].id)
        self.assertEqual('IndieHackers', tweet.mentions[0].username)
        self.assertEqual(84, tweet.mentions[0].start)
        self.assertEqual(97, tweet.mentions[0].end)

    @responses.activate
    def testGetTweet_withExpansions_poll(self):
        self.responses = responses.RequestsMock()
        self.responses.start()
        with open('../testdata/tweet_wExpansions_poll_user.json', 'r') as f:
            data = f.read()
            f.close()
        self.responses.add(GET, url=URL, body=data)
        tweet = self.api.getTweet(tweetId=1199786642468413448, withExpansion=True)
        poll = tweet.polls[0]
        self.assertEqual(tweet, poll.tweet)
        self.assertEqual("2019-11-28T20:26:41.000Z", poll.end_datetime)
        self.assertEqual("1199786642468413448", poll.id)
        self.assertEqual("closed", poll.voting_status)
        self.assertEqual(1440, poll.duration_minutes)
        self.assertEqual([{'position': 1, 'label': '“C Sharp”', 'votes': 795}, {'position': 2, 'label': '“C Hashtag”', 'votes': 156}],
                            poll.options)

    @responses.activate
    def testGetTweet_withExpansions_media(self):
        self.responses = responses.RequestsMock()
        self.responses.start()
        with open('../testdata/tweet_wExpansions_media_user.json', 'r') as f:
            data = f.read()
            f.close()
        self.responses.add(GET, url=URL, body=data)
        tweet = self.api.getTweet(tweetId=1424757354290159621, withExpansion=True)
        media = tweet.media[0]
        self.assertEqual(tweet, media.tweet)
        self.assertEqual("photo", media.type)
        self.assertEqual("3_1424756947169988610", media.media_key)
        self.assertEqual(421, media.height)
        self.assertEqual(749, media.width)
        self.assertEqual("https://pbs.twimg.com/media/E8XA5Q9WUAIXRSe.jpg", media.url)

    @responses.activate
    def testGetTweets_withoutExpansions(self):
        self.responses = responses.RequestsMock()
        self.responses.start()
        with open('../testdata/tweets_withoutExpansions.json', 'r') as f:
            data = f.read()
            f.close()
        self.responses.add(GET, url=URL, body=data)
        tweetIds = [1216144745619165184, 1267631648910139392, 1425855818512011264, 1383112661311778817,
                    1325907009556852751]
        tweetsList = self.api.getTweets(tweetIds=tweetIds, withExpansion=False)
        self.assertEqual("1216144745619165184", tweetsList[0].id)
        self.assertEqual("1267631648910139392", tweetsList[1].id)
        self.assertEqual("1425855818512011264", tweetsList[2].id)
        self.assertEqual("1383112661311778817", tweetsList[3].id)
        self.assertEqual("1325907009556852751", tweetsList[4].id)
        self.assertEqual("22151118", tweetsList[0].author_id)
        self.assertEqual("410409666", tweetsList[1].author_id)
        self.assertEqual("4625037762", tweetsList[2].author_id)
        self.assertEqual("490932793", tweetsList[3].author_id)
        self.assertEqual("335494047", tweetsList[4].author_id)
        self.assertEqual(324, tweetsList[0].like_count)
        self.assertEqual(530696, tweetsList[1].like_count)
        self.assertEqual(132, tweetsList[2].like_count)
        self.assertEqual(53407, tweetsList[3].like_count)
        self.assertEqual(570, tweetsList[4].like_count)

    @responses.activate
    def testGetTweets_withExpansions(self):
        self.responses = responses.RequestsMock()
        self.responses.start()
        with open('../testdata/tweets_withExpansions.json', 'r') as f:
            data = f.read()
            f.close()
        self.responses.add(GET, url=URL, body=data)
        tweetIds = [1216144745619165184, 1267631648910139392, 1425855818512011264, 1383112661311778817,
                    1325907009556852751]
        tweetsList = self.api.getTweets(tweetIds=tweetIds, withExpansion=True)
        self.assertEqual("1216144745619165184", tweetsList[0].id)
        self.assertEqual("1267631648910139392", tweetsList[1].id)
        self.assertEqual("1425855818512011264", tweetsList[2].id)
        self.assertEqual("1383112661311778817", tweetsList[3].id)
        self.assertEqual("1325907009556852751", tweetsList[4].id)
        self.assertEqual("m_ashcroft", tweetsList[0].users[0].username)
        self.assertEqual("LoganPaul", tweetsList[1].users[0].username)
        self.assertEqual("susanthesquark", tweetsList[2].users[0].username)
        self.assertEqual("MarkRober", tweetsList[3].users[0].username)
        self.assertEqual("Jopo_dr", tweetsList[4].users[0].username)
        self.assertEqual(0, len(tweetsList[0].media))
        self.assertEqual(1, len(tweetsList[1].media))
        self.assertEqual(1, len(tweetsList[2].media))
        self.assertEqual(1, len(tweetsList[3].media))
        self.assertEqual(0, len(tweetsList[4].media))
        self.assertEqual(0, len(tweetsList[0].poll))  
        self.assertEqual(0, len(tweetsList[1].poll))
        self.assertEqual(0, len(tweetsList[2].poll))
        self.assertEqual(0, len(tweetsList[3].poll))
        self.assertEqual(0, len(tweetsList[4].poll))

    @responses.activate
    def testRetweet_withoutExpansion(self):
        self.responses = responses.RequestsMock()
        self.responses.start()
        with open('../testdata/retweeters_withoutExpansion.json', 'r') as f:
            data = f.read()
            f.close()
        self.responses.add(GET, url=URL, body=data)
        ids = 1430423837229920258
        reTweeters = self.api.getReTweeter(tweetId=ids, withExpansion=False)
        self.assertEqual(10, len(reTweeters))
        self.assertEqual("Vincent02770108", reTweeters[9].username)
        self.assertEqual('1382425222494756868', reTweeters[9].id)
        self.assertEqual({}, reTweeters[9].tweets)

    @responses.activate
    def testRetweet_withExpansion(self):
        self.responses = responses.RequestsMock()
        self.responses.start()
        with open('../testdata/retweeters_withExpansion.json', 'r') as f:
            data = f.read()
            f.close()
        self.responses.add(GET, url=URL, body=data)
        ids = 1430423837229920258
        reTweeters = self.api.getReTweeter(tweetId=ids, withExpansion=False)
        self.assertEqual(10, len(reTweeters))
        self.assertEqual("HubOfML", reTweeters[0].name)
        self.assertEqual('3040871649', reTweeters[0].id)
        pinned_tweet_id = reTweeters[0].pinned_tweet_id
        self.assertIsInstance(reTweeters[0].tweets[pinned_tweet_id], twitter.Tweet)
        self.assertEqual(reTweeters[0].id, reTweeters[0].tweets[pinned_tweet_id].author_id)




if __name__ == '__main__':
    unittest.main()
