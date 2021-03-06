#! ../env/bin/python
import os

from flask import Flask
from webassets.loaders import PythonLoader as PythonAssetsLoader

from wut4lunch import assets
from wut4lunch.models import db

from wut4lunch.extensions import (
    cache,
    assets_env,
    debug_toolbar,
    login_manager,
)


def create_app(object_name, env="prod"):
    app = Flask(__name__)

    app.config.from_object(object_name)
    app.config['ENV'] = env

    #init the cache
    cache.init_app(app)

    debug_toolbar.init_app(app)

    #init SQLAlchemy
    db.init_app(app)

    login_manager.init_app(app)

    # Import and register the different asset bundles
    assets_env.init_app(app)
    assets_loader = PythonAssetsLoader(assets)
    for name, bundle in assets_loader.load_bundles().iteritems():
        assets_env.register(name, bundle)

    # register our blueprints
    from controllers.main import main
    app.register_blueprint(main)

    return app

if __name__ == '__main__':
    # Import the config for the proper environment using the
    # shell var APPNAME_ENV
    env = os.environ.get('APPNAME_ENV', 'prod')
    app = create_app('wut4lunch.settings.%sConfig' % env.capitalize(), env=env)

    app.run()
