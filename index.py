#!/usr/bin/python3

import os
import sys

restricted = "restricted"
sys.path.append(os.path.abspath(restricted))

from cgi import FieldStorage
from html import escape
import pymysql as db
import passwords
import funcs

from os import environ
from http.cookies import SimpleCookie

cookie = SimpleCookie()
http_cookie_header = environ.get("HTTP_COOKIE")

result = "href=\"login.py\">Login"

if http_cookie_header:
    cookie.load(http_cookie_header)
    try:
        if funcs.check_if_exists(cookie["sessionId"].value):
            result = "href=\"home/index.py\">Home"

    except:
        pass


print("Content-Type: text/html")
print()      
print("""<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <title>cool welcome page</title>
        <link rel="stylesheet" href="css/index.css" />
        <script src="js/parallax.js" type="module"></script>
    </head>
    <body>
        <header>
            <a href="">Nice Chess Games</a>
            <div
                ><a href="home/leaderboard.py">Leaderboard</a
                ><a href="home/search.py">Search</a
                ><a %s </a
            ></div>
        </header>
        <section class="parallax">
            <a href="register.py" class="register">Register!</a>
            <img src="parallax_svg/layer-1.svg" class="parallax_1" data-speed="10" style="transform: translate3d(0px, 0px, 0px)" />
            <img src="parallax_svg/layer-0.png" class="parallax_0" data-speed="0" style="transform: translate3d(0px, 0px, 0px)" />
        </section>
        <section class="content">
            <section class="content-wrapper">
                <article>
                    <h2>Aha you stumbled upon our product!</h2>
                    <p>
                        Hello this is where I sell you a bunch of corporate lingo about how our product is better than others.
                        Honestly it isn't, and if you don't like it, well sorry. But if you wanna stay be prepared for lots of issues with this website.
                        You may encounter many problems and bugs (features) along the way such as improperly garnished passwords (probably needs more salt), and other things that hasn't came to my mind.
                    </p>
                </article>
                <article>
                    <h2>Cool features!</h2>
                    <ul>
                        <li>Cool, functional front page with parallax!</li>
                        <li>Hopefully a functional chess game with local and online multiplayer!</li>
                        <li>A leaderboard to see people's <a href="https://en.wikipedia.org/wiki/Elo_rating_system">ELO</a></li>
                        <li>A place to inspect people's profiles</li>
                        <li>Profiles and kinda ok security!</li>
                    </ul>
                </article>
                <article>
                    <h2>Please for the love of god don't forget your password</h2>
                    <p>
                        Unfortunately if you lose it I won't be able to get it back! Mostly because I can't send you a confirmation email from this server. 
                    </p>
                </article>
                <a href="register.py" class="register">Register!</a>
            </section> 
        </section>
        <footer>
            <small>
                Lorem ipsum random legal stuff, Nam posuere, nisi at tempor pulvinar, quam diam condimentum dolor, nec egestas arcu risus ac odio. Nulla sollicitudin elit turpis, sed commodo quam venenatis lacinia. Aenean porta ultrices bibendum. Suspendisse consectetur odio nec erat finibus molestie. Vestibulum tincidunt, lacus vitae laoreet pharetra, eros odio dictum mauris, eget aliquam dolor felis non augue. Sed nec lorem sit amet est interdum dictum ut non erat. Nam sodales justo ac elementum porttitor. Vivamus placerat, tortor posuere mattis luctus, orci ex congue lorem, sit amet euismod mauris ipsum nec enim. Duis a metus at mi vehicula eleifend. Aenean aliquam augue quis gravida auctor. Nullam ultricies egestas magna, eget rhoncus orci hendrerit in. Ut interdum eros nec felis ornare egestas. 
            </small>
        </footer>
    </body>
</html>""" % (result))