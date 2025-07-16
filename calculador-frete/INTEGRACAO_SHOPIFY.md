# Integração do Calculador de Frete no Shopify

## Guia Completo para Tema Warehouse

Este guia te ajudará a integrar o calculador de frete na sua loja Shopify usando o tema Warehouse, especificamente no arquivo `product-info.liquid`.

---

## 📋 Pré-requisitos

1. **Acesso ao admin da sua loja Shopify**
2. **Token da API do Melhor Envio** (sandbox ou produção)
3. **Backend da API de frete** (fornecido neste projeto)
4. **Conhecimento básico de Liquid** (linguagem de template do Shopify)

---

## 🚀 Passo 1: Deploy do Backend

### 1.1 Configurar Variáveis de Ambiente

Antes de fazer deploy, configure as seguintes variáveis:

```bash
MELHOR_ENVIO_TOKEN=seu_token_aqui
MELHOR_ENVIO_SANDBOX=false  # true para sandbox, false para produção
```

### 1.2 Deploy da API

O backend precisa estar rodando em um servidor acessível. Você pode usar:
- Heroku
- Railway
- DigitalOcean
- AWS
- Ou qualquer outro provedor

**URL da API será algo como:** `https://sua-api-frete.herokuapp.com`

---

## 🎨 Passo 2: Upload dos Arquivos para o Shopify

### 2.1 Acessar o Editor de Código

1. No admin do Shopify, vá em **Online Store > Themes**
2. No tema ativo (Warehouse), clique em **Actions > Edit code**

### 2.2 Upload dos Arquivos CSS e JavaScript

1. **Na pasta `assets/`**, clique em **Add a new asset**
2. **Upload o arquivo `calculador-frete.css`**
3. **Upload o arquivo `calculador-frete.js`**

---

## 📝 Passo 3: Modificar o Arquivo product-info.liquid

### 3.1 Localizar o Arquivo

Na estrutura de arquivos, encontre:
```
sections/
  └── product-info.liquid
```

### 3.2 Adicionar o CSS (no início do arquivo)

Adicione no topo do arquivo `product-info.liquid`:

```liquid
{{ 'calculador-frete.css' | asset_url | stylesheet_tag }}
```

### 3.3 Encontrar o Local de Inserção

Procure por uma seção similar a esta no arquivo:

```liquid
<div class="product-form__buttons">
  <!-- Botões de compra existem aqui -->
</div>
```

### 3.4 Adicionar o Calculador de Frete

**ANTES** da seção de botões de compra, adicione:

```liquid
{%- comment -%}
  Calculador de Frete - Melhor Envio
{%- endcomment -%}
<div class="product-form__frete">
  <div id="calculador-frete-{{ product.id }}"></div>
</div>
```

### 3.5 Adicionar o JavaScript (no final do arquivo)

No final do arquivo `product-info.liquid`, antes da tag `</div>` final, adicione:

```liquid
<script src="{{ 'calculador-frete.js' | asset_url }}" defer></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
  // Configuração do calculador
  const freteConfig = {
    apiUrl: 'https://sua-api-frete.herokuapp.com', // SUBSTITUA pela sua URL
    fromPostalCode: '01001000', // SUBSTITUA pelo seu CEP
    containerId: 'calculador-frete-{{ product.id }}',
    productData: {
      id: '{{ product.id }}',
      price: {{ product.price | divided_by: 100.0 }},
      weight: {% if product.metafields.custom.weight %}{{ product.metafields.custom.weight }}{% else %}0.5{% endif %},
      width: {% if product.metafields.custom.width %}{{ product.metafields.custom.width }}{% else %}15{% endif %},
      height: {% if product.metafields.custom.height %}{{ product.metafields.custom.height }}{% else %}10{% endif %},
      length: {% if product.metafields.custom.length %}{{ product.metafields.custom.length }}{% else %}20{% endif %},
      quantity: 1
    }
  };
  
  // Inicializar calculador
  CalculadorFrete.init(freteConfig);
});
</script>
```

---

## ⚙️ Passo 4: Configurar Metafields (Opcional mas Recomendado)

Para que o calculador use as dimensões reais dos produtos, configure metafields:

### 4.1 Criar Metafields

No admin do Shopify:
1. Vá em **Settings > Metafields**
2. Selecione **Products**
3. Adicione os seguintes metafields:

| Nome | Namespace e Key | Tipo |
|------|----------------|------|
| Peso | `custom.weight` | Decimal |
| Largura | `custom.width` | Integer |
| Altura | `custom.height` | Integer |
| Comprimento | `custom.length` | Integer |

### 4.2 Preencher os Metafields

Para cada produto:
1. Vá em **Products > [Produto específico]**
2. Role até **Metafields**
3. Preencha:
   - **Peso**: em quilogramas (ex: 0.5)
   - **Largura**: em centímetros (ex: 15)
   - **Altura**: em centímetros (ex: 10)
   - **Comprimento**: em centímetros (ex: 20)

---

## 🎯 Passo 5: Personalização Avançada

### 5.1 Integração com Variantes

Se você quiser que o frete mude conforme a variante selecionada:

