# 🚚 Calculador de Frete para Shopify

## Integração com API do Melhor Envio

Este projeto implementa um calculador de frete completo para lojas Shopify, permitindo que os clientes vejam os custos e prazos de entrega **antes** de ir para o checkout da Cartpanda.

---

## 🎯 Objetivo

Resolver o problema de não ter um calculador de frete na página do produto da loja Shopify (tema Warehouse), mostrando valores similares aos da Cartpanda para criar uma experiência consistente.

---

## ✨ Funcionalidades

- **Cálculo em tempo real** via API do Melhor Envio
- **Interface responsiva** compatível com tema Warehouse
- **Múltiplas transportadoras** (Correios, Jadlog, etc.)
- **Valores personalizados** (custom_price e custom_delivery_time)
- **Fácil integração** no Shopify
- **Design moderno** com animações suaves

---

## 📦 Estrutura do Projeto

```
calculador-frete/
├── src/
│   ├── services/
│   │   └── melhor_envio_service.py    # Integração com API Melhor Envio
│   ├── routes/
│   │   └── shipping.py                # Endpoints da API
│   ├── static/
│   │   ├── calculador-frete.js        # JavaScript do calculador
│   │   ├── calculador-frete.css       # Estilos CSS
│   │   └── index.html                 # Página de demonstração
│   └── main.py                        # Aplicação Flask principal
├── INTEGRACAO_SHOPIFY.md              # Guia de integração detalhado
└── README.md                          # Este arquivo
```

---

## 🚀 Como Usar

### 1. Configurar o Backend

```bash
# Instalar dependências
cd calculador-frete
source venv/bin/activate
pip install -r requirements.txt

# Configurar variáveis de ambiente
export MELHOR_ENVIO_TOKEN="seu_token_aqui"
export MELHOR_ENVIO_SANDBOX="false"  # true para sandbox

# Executar aplicação
python src/main.py
```

### 2. Integrar no Shopify

1. **Upload dos arquivos** para pasta `assets/` do tema:
   - `calculador-frete.js`
   - `calculador-frete.css`

2. **Modificar `product-info.liquid`**:
   ```liquid
   {{ 'calculador-frete.css' | asset_url | stylesheet_tag }}
   
   <div id="calculador-frete-{{ product.id }}"></div>
   
   <script src="{{ 'calculador-frete.js' | asset_url }}"></script>
   <script>
   CalculadorFrete.init({
     apiUrl: 'https://sua-api.herokuapp.com',
     fromPostalCode: '01001000', // SEU CEP
     containerId: 'calculador-frete-{{ product.id }}'
   });
   </script>
   ```

3. **Configurar metafields** (opcional):
   - `custom.weight` (Decimal)
   - `custom.width` (Integer)
   - `custom.height` (Integer)
   - `custom.length` (Integer)

---

## 🔧 Configuração da API do Melhor Envio

### Obter Token

1. Acesse [Melhor Envio](https://www.melhorenvio.com.br/)
2. Vá em **Configurações > Aplicativos**
3. Crie um novo aplicativo
4. Anote o **Access Token**

### Endpoints Disponíveis

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/shipping/health` | GET | Status da API |
| `/api/shipping/calculate` | POST | Cálculo completo |
| `/api/shipping/calculate-simple` | POST | Cálculo simplificado |
| `/api/shipping/calculate-shopify` | POST | Específico para Shopify |
| `/api/shipping/validate-postal-code` | POST | Validar CEP |

---

## 💡 Exemplo de Uso

### JavaScript

```javascript
// Inicializar calculador
const calculator = CalculadorFrete.init({
  apiUrl: 'https://sua-api.com',
  fromPostalCode: '01001000',
  containerId: 'calculador-frete',
  productData: {
    id: 'produto-123',
    price: 89.90,
    weight: 0.5,
    width: 15,
    height: 10,
    length: 20,
    quantity: 1
  }
});

// Recalcular com novos dados
calculator.recalculate({
  price: 120.00,
  weight: 0.8
});
```

### API Request

```bash
curl -X POST https://sua-api.com/api/shipping/calculate-simple \
  -H "Content-Type: application/json" \
  -d '{
    "from_postal_code": "01001000",
    "to_postal_code": "20040020",
    "weight": 0.5,
    "width": 15,
    "height": 10,
    "length": 20,
    "value": 89.90
  }'
