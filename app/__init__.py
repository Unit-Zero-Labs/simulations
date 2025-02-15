from flask import Flask
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__, 
                static_folder='static', 
                template_folder='templates')
    app.config.from_object(config_class)

    # import & register blueprints
    from app.routes.main import main_bp
    from app.routes.lending import lending_bp
    from app.routes.stable_pool import stable_pool_bp
    from app.routes.non_stable_pool import non_stable_pool_bp
    from app.routes.tokenomics import tokenomics_bp    
    from app.routes.fund_raising import fund_raising_bp 
    from app.routes.lp_sim import lp_sim_bp 


    app.register_blueprint(main_bp)
    app.register_blueprint(lending_bp)
    app.register_blueprint(stable_pool_bp)
    app.register_blueprint(non_stable_pool_bp)
    app.register_blueprint(tokenomics_bp)
    app.register_blueprint(fund_raising_bp)
    app.register_blueprint(lp_sim_bp)

    return app