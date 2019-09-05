from pathlib import Path


PROJECT_ROOT = Path(__file__).parent


def setup_static_routes(app):
    app.router.add_static('/static/',
                          PROJECT_ROOT / 'static',
                          name='static')
