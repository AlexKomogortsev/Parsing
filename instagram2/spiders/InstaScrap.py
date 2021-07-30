import scrapy
import re
from scrapy.http import HtmlResponse
from dotenv import load_dotenv
import os
import json
from instagram.items import InstagramItem


class InstascrapSpider(scrapy.Spider):
    name = 'InstaScrap'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    load_dotenv('.env')
    USERNAME = os.getenv('name', None)
    PASSWORD = os.getenv('pass', None)
    user_list = ['mrdementiev', 'elena_reverdatto']
    query_hash1 = '8c2a529969ee035a5063f2fc8602a0fd'

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.login_url,
            method='POST',
            callback=self.login,
            formdata={'username': self.USERNAME,
                      'enc_password': self.PASSWORD},
            headers={'x-csrftoken': csrf}
        )

    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data['authenticated']:
            for user in self.user_list:
                yield response.follow(
                    f'/{user}',
                    callback=self.parse_user,
                    cb_kwargs={
                        'username': user
                    }
                )

    def parse_user(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)

        url_followers = f'https://i.instagram.com/api/v1/friendships/{user_id}/followers/?count=12&search_surface=follow_list_page'
        yield scrapy.Request(url_followers,
                             callback=self.parse_followers,
                             cb_kwargs={
                                 'user_id': user_id,
                                 'username': username
                             },
                             headers={
                                 'User-Agent': 'Instagram 155.0.0.37.107'
                             }
                             )

    def parse_followers(self, response: HtmlResponse, user_id, username):
        j_data = response.json()

        if j_data['big_list'] is True:
            next_max_id = j_data['next_max_id']

            for follower in j_data['users']:
                item = self.parse_followers_data(follower, username)
                yield item

            url_followers = f'https://i.instagram.com/api/v1/friendships/{user_id}/followers/?count=12&max_id={next_max_id}&search_surface=follow_list_page'

            yield scrapy.Request(url_followers,
                                 callback=self.parse_followers,
                                 cb_kwargs={
                                     'user_id': user_id,
                                     'username': username
                                 },
                                 headers={
                                     'User-Agent': 'Instagram 155.0.0.37.107'
                                 }
                                 )

        else:
            for follower in j_data['users']:
                item = self.parse_followers_data(follower, username)
                yield item

            url_followings = f'https://i.instagram.com/api/v1/friendships/{user_id}/following/?count=12'

            yield scrapy.Request(url_followings,
                                 callback=self.parse_followings,
                                 cb_kwargs={
                                     'user_id': user_id,
                                     'username': username
                                 },
                                 headers={
                                     'User-Agent': 'Instagram 155.0.0.37.107'
                                 })

    def parse_followings(self, response: HtmlResponse, user_id, username):
        j_data = response.json()

        if j_data['big_list'] is True:
            next_max_id = j_data['next_max_id']

            for following in j_data['users']:
                item = self.parse_followings_data(following, username)
                yield item

            url_followings = f'https://i.instagram.com/api/v1/friendships/{user_id}/following/?count=12&max_id={next_max_id}'

            yield scrapy.Request(url_followings,
                                 callback=self.parse_followings,
                                 cb_kwargs={
                                     'user_id': user_id,
                                     'username': username
                                 },
                                 headers={
                                     'User-Agent': 'Instagram 155.0.0.37.107'
                                 }
                                 )
        else:
            for following in j_data['users']:
                item = self.parse_followings_data(following, username)
                yield item

    def parse_followers_data(self, follower, username):
        follower_name = follower['username']
        follower_id = follower['pk']
        follower_photo_link = follower['profile_pic_url']

        item = InstagramItem(follower_name=follower_name, follower_id=follower_id,
                             follower_photo_link=follower_photo_link, username=username)

        return item

    def parse_followings_data(self, following, username):
        following_name = following['username']
        following_id = following['pk']
        following_photo_link = following['profile_pic_url']

        item = InstagramItem(following_name=following_name, following_id=following_id,
                             following_photo_link=following_photo_link,
                             username=username)

        return item

    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
