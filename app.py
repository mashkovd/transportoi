from flask import Flask, request, redirect
from flasgger import Swagger
from flask_marshmallow import Marshmallow
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Resource

import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:postgres@postgres:5432/transportoi"
db = SQLAlchemy(app)
ma = Marshmallow(app)
swagger = Swagger(app)
api = Api(app)
migrate = Migrate(app, db)


# models
class Link(db.Model):
    short_link = db.Column(db.String(), primary_key=True)
    long_link = db.Column(db.String())
    statistics = db.relationship('Statistics', backref='statistics', lazy=True)


class Statistics(db.Model):
    short_link = db.Column(db.String(), db.ForeignKey('link.short_link'), nullable=False, primary_key=True)
    count = db.Column(db.Integer())


# schemas
class LinkSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Link

    long_link = ma.auto_field()
    short_link = ma.auto_field()


class StatisticsSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Statistics

    # short_link = ma.auto_field()
    count = ma.auto_field()


# Resource
class LongToShort(Resource):
    def post(self):
        """
        Создание короткой ссылки из длинной
        ---
        tags:
          - Сервис для ссылок
        parameters:
          - name: long_link
            in: body
            required: true
            schema:
              id: Link
              properties:
                long_link:
                  type: string
                  description: Длинная ссылка
                  default: https://yandex.ru/news/?clid=1955454&win=368

        responses:
          200:
            description: Короткая ссылка успешна создана
        """
        long_link = request.json.get('long_link')
        short_link = f'{request.host_url}{hashlib.sha1(long_link.encode("UTF-8")).hexdigest()[:10]}'
        link = Link.query.filter_by(short_link=short_link).one_or_none()
        if link is None:
            link = Link(long_link=long_link, short_link=short_link)
            db.session.add(link)
            db.session.commit()

        link_schema = LinkSchema()
        return link_schema.dump(link)


class ShortLink(Resource):
    def get(self, short_postfix):
        """
        ---
        tags:
          - Перейти на длинную ссылку по соответствующей данной короткой
        parameters:
          - in: path
            name: short_postfix
            type: string
            required: true
        responses:
          302:
            description: Редирект на длинную ссылку
         """
        link = Link.query.filter_by(short_link=f'{request.host_url}{short_postfix}').one_or_none()
        if link:
            statistics = Statistics.query.filter_by(short_link=f'{request.host_url}{short_postfix}').one_or_none()
            if statistics:
                statistics.count += 1
            else:
                statistics = Statistics(short_link=f'{request.host_url}{short_postfix}', count=1)
                db.session.add(statistics)
            db.session.commit()

            return redirect(link.long_link)
        else:
            return {'message': 'short_link not founded'}


class LinkStatistics(Resource):
    def get(self, short_postfix):
        """
        Получить количество переходов по короткой ссылке
        ---
        tags:
          - Сервис для ссылок
        parameters:
          - in: path
            name: short_postfix
            type: string
            required: true
        responses:
          200:
            description: Кол-во переходов по короткой ссылке
            schema:
              id: StatisticsSchema
              properties:
                count:
                  type: integer
                  description: Кол-во переходов
                  default: 0
         """

        statistics = Statistics.query.filter_by(short_link=f'{request.host_url}{short_postfix}').one_or_none()
        if statistics is None:
            return {'count': 0}
        statistics_schema = StatisticsSchema()
        return statistics_schema.dump(statistics)


class LinkResource(Resource):
    def get(self):
        """
        Получить информацию по всем ссылкам
        ---
        tags:
          - Ссылки
        responses:
          200:
            description: Список ссылок
            schema:
              id: LinkSchema
              properties:
                long_link:
                  type: string
                  description: Длинная ссылка
                short_link:
                  type: string
                  description: Короткая ссылка
        """
        all_links = Link.query.all()
        link_schema = LinkSchema(many=True)
        return link_schema.dump(all_links)


api.add_resource(LinkResource, '/link')
api.add_resource(LongToShort, '/long_to_short')
api.add_resource(ShortLink, '/<string:short_postfix>')
api.add_resource(LinkStatistics, '/statistics/<string:short_postfix>')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
