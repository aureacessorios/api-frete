/**
 * Calculador de Frete para Shopify
 * Integração com API do Melhor Envio
 * 
 * Para usar, inclua este script na sua página de produto e chame:
 * CalculadorFrete.init({
 *   apiUrl: 'https://sua-api.com',
 *   fromPostalCode: '01001000',
 *   containerId: 'calculador-frete'
 * });
 */

class CalculadorFrete {
    constructor(config) {
        this.config = {
            apiUrl: config.apiUrl || 'http://localhost:5000',
            fromPostalCode: config.fromPostalCode || '01001000',
            containerId: config.containerId || 'calculador-frete',
            productData: config.productData || null,
            ...config
        };
        
        this.container = null;
        this.isLoading = false;
        this.lastResults = null;
    }
    
    static init(config) {
        const calculator = new CalculadorFrete(config);
        calculator.render();
        return calculator;
    }
    
    render() {
        this.container = document.getElementById(this.config.containerId);
        if (!this.container) {
            console.error(`Container ${this.config.containerId} não encontrado`);
            return;
        }
        
        this.container.innerHTML = this.getHTML();
        this.attachEvents();
    }
    
    getHTML() {
        return `
            <div class="calculador-frete">
                <div class="calculador-frete__header">
                    <h3 class="calculador-frete__title">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M1 3h15l-1 6h-13l-1-6z"/>
                            <path d="M16 8v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8"/>
                            <circle cx="7" cy="21" r="1"/>
                            <circle cx="17" cy="21" r="1"/>
                        </svg>
                        Calcular Frete
                    </h3>
                    <p class="calculador-frete__subtitle">Consulte o valor e prazo de entrega</p>
                </div>
                
                <div class="calculador-frete__form">
                    <div class="calculador-frete__input-group">
                        <label for="cep-destino" class="calculador-frete__label">CEP de destino:</label>
                        <div class="calculador-frete__input-wrapper">
                            <input 
                                type="text" 
                                id="cep-destino" 
                                class="calculador-frete__input"
                                placeholder="00000-000"
                                maxlength="9"
                            />
                            <button 
                                type="button" 
                                class="calculador-frete__button"
                                onclick="this.closest('.calculador-frete').calculator.calculate()"
                            >
                                Calcular
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="calculador-frete__results" id="frete-results" style="display: none;">
                    <!-- Resultados serão inseridos aqui -->
                </div>
                
                <div class="calculador-frete__loading" id="frete-loading" style="display: none;">
                    <div class="calculador-frete__spinner"></div>
                    <span>Calculando frete...</span>
                </div>
                
                <div class="calculador-frete__error" id="frete-error" style="display: none;">
                    <!-- Erros serão exibidos aqui -->
                </div>
            </div>
        `;
    }
    
