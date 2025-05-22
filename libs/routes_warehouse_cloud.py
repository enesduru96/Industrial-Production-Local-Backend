from flask import request
from flask import Blueprint
from flask_jwt_extended import jwt_required

from libs.Local_Requests import WR__MaterialTypes, WR__MaterialCategories, WR__MaterialProviders, WR__Customers
from libs.Local_Requests import WR__Products, WR__Materials_new, WR___Main, WR__Shipments, WR__LazerStockTasks


warehouse_routes = Blueprint("warehouse_routes", __name__)

def check_user_access(headers):
    access_granted = False   
    if headers["User-Agent"] != "user-companyname" or headers["Connection"] != "keep-alive":
        access_granted = False
    else:
        access_granted = True

    return access_granted


@warehouse_routes.route('/get-warehouse-config', methods=['POST'])
@jwt_required()
def handle_get_config():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    localResult = WR___Main.get_warehouse_config()
    return localResult

@warehouse_routes.route('/yeni-hammadde', methods=['POST'])
@jwt_required()
def handle_stock_add_request():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    data_received = data['data_sent']
    localResult = WR__Materials_new.define_stock_material(data_received)

    print(localResult)
    return localResult

@warehouse_routes.route('/hammadde-duzenle', methods=['POST'])
@jwt_required()
def handle_material_edit_request():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    data_received = data['data_sent']
    localResult = WR__Materials_new.edit_stock_material(data_received)
    print(localResult)
    return localResult

@warehouse_routes.route('/get-materials', methods=["POST", "GET"])
@jwt_required()
def handle_get_stock_request():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    print(data)
    localResult = WR__Materials_new.get_materials(data)
    return localResult

@warehouse_routes.route('/get-urunler', methods=["POST"])
@jwt_required()
def handle_get_products_request():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    print(data)
    localResult = WR__Products.get_products(data)
    return localResult

@warehouse_routes.route('/get-lazer-gecmisi', methods=["POST"])
@jwt_required()
def handle_get_laser_history():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    localResult = WR__LazerStockTasks.get_logged_used_sheets()
    return localResult


@warehouse_routes.route('/get-lazer-rapor-file', methods=['POST'])
@jwt_required()
def handle_get_laser_report_file():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    data = request.json
    data_sent = data["data_sent"]
    file_name = data_sent["file_name"]
    date_string = data_sent["date"]
    localResult = WR__LazerStockTasks.get_report_file(file_name, date_string)
    return localResult

@warehouse_routes.route('/get-urun-resim', methods=["POST"])
@jwt_required()
def handle_get_product_photo_request():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    print(data)
    localResult = WR__Products.get_base64_product_photo(data)
    return localResult

@warehouse_routes.route('/urun-ekle', methods=['POST'])
@jwt_required()
def handle_product_add_request():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    data_received = data['data_sent']
    result = WR__Products.add_product(data_received)
    return result

@warehouse_routes.route('/urun-duzenle', methods=['POST'])
@jwt_required()
def handle_product_edit_request():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    data_received = data['data_sent']
    result = WR__Products.edit_product(data_received)
    return result

@warehouse_routes.route('/get-urun-bilesenleri-tek', methods=['POST'])
@jwt_required()
def handle_get_product_elements_one():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    data_received = data['data_sent']
    result = WR__Products.get_product_components_single(data_received)
    return result

@warehouse_routes.route('/scaledata', methods=['POST'])
@jwt_required()
def scale_data_request():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    if request.method == 'GET':
        data = {"hello" : "world"}
        return data
    
    elif request.method == 'POST':
        data = request.json

        if data['RequestType'] == "Material_Weighed_SaveToStock":
            result = WR__Materials_new.handle_scale_weighed_materials(data)

        elif data['RequestType'] == 'Material_Weighed_DontSaveToStock':
            pass

        elif data['RequestType'] == "x":
            pass

        return result

@warehouse_routes.route('/get-largest-plu', methods=["POST"])
@jwt_required()
def handle_get_largest_plu():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    data_sent = data['data_sent']
    localResult = WR__Materials_new.get_largest_plu()
    return localResult


#region shipments

@warehouse_routes.route('/get-shipments', methods=['POST'])
@jwt_required()
def handle_get_shipments():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    localResult = WR__Shipments.get_shipments(data)
    return localResult

@warehouse_routes.route('/sevkiyat-ekle', methods=['POST'])
@jwt_required()
def handle_add_shipment():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    data_sent = data['data_sent']
    localResult = WR__Shipments.add_shipment(data_sent)
    return localResult

