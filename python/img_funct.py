from PIL import Image

from time import perf_counter


def save_img(img, path):
    """Function to save img in delivered path

            img - image obj to save
            path - path where to save image
            """

    pil_img = Image.fromarray(img)
    pil_img.save(path)


# Function to measure time
def performance():
    """Function to measure time
    Function is using yield, so to use it there is need to use next.
    First yield have messaged 'Counting started'
    second one return time needed to perform action """

    while 1:
        start = perf_counter()
        yield 'Counting started'

        stop = perf_counter()
        yield f'The script needed 10 {stop - start:.2f} seconds to perform this action'


# Function to give id of nick
def get_nick_id(nick, User):
    # getting id of user
    user = User.query.filter(User.nick == nick).first()
    return user.id
