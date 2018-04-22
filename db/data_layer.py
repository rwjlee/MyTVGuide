from db.base import DbManager
from db.entities import User, Show, Like
import requests, json

db = DbManager()

API_BASE = 'http://api.tvmaze.com/search/shows?q='

def get_json(url):
    resp = requests.get(url)
    return json.loads(resp.text)

def create_user(email, name, password):
    user = User()
    user.name = name
    user.email = email
    user.password = password
    return db.save(user)

def get_show_by_api_id(api_id):
    try:
        show = db.open().query(Show).filter(Show.api_id == api_id).one()
        return show
    except:
        return None

def create_show(title, image_url, api_id):
    show = get_show_by_api_id(api_id)
    if show:
        return show

    show = Show()
    show.title = title
    show.image_url = image_url
    show.api_id = api_id
    return db.save(show)

def search_by_title(query):
    query_list = query.split()
    if len(query_list)==0:
        return None

    q=""
    for word in query_list:
        q = q + '+{}'.format(word)

    print("======={}======".format(q))
    query_url = API_BASE + q
    json_data = get_json(query_url)
    
    if len(json_data)==0:
        return None

    show_list = []

    for show_data in json_data:
        show_dict = show_data['show']
        api_id = str(show_dict['id'])
        print("-----{}------".format(api_id))
        title = show_dict['name']
        if show_dict['image']:
            image_url = show_dict['image']['medium']
        else:
            image_url = ''

        new_show = create_show(title, image_url, api_id)
        show_list.append(new_show)
        
    return show_list

def create_like(user_id, show_id):
    try:
        like = get_like(user_id, show_id)
    except:
        like = Like()
        like.user = get_user_by_id(user_id)
        like.show = get_show_by_id(show_id)
        like.uid_to_sid = str(user_id) + '_' + str(show_id)
        db.save(like)

    return like

def get_like(user_id, show_id):
    uid_to_sid = str(user_id) + '_' + str(show_id)
    return db.open().query(Like).filter(Like.uid_to_sid == uid_to_sid).one()

def delete_like(user_id, show_id):
    uid_to_sid = str(user_id) + '_' + str(show_id)
    like = get_like(user_id, show_id)
    return db.delete(like)

def get_show_by_id(show_id):
    return db.open().query(Show).filter(Show.id == show_id).one()

def get_shows_by_user(user_id):
    user = get_user_by_id(user_id)
    shows = user.likes_shows
    return shows

def get_followers_by_show(show_id):
    followers = []
    try:
        likes = db.open().query(Like).filter(Like.show_id == show_id).all()
        followers = [get_user_by_id(like.user_id) for like in likes]
    except:
        pass

    return followers

def get_user_by_id(user_id):
    return db.open().query(User).filter(User.id == user_id).one()

def get_user_by_email(email):
    return db.open().query(User).filter(User.email == email).one()


