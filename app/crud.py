import base64
from sqlalchemy.orm import Session
from app.models import UserModel, FileContent
from werkzeug.security import generate_password_hash, check_password_hash


def get_user_by_id(db: Session, user_id: int):
    return db.query(UserModel).filter(UserModel.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(UserModel).filter(UserModel.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(UserModel).offset(skip).limit(limit).all()


def create_user_in_db(db: Session, username, password):
    hashed_password = generate_password_hash(password)
    db_user = UserModel(username=username, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_image_by_id(db, image_id):
    return db.query(FileContent).filter(FileContent.id == image_id).first()


def get_images_from_db(db: Session, skip: int = 0, limit: int = 10):
    images = db.query(FileContent).order_by(-FileContent.id).offset(skip).limit(limit).all()
    return images


def save_image_in_db(db, title, data, filename, url=""):
    #db_item = FileContent(**item.dict(), owner_id=user_id)
    render_file = render_picture(data)
    db_item = FileContent(title=title, data=data, filename=filename, rendered_data=render_file, url=url)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_db_image_count(db):
    num_images = db.query(FileContent).count()
    return num_images


def get_db_stats(db):
    num_images = get_db_image_count(db)
    last_image = db.query(FileContent).order_by(-FileContent.id).first()
    total_images = last_image.id
    return total_images, num_images


def check_user_pass(db, username, password):
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if user is None:
        return False
    if check_password_hash(user.password_hash, password):
        return True
    else:
        return False


### HELPER ###
# needed to save the image in base64 in DB: this should be don in an object storage like S3
def render_picture(data):
    render_pic = base64.b64encode(data).decode('ascii')
    return render_pic

