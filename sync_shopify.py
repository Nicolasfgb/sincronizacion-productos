from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Credenciales Shopify (reemplaza con tus datos)
SHOPIFY_STORE_ORIGIN = "parfumsnoxfr.myshopify.com"
SHOPIFY_API_KEY_ORIGIN = "ef86d3cd35aca52d7a45fc01700a04e7"
SHOPIFY_PASSWORD_ORIGIN = "fa694269ac775023c810baeb80fad902"

SHOPIFY_STORE_DEST = "parfumsnoxeu.myshopify.com"
SHOPIFY_API_KEY_DEST = "86943d14b72c92c66d2f7d6f2b2cd78e"
SHOPIFY_PASSWORD_DEST = "d7e0601e49508651865d2ff840be34f4"

# URLs API Shopify
URL_ORIGIN = f"https://{SHOPIFY_API_KEY_ORIGIN}:{SHOPIFY_PASSWORD_ORIGIN}@{SHOPIFY_STORE_ORIGIN}/admin/api/2023-04/products.json"
URL_DEST = f"https://{SHOPIFY_API_KEY_DEST}:{SHOPIFY_PASSWORD_DEST}@{SHOPIFY_STORE_DEST}/admin/api/2023-04/products.json"

def obtener_productos(shop_url):
    """Obtiene la lista de productos de una tienda Shopify"""
    response = requests.get(shop_url)
    if response.status_code == 200:
        return response.json().get("products", [])
    return []

def crear_producto_en_destino(producto):
    """Crea un producto en la tienda de destino con todos sus detalles"""
    
    # Elimina los IDs para evitar conflictos
    keys_a_eliminar = ["id", "admin_graphql_api_id", "created_at", "updated_at"]
    for key in keys_a_eliminar:
        producto.pop(key, None)

    # Prepara los datos para la nueva tienda
    data = {"product": producto}
    
    # Enviar a la API de la tienda destino
    response = requests.post(URL_DEST, json=data)
    
    if response.status_code == 201:
        return True
    else:
        print(f"Error creando producto: {response.json()}")
        return False

@app.route('/sync-products', methods=['GET'])
def sync_products():
    """Sincroniza todos los productos con sus detalles de la tienda origen a la tienda destino"""
    
    productos_origen = obtener_productos(URL_ORIGIN)
    productos_destino = obtener_productos(URL_DEST)

    # Obtener los títulos de los productos de la tienda destino
    productos_destino_titles = {p["title"] for p in productos_destino}

    # Filtrar productos nuevos (los que no existen en la tienda destino)
    nuevos_productos = [p for p in productos_origen if p["title"] not in productos_destino_titles]

    # Crear productos nuevos en la tienda destino
    productos_creados = 0
    for producto in nuevos_productos:
        if crear_producto_en_destino(producto):
            productos_creados += 1

    return jsonify({
        "message": "Sincronización completada",
        "productos_agregados": productos_creados
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

