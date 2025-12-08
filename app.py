from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from extensions import db, login_manager
from authlib.integrations.flask_client import OAuth
import os 



def create_app(): 
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    # create folders
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok = True)
    os.makedirs(app.config['QRCODE_FOLDER'], exist_ok = True)
    
    from auth import bp as auth_bp
    from routes import bp as main_bp
    
    # add blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()
        # add code here if I want to modify the db
    
    # If I want to initialize db by command
    @app.cli.command('db_init')
    def db_init(): 
        with app.app_context():
            db.create_all()
    
    return app
            
if __name__=='__main__':
    create_app().run(debug=True)

    




