from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from .models import Advertisement
from .schemas import AdvertisementCreateSchema, AdvertisementUpdateSchema
from ads_app.database.session import db
from .errors import APIError, handle_api_error


ads_bp = Blueprint('ads', __name__, url_prefix='/api/v1/ads')


@ads_bp.route('', methods=['POST'])
def create_ad():
    try:
        data = AdvertisementCreateSchema(**request.get_json()).model_dump()
    except Exception as e:
        raise APIError(str(e), 400)

    try:
        ad = Advertisement(**data)
        db.session.add(ad)
        db.session.commit()
        return jsonify(ad.dict), 201
    except SQLAlchemyError as _:
        db.session.rollback()
        raise APIError("Database error", 500)


@ads_bp.route('/<int:ad_id>', methods=['GET'])
def get_ad(ad_id):
    ad = db.session.get(Advertisement, ad_id)
    if not ad:
        raise APIError("Advertisement not found", 404)
    return jsonify(ad.dict)


@ads_bp.route('/<int:ad_id>', methods=['PUT'])
def update_ad(ad_id):
    ad = db.session.get(Advertisement, ad_id)
    if not ad:
        raise APIError("Advertisement not found", 404)

    try:
        data = AdvertisementUpdateSchema(
            **request.get_json()).model_dump(exclude_unset=True
            )
    except Exception as e:
        raise APIError(str(e), 400)

    try:
        for key, value in data.items():
            setattr(ad, key, value)
        db.session.commit()
        return jsonify(ad.dict)
    except SQLAlchemyError as _:
        db.session.rollback()
        raise APIError("Database error", 500)


@ads_bp.route('/<int:ad_id>', methods=['DELETE'])
def delete_ad(ad_id):
    ad = db.session.get(Advertisement, ad_id)
    if not ad:
        raise APIError("Advertisement not found", 404)

    try:
        db.session.delete(ad)
        db.session.commit()
        return jsonify({'message': 'Advertisement deleted successfully'}), 200
    except SQLAlchemyError as _:
        db.session.rollback()
        raise APIError("Database error", 500)


def register_error_handlers(app):
    app.register_error_handler(APIError, handle_api_error)
