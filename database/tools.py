from telegram import Update
from dbmodels import User, Film, db


def store_user(update: Update):

    uid = update.effective_message.from_user.id

    with db:
        user_entry = User.select().where(User.uid == uid)

        if user_entry.exists():
            return

        username = update.effective_message.from_user.username
        if username is None:
            username = update.effective_message.from_user.first_name

        User.create(uid=uid,
                    username=username)


def store_film(title, file_id, download_url, quality):

    with db:

        Film.get_or_create(title=title)

        film = Film.get(Film.title == title)

        if film.quality.get(quality):
            return

        film.file_id.update({quality: file_id})
        film.download_url.update({quality: download_url})
        film.quality.update({quality: quality})

        query = Film.update(file_id=film.file_id,
                            download_url=film.download_url,
                            quality=film.quality).where(Film.title == title)
        query.execute()


def if_film_in_db(title, quality):

    film = Film.select().where(Film.title == title)

    if film.exists():
        record = film.get()

        return record.file_id.get(quality)
