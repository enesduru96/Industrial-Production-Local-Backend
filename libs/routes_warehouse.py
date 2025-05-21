
from flask import request, Blueprint
from libs import CloudRequests
from libs.Local_Requests import WR__MaterialTypes, WR__MaterialCategories, WR__MaterialProviders, WR__Customers, WR__Products, WR__Materials_new, WR___Main, WR__Shipments

warehouse_routes = Blueprint("warehouse_routes", __name__)

@warehouse_routes.route('/get-warehouse-config', methods=['POST'])
def handle_get_config():
    data = request.json
    localResult = WR___Main.get_warehouse_config()
    return localResult


#region Materials

@warehouse_routes.route('/yeni-hammadde', methods=['POST'])
def handle_add_material():
    data = request.json
    data_received = data['data_sent']
    localResult = WR__Materials_new.define_stock_material(data_received)

    print(localResult)
    return localResult

@warehouse_routes.route('/hammadde-duzenle', methods=['POST'])
def handle_edit_material():
    data = request.json
    data_received = data['data_sent']
    localResult = WR__Materials_new.edit_stock_material(data_received)
    print(localResult)
    return localResult

@warehouse_routes.route('/get-materials', methods=["POST", "GET"])
def handle_get_materials():
    data = request.json
    print(data)
    localResult = WR__Materials_new.get_materials(data)
    return localResult

@warehouse_routes.route('/add-malzeme-teslim', methods=["POST"])
def handle_add_material_delivery():
    data = request.json
    data_sent = data["data_sent"]
    localResult = WR__Materials_new.add_material_delivery(data_sent)
    return localResult

@warehouse_routes.route('/get-malzeme-teslim-gecmisi', methods=['POST'])
def handle_get_material_delivery_history():
    data = request.json
    localResult = WR__Materials_new.get_material_delivery_history()
    return localResult

#endregion


#region Products

@warehouse_routes.route('/get-urunler', methods=["POST"])
def handle_get_products():
    data = request.json
    print(data)
    localResult = WR__Products.get_products(data)
    return localResult

@warehouse_routes.route('/get-urun-resim', methods=["POST"])
def handle_get_product_image():
    data = request.json
    print(data)
    localResult = WR__Products.get_base64_product_photo(data)
    return localResult

@warehouse_routes.route('/urun-ekle', methods=['POST'])
def handle_add_product():
    data = request.json
    data_received = data['data_sent']
    localResult = WR__Products.add_product(data_received)
    print(localResult)
    return localResult

@warehouse_routes.route('/urun-duzenle', methods=['POST'])
def handle_edit_product():
    data = request.json
    data_received = data['data_sent']
    localResult = WR__Products.edit_product(data_received)
    print(localResult)
    return localResult

@warehouse_routes.route('/get-urun-bilesenleri-tek', methods=['POST'])
def handle_get_product_components_single():
    data = request.json
    data_received = data['data_sent']
    localResult = WR__Products.get_product_components_single(data_received)
    print(localResult)
    return localResult

#endregion

@warehouse_routes.route('/scaledata', methods=['POST'])
def handle_scale_data():
    if request.method == 'GET':
        data = {"hello" : "world"}
        return data
    
    elif request.method == 'POST':
        data = request.json

        if data['RequestType'] == "Material_Weighed_SaveToStock":
            localResult = WR__Materials_new.handle_scale_weighed_materials(data)
            cloudResult = CloudRequests.Handle_Scale_Weighed_Materials(data)

        elif data['RequestType'] == 'Material_Weighed_DontSaveToStock':
            pass

        elif data['RequestType'] == "x":
            pass

        return localResult

@warehouse_routes.route('/get-largest-plu', methods=["POST"])
def handle_get_largest_plu():
    data = request.json
    data_sent = data['data_sent']
    localResult = WR__Materials_new.get_largest_plu()
    return localResult


#region shipments

@warehouse_routes.route('/get-shipments', methods=['POST'])
def handle_get_shipments():
    data = request.json
    localResult = WR__Shipments.get_shipments(data)
    return localResult

@warehouse_routes.route('/sevkiyat-ekle', methods=['POST'])
def handle_add_shipment():
    data = request.json
    data_sent = data['data_sent']
    localResult = WR__Shipments.add_shipment(data_sent)
    return localResult