    attachEvents() {
        // Referência para o calculador no DOM
        this.container.calculator = this;
        
        // Máscara para CEP
        const cepInput = this.container.querySelector('#cep-destino');
        cepInput.addEventListener('input', this.formatCEP.bind(this));
        cepInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.calculate();
            }
        });
        
        // Auto-calcular se CEP for colado
        cepInput.addEventListener('paste', () => {
            setTimeout(() => {
                if (this.isValidCEP(cepInput.value)) {
                    this.calculate();
                }
            }, 100);
        });
    }
    
    formatCEP(event) {
        let value = event.target.value.replace(/\D/g, '');
        if (value.length > 5) {
            value = value.replace(/^(\d{5})(\d)/, '$1-$2');
        }
        event.target.value = value;
    }
    
    isValidCEP(cep) {
        const cleanCEP = cep.replace(/\D/g, '');
        return cleanCEP.length === 8;
    }
    
    async calculate() {
        const cepInput = this.container.querySelector('#cep-destino');
        const cep = cepInput.value.replace(/\D/g, '');
        
        if (!this.isValidCEP(cep)) {
            this.showError('Por favor, insira um CEP válido');
            return;
        }
        
        this.showLoading(true);
        this.hideError();
        this.hideResults();
        
        try {
            const productData = this.getProductData();
            const response = await this.callAPI(cep, productData);
            
            if (response.success) {
                this.showResults(response);
                this.lastResults = response;
            } else {
                this.showError(response.error || 'Erro ao calcular frete');
            }
        } catch (error) {
            console.error('Erro ao calcular frete:', error);
            this.showError('Erro de conexão. Tente novamente.');
        } finally {
            this.showLoading(false);
        }
    }
    
    getProductData() {
        // Tentar obter dados do produto do Shopify
        if (this.config.productData) {
            return this.config.productData;
        }
        
        // Tentar extrair dados da página do Shopify
        const productData = {
            id: 'default',
            price: 0,
            weight: 0.3, // peso padrão em kg
            width: 10,   // dimensões padrão em cm
            height: 5,
            length: 15,
            quantity: 1
        };
        
        // Tentar obter preço do produto
        const priceElement = document.querySelector('.price, .product-price, [data-price]');
        if (priceElement) {
            const priceText = priceElement.textContent || priceElement.getAttribute('data-price') || '0';
            const price = parseFloat(priceText.replace(/[^\d,]/g, '').replace(',', '.'));
            if (!isNaN(price)) {
                productData.price = price;
            }
        }
        
        // Tentar obter peso do produto (se disponível em metafields)
        const weightElement = document.querySelector('[data-weight]');
        if (weightElement) {
            const weight = parseFloat(weightElement.getAttribute('data-weight'));
            if (!isNaN(weight)) {
                productData.weight = weight > 50 ? weight / 1000 : weight; // converter gramas para kg
            }
        }
        
        // Tentar obter dimensões (se disponíveis)
        ['width', 'height', 'length'].forEach(dimension => {
            const element = document.querySelector(`[data-${dimension}]`);
            if (element) {
                const value = parseFloat(element.getAttribute(`data-${dimension}`));
                if (!isNaN(value)) {
                    productData[dimension] = value;
                }
            }
        });
        
        return productData;
    }
    
    async callAPI(cep, productData) {
        const payload = {
            from_postal_code: this.config.fromPostalCode,
            to_postal_code: cep,
            shopify_product: productData
        };
        
        const response = await fetch(`${this.config.apiUrl}/api/shipping/calculate-shopify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        return await response.json();
    }
    
    showResults(data) {
        const resultsContainer = this.container.querySelector('#frete-results');
        const options = data.shipping_options || [];
        
        if (options.length === 0) {
            this.showError('Nenhuma opção de frete disponível para este CEP');
            return;
        }
        
        let html = '<div class="calculador-frete__options">';
        
        options.forEach((option, index) => {
            const isRecommended = index === 0; // Primeira opção (mais barata)
            
            html += `
                <div class="calculador-frete__option ${isRecommended ? 'calculador-frete__option--recommended' : ''}">
                    <div class="calculador-frete__option-header">
                        <div class="calculador-frete__option-company">
                            ${option.company_logo ? `<img src="${option.company_logo}" alt="${option.company}" class="calculador-frete__company-logo">` : ''}
                            <span class="calculador-frete__company-name">${option.company}</span>
                        </div>
                        ${isRecommended ? '<span class="calculador-frete__badge">Mais barato</span>' : ''}
                    </div>
                    
                    <div class="calculador-frete__option-details">
                        <div class="calculador-frete__option-service">${option.name}</div>
                        <div class="calculador-frete__option-info">
                            <div class="calculador-frete__price">${option.formatted_price}</div>
                            <div class="calculador-frete__delivery">${option.formatted_delivery}</div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        
        // Adicionar informações adicionais
        if (data.cheapest && data.fastest && data.cheapest.id !== data.fastest.id) {
            html += `
                <div class="calculador-frete__summary">
                    <div class="calculador-frete__summary-item">
                        <strong>Mais barato:</strong> ${data.cheapest.formatted_price} em ${data.cheapest.formatted_delivery}
                    </div>
                    <div class="calculador-frete__summary-item">
                        <strong>Mais rápido:</strong> ${data.fastest.formatted_price} em ${data.fastest.formatted_delivery}
                    </div>
                </div>
            `;
        }
        
        resultsContainer.innerHTML = html;
        resultsContainer.style.display = 'block';
    }
    
    showLoading(show) {
        const loadingElement = this.container.querySelector('#frete-loading');
        loadingElement.style.display = show ? 'flex' : 'none';
        this.isLoading = show;
    }
    
    showError(message) {
        const errorElement = this.container.querySelector('#frete-error');
        errorElement.innerHTML = `
            <div class="calculador-frete__error-content">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="15" y1="9" x2="9" y2="15"/>
                    <line x1="9" y1="9" x2="15" y2="15"/>
                </svg>
                <span>${message}</span>
            </div>
        `;
        errorElement.style.display = 'block';
    }
    
    hideError() {
        const errorElement = this.container.querySelector('#frete-error');
        errorElement.style.display = 'none';
    }
    
    hideResults() {
        const resultsElement = this.container.querySelector('#frete-results');
        resultsElement.style.display = 'none';
    }
    
    // Método público para recalcular com novos dados
    recalculate(newProductData) {
        if (newProductData) {
            this.config.productData = newProductData;
        }
        
        const cepInput = this.container.querySelector('#cep-destino');
        if (cepInput.value && this.isValidCEP(cepInput.value)) {
            this.calculate();
        }
    }
}

// Disponibilizar globalmente
window.CalculadorFrete = CalculadorFrete;