@warehouse_routes.route('/get-sevkiyat-fatura-irsaliye', methods=['POST'])
@jwt_required()
def handle_get_pdf():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    data_sent = data['data_sent']
    localResult = WR__Shipments.get_invoice(data_sent)
    return localResult

@warehouse_routes.route('/get-sevkiyat-bilesenleri-tek', methods=["POST"])
@jwt_required()
def handle_get_shipment_elements_one():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    data_sent = data['data_sent']
    localResult = WR__Shipments.get_shipment_components_single(data_sent)
    return localResult


#endregion


#region Material Types
@warehouse_routes.route('/get-material-types', methods=['POST'])
@jwt_required()
def handle_get_material_types():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    response_data = WR__MaterialTypes.get_material_types_from_db(data)
    return response_data

@warehouse_routes.route('/add-material-type', methods=['POST'])
@jwt_required()
def handle_add_material_type():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    data_received = data['data_sent']
    print(data)
    response_data = WR__MaterialTypes.add_material_type_to_db(data_received)
    return response_data

@warehouse_routes.route('/edit-material-type', methods=['POST'])
@jwt_required()
def handle_edit_material_type():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    data_received = data['data_sent']
    response_data = WR__MaterialTypes.edit_material_type(data_received)
    return response_data

@warehouse_routes.route('/remove-material-type', methods=['POST'])
@jwt_required()
def handle_remove_material_type():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    data_received = data['data_sent']
    response_data = WR__MaterialTypes.remove_material_type(data_received)
    return response_data
#endregion

#region Material Categories
@warehouse_routes.route('/get-material-categories', methods=['POST'])
@jwt_required()
def handle_get_material_categories():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    response_data = WR__MaterialCategories.get_material_categories_from_db(data)
    return response_data

@warehouse_routes.route('/add-material-category', methods=['POST'])
@jwt_required()
def handle_add_material_category():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    data_received = data['data_sent']
    print(data)
    response_data = WR__MaterialCategories.add_material_category_to_db(data_received)
    return response_data

@warehouse_routes.route('/edit-material-category', methods=['POST'])
@jwt_required()
def handle_edit_material_category():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    data_received = data['data_sent']
    response_data = WR__MaterialCategories.edit_material_category(data_received)
    return response_data

@warehouse_routes.route('/remove-material-category', methods=['POST'])
@jwt_required()
def handle_remove_material_category():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    data_received = data['data_sent']
    response_data = WR__MaterialCategories.remove_material_category(data_received)
    return response_data
#endregion

#region Material Providers
@warehouse_routes.route('/get-material-providers', methods=['POST'])
@jwt_required()
def handle_get_material_providers():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    response_data = WR__MaterialProviders.get_material_providers_from_db(data)
    return response_data

@warehouse_routes.route('/yeni-tedarikci', methods=['POST'])
@jwt_required()
def handle_add_material_provider():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    data_received = data['data_sent']
    print(data)
    response_data = WR__MaterialProviders.add_material_provider_to_db(data_received)
    return response_data

@warehouse_routes.route('/tedarikci-duzenle', methods=['POST'])
@jwt_required()
def handle_edit_material_provider():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    data_received = data['data_sent']
    response_data = WR__MaterialProviders.edit_material_provider(data_received)
    return response_data

@warehouse_routes.route('/remove-material-provider', methods=['POST'])
@jwt_required()
def handle_remove_material_provider():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    data_received = data['data_sent']
    response_data = WR__MaterialProviders.remove_material_provider(data_received)
    return response_data

#endregion

#region Customers
@warehouse_routes.route('/get-musteriler', methods=['POST'])
@jwt_required()
def handle_get_customers():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    response_data = WR__Customers.get_customers_from_db(data)
    return response_data

@warehouse_routes.route('/yeni-musteri', methods=['POST'])
@jwt_required()
def handle_add_customer():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    data_received = data['data_sent']
    print(data)
    response_data = WR__Customers.add_customer_to_db(data_received)
    return response_data

@warehouse_routes.route('/musteri-duzenle', methods=['POST'])
@jwt_required()
def handle_edit_customer():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}

    data = request.json
    data_received = data['data_sent']
    response_data = WR__Customers.edit_customer(data_received)
    return response_data

@warehouse_routes.route('/remove-musteri', methods=['POST'])
@jwt_required()
def handle_remove_customer():
    access_granted = check_user_access(request.headers)
    if access_granted == False: return {"status" : "access_denied"}
    
    data = request.json
    data_received = data['data_sent']
    response_data = WR__Customers.remove_customer(data_received)
    return response_data

#endregion