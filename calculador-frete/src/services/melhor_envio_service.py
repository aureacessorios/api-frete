import requests
import json
from typing import List, Dict, Optional

class MelhorEnvioService:
    def __init__(self, access_token: str, is_sandbox: bool = True):
        """
        Inicializa o serviço do Melhor Envio
        
        Args:
            access_token: Token de acesso da API
            is_sandbox: Se deve usar o ambiente sandbox (True) ou produção (False)
        """
        self.access_token = access_token
        self.base_url = "https://sandbox.melhorenvio.com.br" if is_sandbox else "https://www.melhorenvio.com.br"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'CalculadorFrete/1.0 (contato@loja.com)'
        }
    
    def calculate_shipping(self, from_postal_code: str, to_postal_code: str, 
                          products: List[Dict], options: Dict = None) -> List[Dict]:
        """
        Calcula o frete para uma lista de produtos
        
        Args:
            from_postal_code: CEP de origem
            to_postal_code: CEP de destino
            products: Lista de produtos com dimensões e peso
            options: Opções adicionais (receipt, own_hand, insurance_value)
            
        Returns:
            Lista de cotações de frete
        """
        try:
            url = f"{self.base_url}/api/v2/me/shipment/calculate"
            
            # Estrutura padrão da requisição
            payload = {
                "from": {
                    "postal_code": from_postal_code.replace("-", "")
                },
                "to": {
                    "postal_code": to_postal_code.replace("-", "")
                },
                "products": products
            }
            
            # Adicionar opções se fornecidas
            if options:
                payload["options"] = options
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Erro ao calcular frete: {e}")
            return []
    
    def calculate_shipping_by_package(self, from_postal_code: str, to_postal_code: str,
                                    package: Dict, options: Dict = None) -> List[Dict]:
        """
        Calcula o frete para um pacote específico
        
        Args:
            from_postal_code: CEP de origem
            to_postal_code: CEP de destino
            package: Dados do pacote (height, width, length, weight)
            options: Opções adicionais
            
        Returns:
            Lista de cotações de frete
        """
        try:
            url = f"{self.base_url}/api/v2/me/shipment/calculate"
            
            payload = {
                "from": {
                    "postal_code": from_postal_code.replace("-", "")
                },
                "to": {
                    "postal_code": to_postal_code.replace("-", "")
                },
                "package": package
            }
            
            if options:
                payload["options"] = options
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Erro ao calcular frete por pacote: {e}")
            return []
    
    def format_shipping_options(self, shipping_data: List[Dict]) -> List[Dict]:
        """
        Formata os dados de frete para exibição
        
        Args:
            shipping_data: Dados brutos da API do Melhor Envio
            
        Returns:
            Lista formatada de opções de frete
        """
        formatted_options = []
        
        for option in shipping_data:
            if option.get('error'):
                continue
                
            formatted_option = {
                'id': option.get('id'),
                'name': option.get('name', ''),
                'company': option.get('company', {}).get('name', ''),
                'price': option.get('custom_price', option.get('price', 0)),
                'delivery_time': option.get('custom_delivery_time', option.get('delivery_time', 0)),
                'currency': option.get('currency', 'R$'),
                'delivery_range': option.get('delivery_range', {}),
                'packages': option.get('packages', []),
                'additional_services': option.get('additional_services', {}),
                'company_logo': option.get('company', {}).get('picture', ''),
                'error': option.get('error')
            }
            
            # Formatar preço
            if formatted_option['price']:
                formatted_option['formatted_price'] = f"R$ {formatted_option['price']:.2f}".replace('.', ',')
            
            # Formatar prazo de entrega
            delivery_time = formatted_option['delivery_time']
            if delivery_time == 0:
                formatted_option['formatted_delivery'] = "Mesmo dia"
            elif delivery_time == 1:
                formatted_option['formatted_delivery'] = "1 dia útil"
            else:
                formatted_option['formatted_delivery'] = f"{delivery_time} dias úteis"
            
            formatted_options.append(formatted_option)
        
        # Ordenar por preço
        formatted_options.sort(key=lambda x: x['price'] if x['price'] else float('inf'))
        
        return formatted_options
    
    def get_cheapest_option(self, shipping_data: List[Dict]) -> Optional[Dict]:
        """
        Retorna a opção de frete mais barata
        
        Args:
            shipping_data: Dados de frete da API
            
        Returns:
            Opção mais barata ou None
        """
        formatted_options = self.format_shipping_options(shipping_data)
        
        if formatted_options:
            return formatted_options[0]
        
        return None
    
    def get_fastest_option(self, shipping_data: List[Dict]) -> Optional[Dict]:
        """
        Retorna a opção de frete mais rápida
        
        Args:
            shipping_data: Dados de frete da API
            
        Returns:
            Opção mais rápida ou None
        """
        formatted_options = self.format_shipping_options(shipping_data)
        
        if formatted_options:
            # Ordenar por tempo de entrega
            fastest_options = sorted(formatted_options, key=lambda x: x['delivery_time'])
            return fastest_options[0] if fastest_options else None
        
        return None
    
    def validate_postal_code(self, postal_code: str) -> bool:
        """
        Valida se o CEP está no formato correto
        
        Args:
            postal_code: CEP a ser validado
            
        Returns:
            True se válido, False caso contrário
        """
        import re
        
        # Remove caracteres não numéricos
        clean_postal_code = re.sub(r'\D', '', postal_code)
        
        # Verifica se tem 8 dígitos
        return len(clean_postal_code) == 8 and clean_postal_code.isdigit()
    
    def create_product_from_shopify(self, shopify_product: Dict) -> Dict:
        """
        Converte um produto do Shopify para o formato do Melhor Envio
        
        Args:
            shopify_product: Dados do produto do Shopify
            
        Returns:
            Produto formatado para o Melhor Envio
        """
        # Valores padrão caso não estejam definidos
        default_dimensions = {
            'width': 10,   # cm
            'height': 5,   # cm  
            'length': 15,  # cm
            'weight': 0.3  # kg
        }
        
        # Extrair dimensões do produto (assumindo que estão em metafields ou propriedades)
        product = {
            'id': str(shopify_product.get('id', 'default')),
            'width': shopify_product.get('width', default_dimensions['width']),
            'height': shopify_product.get('height', default_dimensions['height']),
            'length': shopify_product.get('length', default_dimensions['length']),
            'weight': shopify_product.get('weight', default_dimensions['weight']),
            'insurance_value': float(shopify_product.get('price', 0)),
            'quantity': int(shopify_product.get('quantity', 1))
        }
        
        return product

