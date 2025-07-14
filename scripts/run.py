import sys
import os

# Добавляем корень проекта в пути поиска модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ads_app import create_app

app = create_app()
from ads_app.views import register_error_handlers
register_error_handlers(app)

if __name__ == '__main__':
    app.run(debug=True)