@warehouse_routes.route('/get-sevkiyat-fatura-irsaliye', methods=['POST'])
def handle_get_shipment_invoice():
    data = request.json
    data_sent = data['data_sent']
    localResult = WR__Shipments.get_invoice(data_sent)
    return localResult

@warehouse_routes.route('/get-sevkiyat-bilesenleri-tek', methods=["POST"])
def handle_get_shipment_components_single():
    data = request.json
    data_sent = data['data_sent']
    localResult = WR__Shipments.get_shipment_components_single(data_sent)
    return localResult


#endregion


#region Material Types
@warehouse_routes.route('/get-material-types', methods=['POST'])
def handle_get_material_types():
    data = request.json
    response_data = WR__MaterialTypes.get_material_types_from_db(data)
    return response_data

@warehouse_routes.route('/add-material-type', methods=['POST'])
def handle_add_material_type():
    data = request.json
    data_received = data['data_sent']
    print(data)
    response_data = WR__MaterialTypes.add_material_type_to_db(data_received)
    return response_data

@warehouse_routes.route('/edit-material-type', methods=['POST'])
def handle_edit_material_type():
    data = request.json
    data_received = data['data_sent']
    response_data = WR__MaterialTypes.edit_material_type(data_received)
    return response_data

@warehouse_routes.route('/remove-material-type', methods=['POST'])
def handle_remove_material_type():
    data = request.json
    data_received = data['data_sent']
    response_data = WR__MaterialTypes.remove_material_type(data_received)
    return response_data
#endregion

#region Material Categories
@warehouse_routes.route('/get-material-categories', methods=['POST'])
def handle_get_material_categories():
    data = request.json
    response_data = WR__MaterialCategories.get_material_categories_from_db(data)
    return response_data

@warehouse_routes.route('/add-material-category', methods=['POST'])
def handle_add_material_category():
    data = request.json
    data_received = data['data_sent']
    print(data)
    response_data = WR__MaterialCategories.add_material_category_to_db(data_received)
    return response_data

@warehouse_routes.route('/edit-material-category', methods=['POST'])
def handle_edit_material_category():
    data = request.json
    data_received = data['data_sent']
    response_data = WR__MaterialCategories.edit_material_category(data_received)
    return response_data

@warehouse_routes.route('/remove-material-category', methods=['POST'])
def handle_remove_material_category():
    data = request.json
    data_received = data['data_sent']
    response_data = WR__MaterialCategories.remove_material_category(data_received)
    return response_data
#endregion

#region Material Providers
@warehouse_routes.route('/get-material-providers', methods=['POST'])
def handle_get_material_providers():
    data = request.json
    response_data = WR__MaterialProviders.get_material_providers_from_db(data)
    return response_data

@warehouse_routes.route('/yeni-tedarikci', methods=['POST'])
def handle_add_material_provider():
    data = request.json
    data_received = data['data_sent']
    print(data)
    response_data = WR__MaterialProviders.add_material_provider_to_db(data_received)
    return response_data

@warehouse_routes.route('/tedarikci-duzenle', methods=['POST'])
def handle_edit_material_provider():
    data = request.json
    data_received = data['data_sent']
    response_data = WR__MaterialProviders.edit_material_provider(data_received)
    return response_data

@warehouse_routes.route('/remove-material-provider', methods=['POST'])
def handle_remove_material_provider():
    data = request.json
    data_received = data['data_sent']
    response_data = WR__MaterialProviders.remove_material_provider(data_received)
    return response_data

#endregion

#region Customers
@warehouse_routes.route('/get-musteriler', methods=['POST'])
def handle_get_customers():
    data = request.json
    response_data = WR__Customers.get_customers_from_db(data)
    return response_data

@warehouse_routes.route('/yeni-musteri', methods=['POST'])
def handle_add_customer():
    data = request.json
    data_received = data['data_sent']
    print(data)
    response_data = WR__Customers.add_customer_to_db(data_received)
    return response_data

@warehouse_routes.route('/musteri-duzenle', methods=['POST'])
def handle_edit_customer():
    data = request.json
    data_received = data['data_sent']
    response_data = WR__Customers.edit_customer(data_received)
    return response_data

@warehouse_routes.route('/remove-musteri', methods=['POST'])
def handle_remove_customer():
    data = request.json
    data_received = data['data_sent']
    response_data = WR__Customers.remove_customer(data_received)
    return response_data

#endregion