```

### API Response

```json
{
  "success": true,
  "shipping_options": [
    {
      "id": 1,
      "name": "PAC",
      "company": "Correios",
      "price": 15.50,
      "formatted_price": "R$ 15,50",
      "delivery_time": 5,
      "formatted_delivery": "5 dias úteis"
    }
  ],
  "cheapest": { /* opção mais barata */ },
  "fastest": { /* opção mais rápida */ }
}
```

---

## 🎨 Personalização

### CSS Customizado

```css
.calculador-frete {
  border-color: var(--color-primary);
}

.calculador-frete__button {
  background-color: var(--color-button);
}

.calculador-frete__option--recommended {
  border-color: var(--color-success);
}
```

### Tema Escuro

O calculador suporta automaticamente tema escuro via `prefers-color-scheme: dark`.

---

## 📱 Responsividade

- **Desktop**: Layout em linha
- **Tablet**: Layout adaptativo
- **Mobile**: Layout em coluna
- **Touch**: Suporte completo a touch

---

## 🔒 Segurança

- **CORS** habilitado para integração
- **Validação** de CEPs
- **Rate limiting** respeitado
- **Tokens** seguros via variáveis de ambiente

---

## 🧪 Testes

### Testar Localmente

```bash
# Executar aplicação
python src/main.py

# Acessar demonstração
http://localhost:5000
```

### Testar API

```bash
# Health check
curl http://localhost:5000/api/shipping/health

# Calcular frete
curl -X POST http://localhost:5000/api/shipping/calculate-simple \
  -H "Content-Type: application/json" \
  -d '{"from_postal_code":"01001000","to_postal_code":"20040020","weight":0.5}'
```

---

## 🚀 Deploy

### Heroku

```bash
# Criar app
heroku create sua-api-frete

# Configurar variáveis
heroku config:set MELHOR_ENVIO_TOKEN=seu_token
heroku config:set MELHOR_ENVIO_SANDBOX=false

# Deploy
git push heroku main
```

### Railway

```bash
# Conectar repositório
railway login
railway link

# Configurar variáveis no dashboard
# Deploy automático via Git
```

---

## 📋 Checklist de Integração

- [ ] Token do Melhor Envio configurado
- [ ] Backend deployado e funcionando
- [ ] Arquivos CSS/JS no tema Shopify
- [ ] Código adicionado em `product-info.liquid`
- [ ] Metafields configurados (opcional)
- [ ] Testes realizados em diferentes dispositivos
- [ ] CEP de origem configurado corretamente

---

## 🔧 Solução de Problemas

### Calculador não aparece
- Verifique se os arquivos estão na pasta `assets/`
- Confirme se a URL da API está correta
- Verifique o console do navegador

### Erro de token
- Confirme se o token está correto
- Verifique se está usando sandbox/produção adequadamente
- Teste o token diretamente na API do Melhor Envio

### Valores diferentes da Cartpanda
- Verifique se está usando `custom_price` e `custom_delivery_time`
- Confirme as dimensões dos produtos
- Compare configurações entre as plataformas

---

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique a documentação do [Melhor Envio](https://docs.melhorenvio.com.br/)
2. Teste a API diretamente
3. Verifique os logs do backend
4. Entre em contato com suporte técnico

---

## 📄 Licença

Este projeto é fornecido como está, para uso interno da loja.

---

## 🎉 Resultado Final

Após a integração, seus clientes poderão:

✅ **Ver fretes na página do produto**  
✅ **Comparar transportadoras e prazos**  
✅ **Ter valores similares** aos do checkout  
✅ **Experiência consistente** em toda a jornada  

O calculador funciona como um "espelho" da Cartpanda, mostrando as mesmas opções de frete antes do checkout, melhorando significativamente a experiência de compra.

