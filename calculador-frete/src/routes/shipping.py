from flask import Blueprint, request, jsonify
import os
from src.services.melhor_envio_service import MelhorEnvioService

shipping_bp = Blueprint('shipping', __name__)

# Configuração do token - em produção, use variáveis de ambiente
MELHOR_ENVIO_TOKEN = os.getenv('MELHOR_ENVIO_TOKEN', 'seu_token_aqui')
IS_SANDBOX = os.getenv('MELHOR_ENVIO_SANDBOX', 'true').lower() == 'true'

@shipping_bp.route('/calculate', methods=['POST'])
def calculate_shipping():
    """
    Endpoint para calcular frete
    
    Payload esperado:
    {
        "from_postal_code": "01001000",
        "to_postal_code": "20040020",
        "products": [
            {
                "id": "1",
                "width": 10,
                "height": 5,
                "length": 15,
                "weight": 0.3,
                "insurance_value": 50.00,
                "quantity": 1
            }
        ],
        "options": {
            "receipt": false,
            "own_hand": false
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados não fornecidos'
            }), 400
        
        # Validar campos obrigatórios
        required_fields = ['from_postal_code', 'to_postal_code', 'products']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório ausente: {field}'
                }), 400
        
        # Inicializar serviço
        melhor_envio = MelhorEnvioService(MELHOR_ENVIO_TOKEN, IS_SANDBOX)
        
        # Validar CEPs
        if not melhor_envio.validate_postal_code(data['from_postal_code']):
            return jsonify({
                'success': False,
                'error': 'CEP de origem inválido'
            }), 400
        
        if not melhor_envio.validate_postal_code(data['to_postal_code']):
            return jsonify({
                'success': False,
                'error': 'CEP de destino inválido'
            }), 400
        
        # Calcular frete
        shipping_data = melhor_envio.calculate_shipping(
            from_postal_code=data['from_postal_code'],
            to_postal_code=data['to_postal_code'],
            products=data['products'],
            options=data.get('options', {})
        )
        
        if not shipping_data:
            return jsonify({
                'success': False,
                'error': 'Erro ao calcular frete'
            }), 500
        
        # Formatar resposta
        formatted_options = melhor_envio.format_shipping_options(shipping_data)
        
        return jsonify({
            'success': True,
            'shipping_options': formatted_options,
            'cheapest': melhor_envio.get_cheapest_option(shipping_data),
            'fastest': melhor_envio.get_fastest_option(shipping_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@shipping_bp.route('/calculate-simple', methods=['POST'])
def calculate_simple_shipping():
    """
    Endpoint simplificado para calcular frete com dados básicos
    
    Payload esperado:
    {
        "from_postal_code": "01001000",
        "to_postal_code": "20040020",
        "weight": 0.3,
        "width": 10,
        "height": 5,
        "length": 15,
        "value": 50.00
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados não fornecidos'
            }), 400
        
        # Validar campos obrigatórios
        required_fields = ['from_postal_code', 'to_postal_code', 'weight']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório ausente: {field}'
                }), 400
        
        # Valores padrão
        default_dimensions = {
            'width': 10,
            'height': 5,
            'length': 15
        }
        
        # Criar produto
        product = {
            'id': 'product_1',
            'width': data.get('width', default_dimensions['width']),
            'height': data.get('height', default_dimensions['height']),
            'length': data.get('length', default_dimensions['length']),
            'weight': data['weight'],
            'insurance_value': data.get('value', 0),
            'quantity': data.get('quantity', 1)
        }
        
        # Inicializar serviço
        melhor_envio = MelhorEnvioService(MELHOR_ENVIO_TOKEN, IS_SANDBOX)
        
        # Calcular frete
        shipping_data = melhor_envio.calculate_shipping(
            from_postal_code=data['from_postal_code'],
            to_postal_code=data['to_postal_code'],
            products=[product],
            options=data.get('options', {})
        )
        
        if not shipping_data:
            return jsonify({
                'success': False,
                'error': 'Erro ao calcular frete'
            }), 500
        
        # Formatar resposta
        formatted_options = melhor_envio.format_shipping_options(shipping_data)
        
        return jsonify({
            'success': True,
            'shipping_options': formatted_options,
            'cheapest': melhor_envio.get_cheapest_option(shipping_data),
            'fastest': melhor_envio.get_fastest_option(shipping_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@shipping_bp.route('/calculate-shopify', methods=['POST'])
def calculate_shopify_shipping():
    """
    Endpoint específico para produtos do Shopify
    
    Payload esperado:
    {
        "from_postal_code": "01001000",
        "to_postal_code": "20040020",
        "shopify_product": {
            "id": 123456,
            "price": "50.00",
            "weight": 300,  // em gramas
            "width": 10,
            "height": 5,
            "length": 15
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados não fornecidos'
            }), 400
        
        # Validar campos obrigatórios
        required_fields = ['from_postal_code', 'to_postal_code', 'shopify_product']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório ausente: {field}'
                }), 400
        
        # Inicializar serviço
        melhor_envio = MelhorEnvioService(MELHOR_ENVIO_TOKEN, IS_SANDBOX)
        
        # Converter produto do Shopify
        shopify_product = data['shopify_product']
        
        # Converter peso de gramas para kg se necessário
        weight = shopify_product.get('weight', 300)
        if weight > 50:  # Assumir que valores > 50 estão em gramas
            weight = weight / 1000
        
        product = {
            'id': str(shopify_product.get('id', 'default')),
            'width': shopify_product.get('width', 10),
            'height': shopify_product.get('height', 5),
            'length': shopify_product.get('length', 15),
            'weight': weight,
            'insurance_value': float(shopify_product.get('price', 0)),
            'quantity': int(shopify_product.get('quantity', 1))
        }
        
        # Calcular frete
        shipping_data = melhor_envio.calculate_shipping(
            from_postal_code=data['from_postal_code'],
            to_postal_code=data['to_postal_code'],
            products=[product],
            options=data.get('options', {})
        )
        
        if not shipping_data:
            return jsonify({
                'success': False,
                'error': 'Erro ao calcular frete'
            }), 500
        
        # Formatar resposta
        formatted_options = melhor_envio.format_shipping_options(shipping_data)
        
        return jsonify({
            'success': True,
            'shipping_options': formatted_options,
            'cheapest': melhor_envio.get_cheapest_option(shipping_data),
            'fastest': melhor_envio.get_fastest_option(shipping_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@shipping_bp.route('/validate-postal-code', methods=['POST'])
def validate_postal_code():
    """
    Endpoint para validar CEP
    
    Payload esperado:
    {
        "postal_code": "01001000"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'postal_code' not in data:
            return jsonify({
                'success': False,
                'error': 'CEP não fornecido'
            }), 400
        
        melhor_envio = MelhorEnvioService(MELHOR_ENVIO_TOKEN, IS_SANDBOX)
        is_valid = melhor_envio.validate_postal_code(data['postal_code'])
        
        return jsonify({
            'success': True,
            'valid': is_valid,
            'postal_code': data['postal_code']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@shipping_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint para verificar se a API está funcionando
    """
    return jsonify({
        'success': True,
        'message': 'API de cálculo de frete funcionando',
        'sandbox': IS_SANDBOX
    })