```liquid
<script>
document.addEventListener('DOMContentLoaded', function() {
  let calculator;
  
  function initCalculator(variantId) {
    const variant = {{ product.variants | json }}.find(v => v.id == variantId);
    
    const freteConfig = {
      apiUrl: 'https://sua-api-frete.herokuapp.com',
      fromPostalCode: '01001000',
      containerId: 'calculador-frete-{{ product.id }}',
      productData: {
        id: variant.id,
        price: variant.price / 100,
        weight: variant.weight / 1000 || 0.5, // Shopify retorna em gramas
        width: 15, // Use metafields se disponível
        height: 10,
        length: 20,
        quantity: 1
      }
    };
    
    calculator = CalculadorFrete.init(freteConfig);
  }
  
  // Inicializar com primeira variante
  const firstVariant = {{ product.selected_or_first_available_variant.id }};
  initCalculator(firstVariant);
  
  // Atualizar quando variante mudar
  document.addEventListener('change', function(e) {
    if (e.target.name === 'id') {
      initCalculator(e.target.value);
    }
  });
});
</script>
```

### 5.2 Estilização Personalizada

Adicione CSS personalizado no arquivo `calculador-frete.css` ou crie um arquivo separado:

```css
/* Personalização para tema Warehouse */
.calculador-frete {
  margin: 20px 0;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
}

.calculador-frete__title {
  color: var(--color-foreground);
}

.calculador-frete__button {
  background-color: var(--color-button);
  color: var(--color-button-text);
}

.calculador-frete__button:hover {
  background-color: var(--color-button-hover);
}
```

---

## 🧪 Passo 6: Teste e Validação

### 6.1 Teste Local

1. **Salve todas as alterações** no editor de código
2. **Visualize sua loja** em uma nova aba
3. **Vá para uma página de produto**
4. **Teste o calculador** com diferentes CEPs

### 6.2 Teste em Dispositivos Móveis

1. **Abra a loja no celular**
2. **Teste a responsividade** do calculador
3. **Verifique se funciona** em diferentes navegadores

### 6.3 Verificar Console de Erros

1. **Abra as ferramentas de desenvolvedor** (F12)
2. **Vá na aba Console**
3. **Procure por erros** relacionados ao calculador

---

## 🔧 Solução de Problemas

### Problema: Calculador não aparece

**Possíveis causas:**
- Arquivos CSS/JS não foram carregados corretamente
- Erro na configuração da API
- Container ID incorreto

**Solução:**
1. Verifique se os arquivos estão na pasta `assets/`
2. Confirme se a URL da API está correta
3. Verifique o console do navegador para erros

### Problema: Erro "Token inválido"

**Solução:**
1. Verifique se o token do Melhor Envio está correto
2. Confirme se está usando sandbox/produção corretamente
3. Teste o token diretamente na API do Melhor Envio

### Problema: Frete não calcula

**Possíveis causas:**
- CEP de origem inválido
- Dimensões do produto incorretas
- Problema na API do Melhor Envio

**Solução:**
1. Verifique o CEP de origem
2. Confirme as dimensões do produto
3. Teste a API diretamente

---

## 📱 Exemplo Completo para product-info.liquid

Aqui está um exemplo completo de como deve ficar a integração:

```liquid
{{ 'calculador-frete.css' | asset_url | stylesheet_tag }}

<div class="product-form">
  <!-- Conteúdo existente do produto -->
  
  {%- comment -%}
    Calculador de Frete
  {%- endcomment -%}
  <div class="product-form__frete">
    <div id="calculador-frete-{{ product.id }}"></div>
  </div>
  
  <div class="product-form__buttons">
    <!-- Botões de compra existentes -->
  </div>
</div>

<script src="{{ 'calculador-frete.js' | asset_url }}" defer></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
  CalculadorFrete.init({
    apiUrl: 'https://sua-api-frete.herokuapp.com',
    fromPostalCode: '01001000', // SEU CEP AQUI
    containerId: 'calculador-frete-{{ product.id }}',
    productData: {
      id: '{{ product.id }}',
      price: {{ product.price | divided_by: 100.0 }},
      weight: {% if product.metafields.custom.weight %}{{ product.metafields.custom.weight }}{% else %}0.5{% endif %},
      width: {% if product.metafields.custom.width %}{{ product.metafields.custom.width }}{% else %}15{% endif %},
      height: {% if product.metafields.custom.height %}{{ product.metafields.custom.height }}{% else %}10{% endif %},
      length: {% if product.metafields.custom.length %}{{ product.metafields.custom.length }}{% else %}20{% endif %},
      quantity: 1
    }
  });
});
</script>
```

---

## 🎉 Conclusão

Após seguir todos esses passos, você terá:

✅ **Calculador de frete funcionando** na página do produto  
✅ **Integração com API do Melhor Envio**  
✅ **Design responsivo** compatível com tema Warehouse  
✅ **Valores similares** aos da Cartpanda no checkout  

O calculador mostrará as opções de frete **antes** do cliente ir para o checkout da Cartpanda, melhorando a experiência de compra e reduzindo o abandono de carrinho.

---

## 📞 Suporte

Se precisar de ajuda:

1. **Verifique os logs** do backend da API
2. **Teste a API** diretamente com ferramentas como Postman
3. **Consulte a documentação** do Melhor Envio
4. **Entre em contato** com o suporte técnico

**Lembre-se:** Este calculador deve mostrar valores **similares** aos da Cartpanda, criando uma experiência consistente para o cliente.

